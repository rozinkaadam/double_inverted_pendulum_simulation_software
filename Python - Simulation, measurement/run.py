import yaml
from init_program import programIniter as pI
import os

# Path to the configuration file
PROGRAM_CONFIG_FILE_PATH = "program_config.yaml"

def read_config_file(file_path):
    """
    Reads a YAML configuration file and returns its content as a dictionary.

    Parameters:
        file_path (str): Path to the YAML configuration file.

    Returns:
        dict: The content of the YAML file as a dictionary.
    """
    config_dict = {}
    try:
        assert os.path.isfile(file_path)
        with open(file_path, 'r') as file:
            config_dict = yaml.safe_load(file)
    except FileNotFoundError:
        print("The specified file was not found.")
    except Exception as e:
        print("An error occurred while reading the file:", str(e))
    
    return config_dict

def main():
    """
    The main function initializes the program by reading the configuration file
    and creating a programIniter instance.
    """
    program_config = read_config_file(PROGRAM_CONFIG_FILE_PATH)
    print(f"The content of '{PROGRAM_CONFIG_FILE_PATH}':")
    print(program_config)

    # Initialize the program with the loaded configuration
    prog_ref = pI(program_config)

if __name__ == "__main__":
    main()
