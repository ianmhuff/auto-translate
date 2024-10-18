import os
import sys
import re
import csv
import configparser
import urllib.request

def main():
    current_directory = os.getcwd()

    # Get autotranslate_settings.ini and create if it doesn't already exist
    ini_filename = "autotranslate_settings.ini"
    if not os.path.exists(ini_filename):
        create_ini(ini_filename)
    config = configparser.ConfigParser()
    config.read(ini_filename)

    # Create ParamLabels.csv if doesn't already exist
    param_labels_path = config.get('FileHandling', 'path_to_param_labels')
    if not os.path.isfile(param_labels_path):
        create_paramlabels(param_labels_path)

    # Get valid file extensions
    file_types = config.get('FileHandling', 'search_file_types')
    valid_extensions = [file_type.strip() for file_type in file_types.split(',')]

    # Determine how the script was executed
    if len(sys.argv) < 2:
        # SCRIPT CLICKED / RAN IN CONSOLE
        output_file_type = config.get('FileHandling', 'output_file_type')
        input(f"===WARNING===\nTHIS SCRIPT WILL READ ALL {valid_extensions} FILES IN THE CURRENT DIRECTORY AND OUTPUT AS [{output_file_type}]\nIf you wish to proceed, press Enter. Otherwise Ctrl+C to exit\n> ")
        for filename in os.listdir(current_directory):
            # Only modify files with specified extensions
            ext = os.path.splitext(filename)[1]
            if ext not in valid_extensions:
                continue

            # Run translate function on script
            file_path = os.path.join(current_directory, filename) # todo combine
            new_file_path = translate_script(file_path, config)
            print(f"Processed file: {file_path} -> {new_file_path}")
            if config.has_section('Development') and config.has_option('Development', 'condense_script'):
                if config.getboolean('Development', 'condense_script'):
                    print('===WARNING===\nCondense script feature is currently in development and will be buggy')
                    condense_script(new_file_path)
                    print(f"CONDENSED: {new_file_path}")
    else:
        # FILES DRAGGED ONTO SCRIPT
        for file_path in sys.argv[1:]:
            new_file_path = translate_script(file_path, config)
            print(f"Processed file: {file_path} -> {new_file_path}")
            if config.has_section('Development') and config.has_option('Development', 'condense_script'):
                if config.getboolean('Development', 'condense_script'):
                    print('===WARNING=== Condense script feature is currently in development and will be buggy')
                    condense_script(new_file_path)
                    print(f"Condensed file: {new_file_path}")

    input("\nPress Enter to exit...")

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
    content = replace_plaintext(content, plaintext_replacements)
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
    content = remove_plaintext(content, plaintext_removals)
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
        # reformat main_loop function names in sub_shift_status_main
        (r" = .+?;(\s*)fighter.sub_shift_status_main", r" = " + new_function_name + r"_loop;\1fighter.sub_shift_status_main"),
        # add spaces after commas where there aren't already any
        (r",(?! +)", r", ")

    ]
    content = replace_regex(content, regex_replacements)
    plaintext_removals2 = [
        '(bool)',
    ]
    content = remove_plaintext(content, plaintext_removals2)
    regex_removals = [
        r",\s*return_value_\d+" # Removes return_value_XX
    ]
    content = remove_regex(content, regex_removals)

    # Replace hashes
    content = replace_hashes(content)

    # Handle tilde lines
    if config.getboolean('General', 'keep_tilde_lines'):
        # reformat lib::L2CValue::~L2CValue(var1) to //free(var1)
        tilde_regex = [(r"lib::L2CValue::~L2CValue\((.+?)\)", r"// free(\1)")]
        content = replace_regex(content, tilde_regex)
    else: 
        content = remove_tilde_lines(content)
    
    # Handle var declarations
    if not config.getboolean('General', 'keep_var_declarations'):
        content = remove_var_declarations(content)
    
    # Generate new file name
    file_name, file_extension = os.path.splitext(file_path)
    # File name
    output_file_name = config.get('FileHandling', 'output_file_name')
    if output_file_name == "rename" and new_function_name is not None:
        file_name = new_function_name
    # File type
    output_file_type = config.get('FileHandling', 'output_file_type')
    if file_extension.lower() != output_file_type:
        new_file_path = file_name + output_file_type
    else:
        new_file_path = file_path

    # Write back to file
    with open(new_file_path, 'w', encoding='utf-8') as file:
        file.write(content)

    return new_file_path

