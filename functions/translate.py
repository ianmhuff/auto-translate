import os
import re
import csv
import configparser

from functions import helper

# Global variable to store the ParamLabels dictionary
param_labels_dict = None

# Use regex & text replacement to make scripts more readable
def translate_script(file_path, config):
    # Get content from file
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Get script type (fighter, weapon)
    script_type = deduce_script_type(content)
    
    # Format function name
    content, new_function_name = format_function_name(content, script_type)

    # Basic text replacements
    plaintext_replacements = [
        ('  ', '    '), # Changes indentation
        ('__', '::'), 
        ('LAB_', '// LAB_'), # Formats gotos
        ('goto //', '// goto'), 
        ('->moduleAccessor', '.module_accessor'), 
        ('->globalTable', '.global_table'), 
        ('->luaStateAgent', '.lua_state_agent'),
        ('&LStack', 'LStack'),
        ('&local_', 'local_'),
        ('return;', 'return return_value.into();'),
    ]
    content = helper.replace_plaintext(content, plaintext_replacements)
    plaintext_removals = [
        '(L2CValue *)&',
        '(L2CValue *)',
        'app::lua_bind::',
        'app::',
        '_impl',
        '(float)',
        '(float *)',
        '(int)',
        '(long)',
        '(ulong)',
        '(Vector2f *)',
        '(Vector3f *)',
        '(L2CAgent *)',
        '(L2CValue)', # todo combine
        '(BattleObjectModuleAccessor *)',
    ]
    content = helper.remove_plaintext(content, plaintext_removals)
    regex_replacements = [
        # Format function definitions to one line
        # Step 1: Line breaks and spaces
        (
            r'(\w+::\w+)\s*\(([\s\S]*?)\)\s*;', 
            lambda m: "{}({});".format(m.group(1), ','.join(arg.strip() for arg in re.split(r',\s*', m.group(2))))
        ),
        # Step 2: Pipes
        (
            r'(\w+::\w+)\s*\(([\s\S]*?)\)\s*;', 
            lambda m: "{}({});".format(m.group(1), re.sub(r'\s*\|\s*', ' | ', m.group(2)))
        ),
        # Replace "this" with either "fighter" or "weapon"
        (r'this(?=[.,)])', script_type),
        # lib::L2CValue::operator[op](var1,var2,var3) -> var3 = var1 [op] var2
        (r"lib::L2CValue::operator(.*)\((.+?),(.+?),(.+?)\)", r"\4 = \2 \1 \3"),
        # lib::L2CValue::operator=(var1,var2) -> var1 = var2
        (r"lib::L2CValue::operator=\((.+?),(.+?)\)", r"\1 = \2"),
        # lib::L2CValue::operator[](var1,var2) -> var1[var2]
        (r"(.+?)lib::L2CValue::operator\[\]\((.+?),(.+?)\)", r"\1\2[\3]"),
        # lib::L2CValue::operator[op](var1,var2) -> var1 [op] var2
        (r"(.+?)lib::L2CValue::operator(.*)\((.+?),(.+?)\)", r"\1\3 \2 \4"),
        # if ((var1 & 1) != 0) -> if var1
        (r"if \(\((.+?) & 1\) != 0\)(.*)", r"if \1\2"),
        # if ((var1 & 1) == 0) -> if !var1
        (r"if \(\((.+?) & 1\) == 0\)(.*)", r"if !\1\2"),
        # if ((var1 & 1U) != 0) -> if var1
        (r"if \(\((.+?) & 1U\) != 0\)(.*)", r"if \1\2"),
        # if ((var1 & 1U) == 0) -> if !var1 
        (r"if \(\((.+?) & 1U\) == 0\)(.*)", r"if !\1\2"),
        # lib::L2CValue::as_[data_type](var1) -> var1
        (r"(.*)lib::L2CValue::as_\w+\((.+?)\)(.*)", r"\1\2\3"),
        # (bool)(var1 & 1) -> var1
        (r"(.*)\(bool\)\((.+?) & 1\)(.*)", r"\1\2\3"),
        # lib::L2CValue::L2CValue(var1,var2) -> var1 = var2
        (r"lib::L2CValue::L2CValue\((.+?),(.+?)\)", r"\1 = \2"),
        # lib::L2CValue::operator.cast.to.bool(aLStackXX) -> aLStackXX
        (r"lib::L2CValue::operator.cast.to.bool\((.*)\)", r"\1"),
        # Format else statements
        (r'\}\s*\n\s*else\s*\n*', '} else '),
        # sub_shift_status_main, fastshift
        (
            r"lua2cpp::L2CFighter(?:Common|Base)::(sub_shift_status_main|fastshift)\((.+?),\s*0x([0-9a-fA-F]+),\s*(\w+)\)", 
            r"\2.\1(L2CValue::Ptr(0x\3 as *const () as _))"
        ),
        # change_status
        (r"lua2cpp::L2CFighterBase::change_status\((.+?),\s*(0x[0-9a-fA-F]+),\s*(0x[0-9a-fA-F]+)\)", r"\1.change_status(\2.into(), \3.into())"),
        # generic L2CFighterCommon function catch-all (this)
        (r"lua2cpp::L2CFighterCommon::(.+?)\(([^,]+)\)", r"\2.\1().get_bool()"),
        # generic L2CFighterCommon function catch-all (this + assignment)
        (r"lua2cpp::L2CFighterCommon::(.+?)\(([^,]+),\s*(\w*Stack\w*)\)", r"\3 = \2.\1().get_bool()"),
        # generic L2CFighterCommon function catch-all (this + args + assignment)
        (r"lua2cpp::L2CFighterCommon::(.+?)\(([^,]+),\s*(.+?),\s*(\w*Stack\w*)\)", r"\4 = \2.\1(\3).get_bool()"),
        # generic L2CFighterCommon function catch-all (this + args)
        (r"lua2cpp::L2CFighterCommon::(.+?)\(([^,]+),\s*(.+?)\)", r"\2.\1(\3).get_bool()"),
        # Reformat Vector3::create
        (r"lua2cpp::L2CFighterBase::Vector3::create\((.+?),\s*(0x[0-9a-fA-F]+),\s*(0x[0-9a-fA-F]+),\s*(0x[0-9a-fA-F]+),\s*(\w+)\)", r"\5 = Vector3f{ x: \2, y: \3, z: \4 }"),
        # L2CFighterBase::lerp
        (
            r"lua2cpp::L2CFighterBase::lerp\((.+?),\s*0x([0-9a-fA-F]+),\s*0x([0-9a-fA-F]+),\s*0x([0-9a-fA-F]+),\s*(\w+)\)", 
            r"\5 = \1.lerp(0x\2.into(), 0x\3.into(), 0x\4.into()).get_f32()"
        ),
        # clear_lua_stack
        (r"lib::L2CAgent::clear_lua_stack\((.+?)\)", r"\1.clear_lua_stack()"),
        # push_lua_stack
        (r"lib::L2CAgent::push_lua_stack\((.+?),\s*(\w+)\)", r"\1.push_lua_stack(&mut L2CValue::new_num(\2))"),
        # pop_lua_stack
        (r"lib::L2CAgent::pop_lua_stack\((.+?),\s*(\d+),\s*(\w+)\)", r"\3 = \1.pop_lua_stack(\2)"),
        # Remove underscore from before const names
        (r'([,|=])\s*_', r'\1 '),
        # add spaces after commas where there aren't already any
        (r",(?! +)", r", ")

    ]
    content = helper.replace_regex(content, regex_replacements)
    plaintext_removals2 = [
        '(bool)',
    ]
    content = helper.remove_plaintext(content, plaintext_removals2)
    regex_removals = [
        r",\s*return_value_\d+" # Removes return_value_XX
    ]
    content = helper.remove_regex(content, regex_removals)

    # Reformat main_loop function names in sub_shift_status_main & fastshift
    if new_function_name is not None and "main" in new_function_name:
        sub_shift_regex = [(r" = .+?;(\s*)(.+?)(sub_shift_status_main|fastshift)", r" = " + new_function_name + r"_loop;\1\2\3")]
        content = helper.replace_regex(content, sub_shift_regex)

    # Replace hashes
    content = replace_hashes(content)

    # Handle tilde lines
    if helper.getsafe(config, 'Translation', 'keep_tilde_lines'):
        # reformat lib::L2CValue::~L2CValue(var1) to //free(var1)
        tilde_regex = [(r"lib::L2CValue::~L2CValue\((.+?)\)", r"// free(\1)")]
        content = helper.replace_regex(content, tilde_regex)
    else: 
        content = remove_tilde_lines(content)
    
    # Handle var declarations
    if not helper.getsafe(config, 'Translation', 'keep_var_declarations'):
        content = remove_var_declarations(content)
    
    # Generate new file name
    file_dir, original_file_name = os.path.split(file_path)
    file_name, file_extension = os.path.splitext(original_file_name)

    # File name
    output_file_name = helper.getsafe(config, 'FileHandling', 'output_file_name')
    if output_file_name == "rename" and new_function_name is not None:
        file_name = new_function_name
    # File type
    output_file_type = helper.getsafe(config, 'FileHandling', 'output_file_type')
    if file_extension.lower() != output_file_type:
        new_file_path = os.path.join(file_dir, file_name + output_file_type)
    else:
        new_file_path = file_path
    
    # Write back to file
    with open(new_file_path, 'w', encoding='utf-8') as file:
        file.write(content)

    return new_file_path

