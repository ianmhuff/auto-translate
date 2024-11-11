import os
import sys
import configparser
import urllib.request

from functions import translate, condense

# Main functionality
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

    # Run translate_script and condense_script on a file
    def translate_helper(file_path, config, do_condense_script):
        new_file_path = translate.translate_script(file_path, config)
        print(f"Processed file: {file_path} -> {new_file_path}")
        if do_condense_script:
            condense.condense_script(new_file_path)
            print(f"Condensed file: {new_file_path}")

    # Determine how the script was executed
    if len(sys.argv) < 2:
        # SCRIPT CLICKED / RAN IN CONSOLE
        output_file_type = config.get('FileHandling', 'output_file_type')
        input(f"===WARNING===\nThis script will read all {valid_extensions} files in the current directory and output as [{output_file_type}].\nIf you wish to proceed, press Enter. Otherwise Ctrl+C to exit\n> ")
        is_condense_script = get_is_condense_script(config)
        if is_condense_script:
            print('===WARNING===\nCondense script feature is currently in development and will be buggy')
        # Loop through files
        for filename in os.listdir(current_directory):
            # Only modify files with specified extensions
            ext = os.path.splitext(filename)[1]
            if ext not in valid_extensions:
                continue

            # Run translate function on script
            file_path = os.path.join(current_directory, filename)
            translate_helper(file_path, config, is_condense_script)
    else:
        # FILES DRAGGED ONTO SCRIPT
        is_condense_script = get_is_condense_script(config)
        if is_condense_script:
            print('===WARNING===\nCondense script feature is currently in development and will be buggy')
        # Loop through files
        for file_path in sys.argv[1:]:
            translate_helper(file_path, config, is_condense_script)

    input("\nPress Enter to exit...")

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

# Gets the condense_script setting in autotranslate_settings.ini
def get_is_condense_script(config):
    if config.has_section('Development') and config.has_option('Development', 'condense_script'):
        is_condense_script = config.getboolean('Development', 'condense_script')
    else: 
        is_condense_script = False
    return is_condense_script

# Download ParamLabels.csv from ultimate-research if it doesn't already exist
def create_paramlabels(param_labels_path):
    print(f"{param_labels_path} not found. Downloading ParamLabels.csv...")
    paramlabels_url = "https://raw.githubusercontent.com/ultimate-research/param-labels/refs/heads/master/ParamLabels.csv"
    try:
        urllib.request.urlretrieve(paramlabels_url, param_labels_path)
        print(f"Downloaded ParamLabels.csv to {param_labels_path}.")
    except Exception as e:
        print(f"Failed to download ParamLabels.csv: {e}")

if __name__ == "__main__":
    main()
