# auto-translate.py
# v0.6

# ideas/todo:
# operator.cast.to.bool ?
# other as_[type]() functions (currently handling as_integer(), as_hash(), as_bool())
#     can these all be handled with one case?
# _SITUATION... -> *SITUATION... (also _FIGHTER..., _GROUND..., etc)
#     this seems difficult to do comprehensively without a complete list of cases where this happens
# returns? i.e. return_value = 0; -> return 0.into();
#     this one would need to be at the bottom since it depends on the formatting
# function headers?

# in lines such as this:
#             (this->moduleAccessor,(bool)(bVar1 & 1),iVar5,(bool)(bVar2 & 1),(bool)(bVar3 & 1),
# the code that changes (bool)(var & 1) to var only runs once

import os
import re

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
    
    # 
    content = replace_plaintext(content)
    content = replace_regex(content)
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

# For basic text replacement that can typically be done with a ctrl+f (no regex)
def replace_plaintext(content):
    replacements = [
        ('(L2CValue *)&', ''),
        ('(L2CValue *)', ''),
        ('app::lua_bind::', ''),
        ('_impl', ''),
        ('__', '::'),
        ('this->moduleAccessor', 'fighter.module_accessor'),
        ('this->globalTable', 'fighter.global_table')
    ]

    for old, new in replacements:
        content = content.replace(old, new)

    return content

# For slightly more difficult text replacement that requires regex
def replace_regex(content):
    replacements = [
        # Removes return_value_XX
        (r",return_value_\d+", ""),
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
        # reformat lib::L2CValue::~L2CValue(var1);
        # to //free(var1);
        (r"lib::L2CValue::~L2CValue\((.+?)\)", r"// free(\1)")
    ]

    for old, new in replacements:
        content = re.sub(old, new, content)

    return content

if __name__ == "__main__":
    main()