# Replace vars & move variables to shorten a script as much as possible
def condense_script(file_path):
    # Get content from file
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.readlines()

    # Patterns
    assignment_pattern = r'\s*(\w+)\s*=\s*([^;]+)\s*;' # Captures variable assignments
    hex_pattern = r'(?<!\[)(0x[0-9a-fA-F]{2})(?![0-9a-fA-F])(?!=\])' # Captures 2-digit hex vals
    in_stack_pattern = r'\bin_stack_\w+\b' # Captures in_stack vars

    # List to track var info 
    # 'name': name of the variable
    # 'value': what the variable is being set to
    # 'line': line this operation took place on
    # 'scope': current amount of indentation present
    # 'allowed': set to false if the variable's scope has expired
    # 'delete': whether to delete the line afterwards
    variables = []
    scope_level = 0

    # Split to lines
    for line_number, line in enumerate(content, start=1):
        # Check for scope changes
        if "{" in line:
            scope_level += 1
        if "}" in line:
            # Disallow variables once their scope expires
            for var in variables:
                if var['scope'] == scope_level:
                    var['allowed'] = False
            scope_level -= 1

        # Check if any variables in the list are in the current line
        for var in variables:
            if var['name'] in line and not line.lstrip().startswith(var['name']) and var['allowed']:
                highest_line_var = max(
                    (v for v in variables if v['name'] == var['name'] and v['allowed']),
                    key=lambda x: x['line']
                )
                replacement_value = highest_line_var['value']
                
                # If var is being inverted and replacement_value contains ==, flip the replacement_value to !=
                if f"!{var['name']}" in line:
                    if "==" in replacement_value:
                        replacement_value = replacement_value.replace("==", "!=")
                    elif "!=" in replacement_value:
                        replacement_value = replacement_value.replace("!=", "==")
                    line = line.replace(f"!{var['name']}", var['name'])
                else:
                    # Add asterisk if value is a const
                    if re.fullmatch(r'[A-Z_*]+', replacement_value):
                        # Remove asterisk if const is put into a var with .into() after it 
                        replacement_value = replacement_value.lstrip('*')
                        if f"{var['name']}.into()" not in line:
                            replacement_value = f"*{replacement_value}"
                
                # Replace var in line
                line = line.replace(var['name'], replacement_value)
                # Update file content
                content[line_number - 1] = line

        # Check for 2-digit hex values & in_stack vars and replace with last updated variable
        hex_values = re.findall(hex_pattern, line)
        in_stack_vars = re.findall(in_stack_pattern, line)
        hex_and_in_stack = hex_values + in_stack_vars
        if hex_and_in_stack:
            sorted_vars = sorted(
                (v for v in variables if v['allowed']),
                key=lambda x: x['line'],
                reverse=True
            )
            # Replace hex value with the highest available variable values
            for index, value in enumerate(hex_and_in_stack):
                if index < len(sorted_vars):
                    replacement_value = sorted_vars[index]['value']
                    line = line.replace(value, replacement_value, 1)
                    content[line_number - 1] = line

        # If line is just a variable, update its value (sometimes happens in pre scripts)
        var_declaration_pattern = r'^\s*(\w+);\s*$'
        declaration_match = re.match(var_declaration_pattern, line)
        if declaration_match:
            variable_name = declaration_match.group(1).strip()
            highest_line_var = max(
                (v for v in variables if v['name'] == variable_name and v['allowed']),
                key=lambda x: x['line'],
                default=None
            )
            if highest_line_var:
                variables.append({
                    "name": variable_name,
                    "value": highest_line_var['value'],
                    "line": line_number,
                    "scope": scope_level,
                    "allowed": True,
                    "delete": True
                })

        # Find variable assignments
        match = re.match(assignment_pattern, line)
        if match:
            variable_name = match.group(1).strip()
            assigned_value = match.group(2).strip()

            # Add "let" before var if going to be kept
            delete = True
            if 'Module::' in assigned_value:
                content[line_number - 1] = re.sub(r'(^\s*)(\S)', r'\1let \2', line)
                delete = False
            else:
                # Check if assigned value is a known variable
                for var in variables:
                    if var['name'] == assigned_value and var['scope'] <= scope_level and var['allowed']:
                        assigned_value = var['value']
                        content[line_number - 1] = re.sub(
                            r'=\s*' + re.escape(var['name']) + r'\s*;',
                            f'= {assigned_value};',
                            line
                        )
                        break

            # Add var to array
            new_var_info = {
                "name": variable_name,
                "value": variable_name if 'Module::' in assigned_value else assigned_value,
                "line": line_number,
                "scope": scope_level,
                "allowed": True, 
                "delete": delete 
            }
            print(new_var_info)
            variables.append(new_var_info)

    # Remove == true, != false, and all combinations
    for line_number, line in enumerate(content):
        if " == false" in line or " != true" in line:
            if "if !" in line:
                line = line.replace("if !", "if ")
            elif "if " in line:
                line = line.replace("if ", "if !")
        line = re.sub(r'\s*(==|!=)\s*(true|false)', '', line)
        content[line_number] = line

    # Delete lines with delete param true
    lines_to_delete = {var['line'] for var in variables if var['delete']}
    content = [line for i, line in enumerate(content, start=1) if i not in lines_to_delete]

    # Remove return value lines with no actual ret val 
    content = [line for line in content if line.strip() != "return return_value.into();"]

    # Remove " -> L2CValue" from FUN functs with no return in them
    if content and "FUN_71" in content[0]:
        # Check for "return" in the entire content
        if not any("return" in line for line in content):
            # Remove " -> L2CValue" from the first line
            content[0] = content[0].replace(" -> L2CValue", "")
    
    # If last line is a sub_shift_status_main or fastshift, remove semicolon for implied return
    for i in range(len(content) - 1, -1, -1):
        line = content[i]
        if line and '}' not in line:
            if "sub_shift_status_main" in line or "fastshift" in line:
                content[i] = line.replace(';', '')
            break

    # Write the modified content back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(content)

