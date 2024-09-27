# auto-translate.py
# v0.3

# ideas/todo:
# deal with return_value_xx lines
# operators other than = (==, +, -, *, <, >, <=, >=, etc.) (also operator.cast.to.bool ?)
# other as_[type]() functions (currently handling as_integer() and as_hash())
# _SITUATION... -> *SITUATION... (also _FIGHTER..., _GROUND..., etc)
#   this seems difficult to do comprehensively without a complete list of cases where this happens
# returns? i.e. return_value = 0; -> return 0.into();
#   this one would need to be at the bottom since it depends on the formatting


import os
import re

def translate():
    # Get the current directory
    current_directory = os.getcwd()

    # Iterate through all files in the directory
    for filename in os.listdir(current_directory):
    
        #don't modify the script file lmao
        if filename == os.path.basename(__file__):
            continue
        
        file_path = os.path.join(current_directory, filename)

        # Only process files (not directories)
        if os.path.isfile(file_path):
            with open(file_path, 'r') as file:
                lines = file.readlines()
            
            # Create a new list to hold modified lines
            modified_lines = []
            
            for line in lines:                
                
                # remove "(L2CValue *)&" from all lines
                substring = "(L2CValue *)&"
                if substring in line:
                    line = line.replace(substring, "")
                
                
                # remove "(L2CValue *)" from all lines
                substring = "(L2CValue *)"
                if substring in line:
                    line = line.replace(substring, "")
                
                
                # remove "app::lua_bind::" from all lines
                substring = "app::lua_bind::"
                if substring in line:
                    line = line.replace(substring, "")
                
                
                # remove "_impl" from all lines
                substring = "_impl"
                if substring in line:
                    line = line.replace(substring, "")
                
                
                # replace __
                # with ::
                substring = "__"
                if substring in line:
                    line = line.replace(substring, "::")
                
                
                # reformat lib::L2CValue::~L2CValue(var1);
                # to //free(var1);
                pattern = r"(\s*)lib::L2CValue::~L2CValue\((.+?)\);\n"
                match = re.fullmatch(pattern, line)
                if match:
                    print(match)
                    whitespace, token1 = match.groups()
                    line = f"{whitespace}//free({token1});\n"
                
                
                # replace this->moduleAccessor
                # with fighter.module_accessor
                substring = "this->moduleAccessor"
                if substring in line:
                    line = line.replace(substring, "fighter.module_accessor")
                
                
                # replace this->globalTable
                # with fighter.global_table
                substring = "this->globalTable"
                if substring in line:
                    line = line.replace(substring, "fighter.global_table")
                
                
                # reformat lib::L2CValue::L2CValue(var1,var2);
                # to var1 = var2;
                pattern = r"(\s*)lib::L2CValue::L2CValue\((.+?),\s*(.+?)\);\n"
                match = re.fullmatch(pattern, line)
                if match:
                    print(match)
                    whitespace, token1, token2 = match.groups()
                    line = f"{whitespace}{token1} = {token2};\n"
                
                
                # reformat lib::L2CValue::operator=(var1,var2);
                # to var1 = var2;
                pattern = r"(\s*)lib::L2CValue::operator=\((.+?),\s*(.+?)\);\n"
                match = re.fullmatch(pattern, line)
                if match:
                    print(match)
                    whitespace, token1, token2 = match.groups()
                    line = f"{whitespace}{token1} = {token2};\n"
                
                
                # reformat if ((var1 & 1) != 0)
                # to if var1
                pattern = r"(\s*)if \(\((.+?) & 1\) != 0\)(.*)"
                match = re.search(pattern, line)
                if match:
                    print(match)
                    whitespace, token1, other = match.groups()
                    line = f"{whitespace}if {token1}{other}\n"
                
                
                # reformat if ((var1 & 1) == 0)
                # to if !var1
                pattern = r"(\s*)if \(\((.+?) & 1\) == 0\)(.*)"
                match = re.search(pattern, line)
                if match:
                    print(match)
                    whitespace, token1, other = match.groups()
                    line = f"{whitespace}if !{token1}{other}\n"
                
                
                # reformat if ((var1 & 1U) != 0)
                # to if var1
                pattern = r"(\s*)if \(\((.+?) & 1U\) != 0\)(.*)"
                match = re.search(pattern, line)
                if match:
                    print(match)
                    whitespace, token1, other = match.groups()
                    line = f"{whitespace}if {token1}{other}\n"
                
                
                # reformat if ((var1 & 1U) == 0)
                # to if !var1
                pattern = r"(\s*)if \(\((.+?) & 1U\) == 0\)(.*)"
                match = re.search(pattern, line)
                if match:
                    print(match)
                    whitespace, token1, other = match.groups()
                    line = f"{whitespace}if !{token1}{other}\n"
                
                
                # reformat (bool)(var1 & 1)
                # to var1
                pattern = r"(\s*)(.*)\(bool\)\((.+?) & 1\)(.*)"
                match = re.search(pattern, line)
                if match:
                    print(match)
                    whitespace, other1, token1, other2 = match.groups()
                    line = f"{whitespace}{other1}{token1}{other2}\n"
                
                
                # reformat lib::L2CValue::as_integer(var1)
                # to var1
                pattern = r"(\s*)(.*)lib::L2CValue::as_integer\((.+?)\)(.*)"
                match = re.search(pattern, line)
                if match:
                    print(match)
                    whitespace, other1, token1, other2 = match.groups()
                    line = f"{whitespace}{other1}{token1}{other2}\n"
                
                
                # reformat lib::L2CValue::as_hash(var1)
                # to var1
                pattern = r"(\s*)(.*)lib::L2CValue::as_hash\((.+?)\)(.*)"
                match = re.search(pattern, line)
                if match:
                    print(match)
                    whitespace, other1, token1, other2 = match.groups()
                    line = f"{whitespace}{other1}{token1}{other2}\n"
                
                
                modified_lines.append(line)  
            
            # Write back the modified lines to the file
            with open(file_path, 'w') as file:
                file.writelines(modified_lines)


if __name__ == "__main__":
    translate()
