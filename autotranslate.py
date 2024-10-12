import os
import re
import csv

def main():
    current_directory = os.getcwd()
    valid_extensions = [".txt", ".c", ".rs"]
    for filename in os.listdir(current_directory):
        # don't modify the script file lmao
        if filename == os.path.basename(__file__):
            continue

        # only modify files of certain types
        ext = os.path.splitext(filename)[1]
        if ext not in valid_extensions:
            continue

        # Run translate funct on script
        file_path = os.path.join(current_directory, filename)
        translate_script(file_path)

    input("\nPress Enter to exit...")

def translate_script(file_path):
    # Get content from file
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Get script type (fighter, weapon)
    script_type = deduce_script_type(content)
    
    content = format_function_name(content, script_type)

    plaintext_replacements = [
        ('  ', '    '), # Changes indentation
        ('__', '::'), 
        ('LAB_', '// LAB_'), # Formats gotos
        ('goto //', '// goto'), 
        ('->moduleAccessor', '.module_accessor'), 
        ('->globalTable', '.global_table'), 
        ('->luaStateAgent', '.lua_state_agent'),
        (',_', ',') # Doesn't cover every occurrence, todo
    ]
    content = replace_plaintext(content, plaintext_replacements)
    plaintext_removals = [
        '(L2CValue *)&',
        '(L2CValue *)',
        'app::lua_bind::',
        '_impl',
        '(float)',
        '(int)',
        '(bool)',
        '(long)',
    ]
    content = remove_plaintext(content, plaintext_removals)
    regex_replacements = [
        # Replace "this" with either "fighter" or "weapon"
        (r'this(?=[.,)])', script_type),
        # reformat lib::L2CValue::operator[op](var1,var2,var3)
        # to var3 = var1 [op] var2
        (r"lib::L2CValue::operator(.*)\((.+?),(.+?),(.+?)\)", r"\4 = \2 \1 \3"),
        # reformat lib::L2CValue::operator=(var1,var2)
        # to var1 = var2
        (r"lib::L2CValue::operator=\((.+?),(.+?)\)", r"\1 = \2"),
        # reformat lib::L2CValue::operator[](var1,var2)
        # to var1[var2]
        (r"(.+?)lib::L2CValue::operator\[\]\((.+?),(.+?)\)", r"\1\2[\3]"),
        # reformat lib::L2CValue::operator[op](var1,var2)
        # to var1 [op] var2
        (r"(.+?)lib::L2CValue::operator(.*)\((.+?),(.+?)\)", r"\1\3 \2 \4"),
        # reformat if ((var1 & 1) != 0)
        # to if var1
        (r"if \(\((.+?) & 1\) != 0\)(.*)", r"if \1\2"),
        # reformat if ((var1 & 1) == 0)
        # to if !var1
        (r"if \(\((.+?) & 1\) == 0\)(.*)", r"if !\1\2"),
        # reformat if ((var1 & 1U) != 0)
        # to if var1
        (r"if \(\((.+?) & 1U\) != 0\)(.*)", r"if \1\2"),
        # reformat if ((var1 & 1U) == 0)
        # to if !var1 
        (r"if \(\((.+?) & 1U\) == 0\)(.*)", r"if !\1\2"),
        # reformat lib::L2CValue::as_[data_type](var1)
        # to var1
        (r"(.*)lib::L2CValue::as_\w+\((.+?)\)(.*)", r"\1\2\3"),
        # reformat (var1 & 1)
        # to var1
        (r"(.*)\((.+?) & 1\)(.*)", r"\1\2\3"),
        # reformat lib::L2CValue::L2CValue(var1,var2)
        # to var1 = var2
        (r"lib::L2CValue::L2CValue\((.+?),(.+?)\)", r"\1 = \2"),
        # reformat lib::L2CValue::~L2CValue(var1)
        # to //free(var1)
        (r"lib::L2CValue::~L2CValue\((.+?)\)", r"// free(\1)"),
        # Format else statements
        (r'\}\s*\n\s*else\s*\n*', '} else '),
        # Format function definitions to one line (todo does not work if nested parentheses exist, probabaly fixes itself once we can replace "*(BattleObjectModuleAccessor **)(param_X + 0x40)", also doesn't work if it's three lines)
        (r'([^\n]*?)(\s*\(.*?\))', r'\1\2')
    ]
    content = replace_regex(content, regex_replacements)
    regex_removals = [
        r",return_value_\d+" # Removes return_value_XX
    ]
    content = remove_regex(content, regex_removals)
    content = replace_hash(content)

    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

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

def replace_hash(content):
    hash_format = r"0x[0-9a-f]+"
    content = re.sub(hash_format, convert_hash, content)
    return content

def convert_hash(match):

    hash_value = match.group(0)

    # if the hash value is smaller than the smallest value in ParamLabels.csv, do nothing for now
    if int(hash_value, 16) < 0x0101d41b76:
        return hash_value

    with open('ParamLabels.csv', newline='') as param_labels_file:
        reader = csv.reader(param_labels_file, delimiter=',', quotechar='|')
        for row in reader:
            if int(row[0], 16) == int(hash_value, 16):
                return "Hash40::new(\"" + row[1] + "\")"
        return hash_value # do nothing if the hash is not found in ParamLabels.csv

# Formats function name. Takes file content and script type as args
def format_function_name(content, script_type):
    if script_type != "fun":
        # normal script
        def format_normal(match):
            name_full = match.group(1)
            plaintext_removals = ["L2CFighter", "L2CWeapon"]
            name = remove_plaintext(name_full, plaintext_removals)
            status_name = match.group(2)
            
            function_name = f"{name.lower()}_{status_name.lower()}"
            
            if script_type == "fighter":
                param_type = "fighter: &mut L2CFighterCommon"
            elif script_type == "weapon":
                param_type = "weapon: &mut L2CWeaponCommon"
            else:
                param_type = ""
            
            return f"unsafe extern \"C\" fn {function_name}({param_type}) -> L2CValue "
        
        pattern = r'void.*?thiscall\s+(L2C(?:Fighter|Weapon)[^:]+)::status::([^\(]+)\s*\(([^)]*)\)\s*'

        content = re.sub(pattern, format_normal, content)
    else:
        # fun script
        def format_fun(match):
            full_declaration = match.group(0)
            paren_index = full_declaration.find('(')
            function_name = full_declaration[:paren_index].strip().split()[-1]
            return f"unsafe extern \"C\" fn {function_name}() -> L2CValue "
        
        pattern = r'void\s+FUN_[0-9a-fA-F]+\s*\(([^)]*)\)\s*'
        content = re.sub(pattern, format_fun, content)

    # Remove everything before function def & ret
    return content[content.find("unsafe"):]

if __name__ == "__main__":
    main()