# Create autotranslate_settings.ini
def create_ini(ini_filename):
    print(f"{ini_filename} not found, creating...")
    config = configparser.ConfigParser()

    config['General'] = {
        'keep_tilde_lines': 'false',
        'keep_var_declarations': 'false'
    }
    config['FileHandling'] = {
        'search_file_types': '.txt, .c',
        'output_file_type': '.rs',
        'output_file_name': 'rename',
        'path_to_param_labels': './ParamLabels.csv'
    }

    with open(ini_filename, 'w') as configfile:
        config.write(configfile)
    
    print(f"{ini_filename} created.")

def create_paramlabels(param_labels_path):
    print(f"{param_labels_path} not found. Downloading ParamLabels.csv...")
    paramlabels_url = "https://raw.githubusercontent.com/ultimate-research/param-labels/refs/heads/master/ParamLabels.csv"
    try:
        urllib.request.urlretrieve(paramlabels_url, param_labels_path)
        print(f"Downloaded ParamLabels.csv to {param_labels_path}.")
    except Exception as e:
        print(f"Failed to download ParamLabels.csv: {e}")

# Rets either "fighter", "weapon", "fun", or "unknown"
def deduce_script_type(content):
    if "L2CWeapon" in content: # Weapon should be first; weapons sometimes have "L2CFighter" in their scripts, but fighters shouldn't have "L2CWeapon" afaik
        return "weapon"
    elif "L2CFighter" in content:
        return "fighter"
    elif "void FUN" in content:
        return "fun"
    return "unknown"

# For basic text replacement that can typically be done with a ctrl+f (no regex)
def replace_plaintext(content, replacements):
    for old, new in replacements:
        content = content.replace(old, new)
    return content

# For basic text removal that can typically be done with a ctrl+f (no regex)
def remove_plaintext(content, removals):
    for removal in removals:
        content = content.replace(removal, '')
    return content

# For slightly more difficult text replacement that requires regex
def replace_regex(content, replacements):
    for old, new in replacements:
        content = re.sub(old, new, content)
    return content

# For slightly more difficult text removal that requires regex
def remove_regex(content, removals):
    for removal in removals:
        content = re.sub(removal, '', content)
    return content

def replace_hashes(content):
    hash_format = r"0x[0-9a-f]+"
    content = re.sub(hash_format, convert_hash, content)
    return content

# Convert hash with ParamLabels.csv
def convert_hash(match):
    hash_value = match.group(0)

    # If hash is shorter than a standard hash, do nothing for now
    if len(hash_value) < 9:
        return hash_value

    # Get ParamLabels path
    config = configparser.ConfigParser()
    config.read("autotranslate_settings.ini")
    param_labels_path = config.get('FileHandling', 'path_to_param_labels')
    # Find hash in ParamLabels
    with open(param_labels_path, newline='') as param_labels_file:
        reader = csv.reader(param_labels_file, delimiter=',', quotechar='|')
        for row in reader:
            if int(row[0], 16) == int(hash_value, 16):
                return "Hash40::new(\"" + row[1] + "\")"
        return hash_value # do nothing if the hash is not found in ParamLabels.csv

# Formats function name. Takes file content and script type as args
def format_function_name(content, script_type):
    if script_type != "fun":
        # Normal script
        pattern = r'void.*?thiscall\s+(L2C(?:Fighter|Weapon)[^:]+)::status::([^\(]+)\s*\(([^)]*)\)\s*'
        plaintext_removals = ["L2CFighter", "L2CWeapon"]
        match = re.search(pattern, content, re.DOTALL)
        if match:
            name_full = match.group(1)
            name = remove_plaintext(name_full, plaintext_removals)
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

# Removes all lines with a tilde
def remove_tilde_lines(content):
    lines = content.splitlines()
    lines_no_tilde = [line for line in lines if '~' not in line]
    return '\n'.join(lines_no_tilde)

# Removes section of variable declarations near the top of the file
def remove_var_declarations(content):
    var_dec_regex = [(r'\{\n\s*([\w\s\[\]\*;,.:]+)\n    \n', r'{\n')]
    return replace_regex(content, var_dec_regex)

if __name__ == "__main__":
    main()