# Rets either "fighter", "weapon", "fun", or "unknown"
def deduce_script_type(content):
    if "void FUN" in content: # FUN functs must be first, as FUN_ functs can contain "L2CFighterBase"
        return "fun"
    elif "L2CWeapon" in content: # Weapon should be before fighter; weapons sometimes have "L2CFighter" in their scripts, but fighters shouldn't have "L2CWeapon" afaik
        return "weapon"
    elif "L2CFighter" in content:
        return "fighter"
    return "unknown"

# Formats function name. Takes file content and script type as args
def format_function_name(content, script_type):
    if script_type != "fun":
        # Normal script
        pattern = r'void.*?thiscall\s+(L2C(?:Fighter|Weapon)[^:]+)::status::([^\(]+)\s*\(([^)]*)\)\s*'
        plaintext_removals = ["L2CFighter", "L2CWeapon"]
        match = re.search(pattern, content, re.DOTALL)
        if match:
            name_full = match.group(1)
            name = helper.remove_plaintext(name_full, plaintext_removals)
            status_name = match.group(2).strip()
            function_name = f"{name.lower()}_{status_name.lower()}"

            if script_type == "fighter":
                param_type = "fighter: &mut L2CFighterCommon"
            elif script_type == "weapon":
                param_type = "weapon: &mut L2CWeaponCommon"
            else:
                param_type = ""

            formatted_function = f"unsafe extern \"C\" fn {function_name}({param_type}) -> L2CValue "
            content = re.sub(pattern, formatted_function, content)
    else:
        # Fun script
        pattern = r'void\s+FUN_[0-9a-fA-F]+\s*\(([^)]*)\)\s*'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            full_declaration = match.group(0)
            paren_index = full_declaration.find('(')
            function_name = full_declaration[:paren_index].strip().split()[-1]

            formatted_function = f"unsafe extern \"C\" fn {function_name}() -> L2CValue "
            content = re.sub(pattern, formatted_function, content)

    # Remove everything before function def & ret
    index = content.find("unsafe")
    if index != -1:
        return content[index:], function_name
    else:
        return content, None

