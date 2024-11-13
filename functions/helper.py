import re

# Helper function that 
# 1. confirms that a section/option exists before trying to access it and
# 2. determines whether to use .get or .getboolean to get the setting
# Ignorewarnings support is for the Development section. Best to keep it around for now
def getsafe(config, section, option, ignorewarnings=False):
    # Check if section exists
    if not config.has_section(section):
        if not ignorewarnings: 
            print(f"Section '{section}' not found in autotranslate_settings.ini- Stopping!\nIf you've recently updated, delete autotranslate_settings.ini and try again.")
            exit() 
        else: return False
    
    # Check if option exists
    if not config.has_option(section, option):
        if not ignorewarnings: 
            print(f"Option '{option}' not found in autotranslate_settings.ini- Stopping!\nIf you've recently updated, delete autotranslate_settings.ini and try again.")
            exit() 
        else: return False

    # Determine whether to use .get or .getboolean
    value = config.get(section, option)
    if value.lower() in ['true', 'false', 'yes', 'no', '1', '0']:
        return config.getboolean(section, option)
    else:
        return value

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
