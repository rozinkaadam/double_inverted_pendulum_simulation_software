import yaml
import config_gui.config_settings_gui as conf_gui

class programIniter:
    """
    Class to initialize the program by managing configuration files and GUI settings.

    Attributes:
        program_config_dict (dict): Program-specific configuration dictionary.
        def_config_dict (dict): Default configuration dictionary read from a YAML file.
        config_settings_gui (ConfigGUI): GUI object for managing configuration settings.
    """

    def __init__(self, program_config_dict) -> None:
        """
        Initializes the programIniter instance.

        Args:
            program_config_dict (dict): Program-specific configuration dictionary.
        """
        self.program_config_dict = program_config_dict
        self.def_config_dict = programIniter.read_default_config_file(
            self.program_config_dict["default_parameters_file_path"]
        )
        
        self.config_settings_gui = conf_gui.ConfigGUI(
            self.program_config_dict, self.def_config_dict
        )

    @staticmethod
    def read_default_config_file(file_path):
        """
        Reads the default configuration from a YAML file.

        Args:
            file_path (str): Path to the YAML configuration file.

        Returns:
            dict: Parsed configuration dictionary if successful, None otherwise.
        """
        try:
            with open(file_path, 'r') as file:
                config_dict = yaml.safe_load(file)
            print(f"Successfully read: {file_path}")
            return config_dict
        except FileNotFoundError:
            print(f"Error: Path not found: {file_path}")
        except PermissionError:
            print(f"Error: No permission to read file: {file_path}")
        except yaml.YAMLError as e:
            print(f"Error processing YAML file: {e}")
        except Exception as e:
            print(f"Unknown error occurred: {e}")

        return None

    @staticmethod
    def write_default_config_file(file_path, config_dict):
        """
        Writes the default configuration to a YAML file.

        Args:
            file_path (str): Path to the YAML configuration file.
            config_dict (dict): Configuration dictionary to save.

        Returns:
            bool: True if the file is successfully written, False otherwise.
        """
        try:
            with open(file_path, 'w') as file:
                yaml.safe_dump(
                    config_dict, file, 
                    default_flow_style=False, allow_unicode=True, sort_keys=False
                )
            print(f"Successfully saved: {file_path}")
            return True
        except FileNotFoundError:
            print(f"Error: Path not found: {file_path}")
        except PermissionError:
            print(f"Error: No permission to write file: {file_path}")
        except Exception as e:
            print(f"Unknown error occurred: {e}")

        return False