def replace_hashes(content):
    hash_format = r"0x[0-9a-f]+"
    content = re.sub(hash_format, convert_hash, content)
    return content

# Converts hashes to strings
def convert_hash(match):
    hash_value = match.group(0)

    # If hash is shorter than a standard hash, do nothing
    if len(hash_value) < 9:
        return hash_value

    # Load ParamLabels if not already loaded
    if param_labels_dict is None:
        config = configparser.ConfigParser()
        config.read("autotranslate_settings.ini")
        param_labels_path = helper.getsafe(config, 'FileHandling', 'path_to_param_labels')
        load_param_labels(param_labels_path)

    # Find hash in dictionary
    hash_int = int(hash_value, 16)
    if hash_int in param_labels_dict:
        return f'Hash40::new("{param_labels_dict[hash_int]}")'
    else:
        return hash_value  # Do nothing if the hash is not found in ParamLabels.csv

# Removes all lines with a tilde
def remove_tilde_lines(content):
    lines = content.splitlines()
    lines_no_tilde = [line for line in lines if '~' not in line]
    return '\n'.join(lines_no_tilde)

# Load ParamLabels into a dictionary for easier searching
def load_param_labels(param_labels_path):
    global param_labels_dict
    param_labels_dict = {}
    
    with open(param_labels_path, newline='') as param_labels_file:
        reader = csv.reader(param_labels_file, delimiter=',', quotechar='|')
        for row in reader:
            param_labels_dict[int(row[0], 16)] = row[1]

# Removes section of variable declarations near the top of the file
def remove_var_declarations(content):
    var_dec_regex = [(r'\{\n\s*([\w\s\[\]\*;,.:]+)\n    \n', r'{\n')]
    return helper.replace_regex(content, var_dec_regex)
