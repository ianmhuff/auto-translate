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
        input(f"===WARNING===\nTHIS SCRIPT WILL EDIT ANY {valid_extensions} FILES IN THE CURRENT DIRECTORY AND OUTPUT AS [{output_file_type}]\nIf you wish to proceed, press Enter. Otherwise Ctrl+C to exit\n> ")
        for filename in os.listdir(current_directory):
            # Only modify files with specified extensions
            ext = os.path.splitext(filename)[1]
            if ext not in valid_extensions:
                continue

            # Run translate function on script
            file_path = os.path.join(current_directory, filename)
            translate_script(file_path, config)
    else:
        # FILES DRAGGED ONTO SCRIPT
        for file_path in sys.argv[1:]:
            new_file_path = translate_script(file_path, config)
            print(f"Processed file: {new_file_path}")

    input("\nPress Enter to exit...")

def translate_script(file_path, config):
    # Get content from file
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Get script type (fighter, weapon)
    script_type = deduce_script_type(content)
    
    # Format function name
    content = format_function_name(content, script_type)

    # Basic text replacements
    plaintext_replacements = [
        ('  ', '    '), # Changes indentation
        ('__', '::'), 
        ('LAB_', '// LAB_'), # Formats gotos
        ('goto //', '// goto'), 
        ('->moduleAccessor', '.module_accessor'), 
        ('->globalTable', '.global_table'), 
        ('->luaStateAgent', '.lua_state_agent'),
        (',_', ','), # Doesn't cover every occurrence, todo
    ]
    content = replace_plaintext(content, plaintext_replacements)
    plaintext_removals = [
        '(L2CValue *)&',
        '(L2CValue *)',
        'app::lua_bind::',
        '_impl',
        '(float)',
        '(int)',
        '(long)',
        '(ulong)',
        '(Vector2f *)',
        '(Vector3f *)',
        '(L2CAgent *)',
        '(L2CValue)', # todo combine
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
        # reformat (bool)(var1 & 1)
        # to var1
        (r"(.*)\(bool\)\((.+?) & 1\)(.*)", r"\1\2\3"),
        # reformat lib::L2CValue::L2CValue(var1,var2)
        # to var1 = var2
        (r"lib::L2CValue::L2CValue\((.+?),(.+?)\)", r"\1 = \2"),
        # Reformat lib::L2CValue::operator.cast.to.bool(aLStackXX)
        # to aLStackXX
        (r"lib::L2CValue::operator.cast.to.bool\((.*)\)", r"\1"),
        # Format else statements
        (r'\}\s*\n\s*else\s*\n*', '} else '),
        # Format function definitions to one line, doesn't work if it's 3+ lines)
        (r'(\w+::\w+)\s*\((.*?)\)\s*;', r'\1(\2);'),
    ]
    content = replace_regex(content, regex_replacements)
    plaintext_removals2 = [
        '(bool)'
    ]
    content = remove_plaintext(content, plaintext_removals2)
    regex_removals = [
        r",return_value_\d+" # Removes return_value_XX
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
    
    # Change file path to type specified in .ini file
    output_file_type = config.get('FileHandling', 'output_file_type')
    file_name, file_extension = os.path.splitext(file_path)
    if file_extension.lower() != output_file_type:
        new_file_path = file_name + output_file_type
    else:
        new_file_path = file_path

    # Write back to file
    with open(new_file_path, 'w', encoding='utf-8') as file:
        file.write(content)

    return new_file_path

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
