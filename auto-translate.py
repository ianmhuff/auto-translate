# auto-translate.py
# v0.5

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

def translate():
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
        
        file_path = os.path.join(current_directory, filename)

        if os.path.isfile(file_path):
            with open(file_path, 'r') as file:
                lines = file.readlines()
            
            modified_lines = []
            
            for line in lines:                
                
                
                # ======= removals =======
                
                # remove "(L2CValue *)&" from all lines
                pattern = "(L2CValue *)&"
                if pattern in line:
                    line = line.replace(pattern, "")
                
                
                # remove "(L2CValue *)" from all lines
                pattern = "(L2CValue *)"
                if pattern in line:
                    line = line.replace(pattern, "")
                
                
                # remove "app::lua_bind::" from all lines
                pattern = "app::lua_bind::"
                if pattern in line:
                    line = line.replace(pattern, "")
                
                
                # remove "_impl" from all lines
                pattern = "_impl"
                if pattern in line:
                    line = line.replace(pattern, "")
                
                
                # remove "return_value_xx" from all lines
                pattern = r",return_value_\d+"
                match = re.search(pattern, line)
                if match:
                    line = re.sub(pattern, "", line)
                
                
                
                
                # ======= replacements =======
                
                # replace __
                # with ::
                pattern = "__"
                if pattern in line and "thiscall" not in line:
                    line = line.replace(pattern, "::")
                
                
                # replace this->moduleAccessor
                # with fighter.module_accessor
                pattern = "this->moduleAccessor"
                if pattern in line:
                    line = line.replace(pattern, "fighter.module_accessor")
                
                
                # replace this->globalTable
                # with fighter.global_table
                pattern = "this->globalTable"
                if pattern in line:
                    line = line.replace(pattern, "fighter.global_table")
                
                
                
                
                # ======= operators =======
                
                # reformat lib::L2CValue::operator[op](var1,var2,var3);
                # to var3 = var1 [op] var2;
                pattern = r"(\s*)lib::L2CValue::operator(.*)\((.+?),(.+?),(.+?)\);\n"
                match = re.fullmatch(pattern, line)
                if match:
                    whitespace, op, token1, token2, token3 = match.groups()
                    line = f"{whitespace}{token3} = {token1} {op} {token2};\n"
                
                
                # reformat lib::L2CValue::operator=(var1,var2);
                # to var1 = var2;
                pattern = r"(\s*)lib::L2CValue::operator=\((.+?),(.+?)\);\n"
                match = re.fullmatch(pattern, line)
                if match:
                    whitespace, token1, token2 = match.groups()
                    line = f"{whitespace}{token1} = {token2};\n"
                
                
                # reformat lib::L2CValue::operator[](var1,var2)
                # to var1[var2]
                pattern = r"(\s*)(.+?)lib::L2CValue::operator\[\]\((.+?),(.+?)\);\n"
                match = re.search(pattern, line)
                if match:
                    whitespace, other, token1, token2 = match.groups()
                    line = f"{whitespace}{other}{token1}[{token2}];\n"
                
                
                # reformat lib::L2CValue::operator[op](var1,var2);
                # to var1 [op] var2;
                pattern = r"(\s*)(.+?)lib::L2CValue::operator(.*)\((.+?),(.+?)\);\n"
                match = re.search(pattern, line)
                if match:
                    whitespace, other, op, token1, token2 = match.groups()
                    line = f"{whitespace}{other}{token1} {op} {token2};\n"
                
                
                
                
                # ======= if statements =======
                
                # reformat if ((var1 & 1) != 0)
                # to if var1
                pattern = r"(\s*)if \(\((.+?) & 1\) != 0\)(.*)"
                match = re.search(pattern, line)
                if match:
                    whitespace, token1, other = match.groups()
                    line = f"{whitespace}if {token1}{other}\n"
                
                
                # reformat if ((var1 & 1) == 0)
                # to if !var1
                pattern = r"(\s*)if \(\((.+?) & 1\) == 0\)(.*)"
                match = re.search(pattern, line)
                if match:
                    whitespace, token1, other = match.groups()
                    line = f"{whitespace}if !{token1}{other}\n"
                
                
                # reformat if ((var1 & 1U) != 0)
                # to if var1
                pattern = r"(\s*)if \(\((.+?) & 1U\) != 0\)(.*)"
                match = re.search(pattern, line)
                if match:
                    whitespace, token1, other = match.groups()
                    line = f"{whitespace}if {token1}{other}\n"
                
                
                # reformat if ((var1 & 1U) == 0)
                # to if !var1
                pattern = r"(\s*)if \(\((.+?) & 1U\) == 0\)(.*)"
                match = re.search(pattern, line)
                if match:
                    whitespace, token1, other = match.groups()
                    line = f"{whitespace}if !{token1}{other}\n"
                
                
                
                
                
                # ======= as_type =======
                
                # reformat lib::L2CValue::as_integer(var1)
                # to var1
                pattern = r"(\s*)(.*)lib::L2CValue::as_integer\((.+?)\)(.*)"
                match = re.search(pattern, line)
                if match:
                    whitespace, other1, token1, other2 = match.groups()
                    line = f"{whitespace}{other1}{token1}{other2}\n"
                
                
                # reformat lib::L2CValue::as_hash(var1)
                # to var1
                pattern = r"(\s*)(.*)lib::L2CValue::as_hash\((.+?)\)(.*)"
                match = re.search(pattern, line)
                if match:
                    whitespace, other1, token1, other2 = match.groups()
                    line = f"{whitespace}{other1}{token1}{other2}\n"
                
                
                # reformat lib::L2CValue::as_bool(var1)
                # to var1
                pattern = r"(\s*)(.*)lib::L2CValue::as_bool\((.+?)\)(.*)"
                match = re.search(pattern, line)
                if match:
                    whitespace, other1, token1, other2 = match.groups()
                    line = f"{whitespace}{other1}{token1}{other2}\n"
                
                
                
                
                # ======= misc =======
                
                # reformat (bool)(var1 & 1)
                # to var1
                pattern = r"(\s*)(.*)\(bool\)\((.+?) & 1\)(.*)"
                match = re.search(pattern, line)
                if match:
                    whitespace, other1, token1, other2 = match.groups()
                    line = f"{whitespace}{other1}{token1}{other2}\n"
                
                
                # reformat lib::L2CValue::L2CValue(var1,var2);
                # to var1 = var2;
                pattern = r"(\s*)lib::L2CValue::L2CValue\((.+?),(.+?)\);\n"
                match = re.fullmatch(pattern, line)
                if match:
                    whitespace, token1, token2 = match.groups()
                    line = f"{whitespace}{token1} = {token2};\n"
                
                
                # reformat lib::L2CValue::~L2CValue(var1);
                # to //free(var1);
                pattern = r"(\s*)lib::L2CValue::~L2CValue\((.+?)\);\n"
                match = re.fullmatch(pattern, line)
                if match:
                    whitespace, token1 = match.groups()
                    line = f"{whitespace}// free({token1});\n"
                
                
                modified_lines.append(line)  
            
            # Write back the modified lines to the file
            with open(file_path, 'w') as file:
                file.writelines(modified_lines)


if __name__ == "__main__":
    translate()
