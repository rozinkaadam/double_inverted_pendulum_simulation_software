import winreg
import ctypes
import threading

def set_enhance_pointer_precision(enable: bool, timeout=5):
    """
    Enables or disables the "Enhance Pointer Precision" feature and applies the change.

    Args:
        enable (bool): True to enable, False to disable the feature.
        timeout (int): Timeout in seconds for the SystemParametersInfoW call (default: 5).

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    try:
        # Update the registry key
        key_path = r"Control Panel\Mouse"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            value = "1" if enable else "0"
            winreg.SetValueEx(key, "MouseSpeed", 0, winreg.REG_SZ, value)
        print(f'Enhance pointer precision registry updated to {"enabled" if enable else "disabled"}.')

        # Call SystemParametersInfoW with a timeout
        result = [False]  # Store the result in a list

        def call_api():
            result[0] = ctypes.windll.user32.SystemParametersInfoW(0x001A, 0, None, 0)

        thread = threading.Thread(target=call_api)
        thread.start()
        thread.join(timeout)

        if thread.is_alive():
            print("SystemParametersInfoW call timed out.")
            return False

        # Check the result
        if result[0]:
            print("SystemParametersInfoW successfully executed.")
        else:
            print("SystemParametersInfoW failed to execute.")
        return result[0]

    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def is_enhance_pointer_precision_enabled():
    """
    Checks whether the "Enhance Pointer Precision" feature is enabled.

    Returns:
        bool: True if the feature is enabled, False otherwise.
    """
    try:
        # Open the registry key for mouse settings
        key_path = r"Control Panel\Mouse"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as key:
            # Read the "MouseSpeed" value
            mouse_speed, _ = winreg.QueryValueEx(key, "MouseSpeed")
            # "1" means enabled, "0" means disabled
            return mouse_speed == "1"
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
