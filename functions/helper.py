import re

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
