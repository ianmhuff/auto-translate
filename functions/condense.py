import re

# Replace vars & move variables to shorten a script as much as possible
def condense_script(file_path):
    # Get content from file
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.readlines()

    # Regex patterns
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

        # Find variable assignments (var1 = var2)
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

    # Delete lines with delete param true
    lines_to_delete = {var['line'] for var in variables if var['delete']}
    content = [line for i, line in enumerate(content, start=1) if i not in lines_to_delete]

    # Remove return value lines with no actual ret val 
    content = [line for line in content if line.strip() != "return return_value.into();"]

    simplify_bools(content)
    remove_arrow_l2c(content)    
    remove_last_semicolon(content)

    # Write the modified content back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(content)

# Remove == true, != false, and all combinations
def simplify_bools(content):
    for line_number, line in enumerate(content):
        if " == false" in line or " != true" in line:
            if "if !" in line:
                line = line.replace("if !", "if ")
            elif "if " in line:
                line = line.replace("if ", "if !")
        line = re.sub(r'\s*(==|!=)\s*(true|false)', '', line)
        content[line_number] = line

# Removes " -> L2CValue" from FUN functs with no return in them
def remove_arrow_l2c(content):
    if content and "FUN_71" in content[0]:
        # Check for "return" in the entire content
        if not any("return" in line for line in content):
            # Remove " -> L2CValue" from the first line
            content[0] = content[0].replace(" -> L2CValue", "")

# If last line is a sub_shift_status_main or fastshift, remove semicolon for implied return
def remove_last_semicolon(content):
    for i in range(len(content) - 1, -1, -1):
        line = content[i]
        if line and '}' not in line:
            if "sub_shift_status_main" in line or "fastshift" in line:
                content[i] = line.replace(';', '')
            break