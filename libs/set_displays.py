import win32api
import win32con

def set_correct_display_settings(arrange_vertically=True):
    """
    Adjusts monitor settings. Either disables extra monitors or arranges them vertically based on the flag.

    Args:
        arrange_vertically (bool): If True, arrange monitors vertically. If False, disable extra monitors.

    Returns:
        list or None: Saved settings if successful, None otherwise.
    """
    # Save the current settings
    saved_settings = _save_current_settings()
    try:
        monitors = _get_monitor_info()
        if len(monitors) <= 1:
            print("Only one monitor is connected.")
            return None

        # Select the monitor with the highest resolution
        primary_monitor = max(monitors, key=lambda x: x['width'] * x['height'])
        print(f"Primary monitor: {primary_monitor['device']}")

        # Either arrange monitors vertically or disable extra monitors
        if arrange_vertically:
            print("Arranging monitors vertically...")
            _arrange_monitors_vertically(monitors, primary_monitor)
        else:
            print("Disabling extra monitors...")
            _disable_extra_monitors(monitors, primary_monitor)

        print("Settings applied successfully.")
        
    except Exception as e:
        # Restore the original settings in case of an error
        print(f"Error occurred: {e}")
        print("Restoring original settings...")
        _restore_settings(saved_settings)
        print("Settings restored.")
        saved_settings = None

    return saved_settings

def restore_og_display_settings(saved_settings):
    """
    Restores original display settings.

    Args:
        saved_settings (list): Previously saved monitor settings.
    """
    _restore_settings(saved_settings)
    print("Settings restored.")

def _get_monitor_info():
    """
    Retrieves information about all connected monitors.

    Returns:
        list: A list of dictionaries containing monitor information.
    """
    monitors = win32api.EnumDisplayMonitors()
    monitor_info = []

    for monitor in monitors:
        hmonitor, hdc, rect = monitor
        info = win32api.GetMonitorInfo(hmonitor)
        width = rect[2] - rect[0]
        height = rect[3] - rect[1]
        monitor_info.append({
            'device': info['Device'],
            'width': width,
            'height': height,
            'info': info
        })
    return monitor_info

def _save_current_settings():
    """
    Saves the current display settings of all monitors.

    Returns:
        list: A list of dictionaries containing the current settings.
    """
    settings = []
    monitors = win32api.EnumDisplayMonitors()
    for monitor in monitors:
        hmonitor, hdc, rect = monitor
        info = win32api.GetMonitorInfo(hmonitor)
        dm = win32api.EnumDisplaySettings(info['Device'], win32con.ENUM_CURRENT_SETTINGS)
        is_primary = dm.Position_x == 0 and dm.Position_y == 0
        settings.append({
            'device': info['Device'],
            'settings': dm,
            'position': (dm.Position_x, dm.Position_y),
            'resolution': (dm.PelsWidth, dm.PelsHeight),
            'primary': is_primary,
            'active': True if dm.PelsWidth > 0 and dm.PelsHeight > 0 else False
        })
    return settings

def _restore_settings(saved_settings):
    """
    Restores the display settings from the saved configuration.

    Args:
        saved_settings (list): Previously saved monitor settings.
    """
    if saved_settings is None:
        return
    for entry in saved_settings:
        device = entry['device']
        dm = entry['settings']
        position_x, position_y = entry['position']
        resolution_width, resolution_height = entry['resolution']
        active = entry['active']
        is_primary = entry['primary']

        if active:
            dm.PelsWidth = resolution_width
            dm.PelsHeight = resolution_height
            dm.Position_x = position_x
            dm.Position_y = position_y
            dm.DisplayFlags = win32con.CDS_SET_PRIMARY if is_primary else 0

            result = win32api.ChangeDisplaySettingsEx(device, dm, win32con.CDS_UPDATEREGISTRY)
            if result != win32con.DISP_CHANGE_SUCCESSFUL:
                print(f"Failed to enable the monitor: {device}")
            else:
                print(f"Successfully enabled the monitor: {device}")
        else:
            dm.PelsWidth = 0
            dm.PelsHeight = 0
            dm.Position_x = -1
            dm.Position_y = -1
            win32api.ChangeDisplaySettingsEx(device, dm)

def _disable_extra_monitors(monitors, primary_monitor):
    """
    Disable all monitors except the primary one.

    Args:
        monitors (list): List of all connected monitors.
        primary_monitor (dict): The primary monitor to keep active.
    """
    for monitor in monitors:
        if monitor['device'] != primary_monitor['device']:
            _disable_monitor(monitor['device'])

def _set_primary_monitor(device_name):
    """
    Sets a monitor as the primary display.

    Args:
        device_name (str): The name of the monitor to set as primary.
    """
    dm = win32api.EnumDisplaySettings(device_name, win32con.ENUM_CURRENT_SETTINGS)
    dm.Position_x = 0
    dm.Position_y = 0
    dm.DisplayFlags = win32con.CDS_SET_PRIMARY
    win32api.ChangeDisplaySettingsEx(device_name, dm)

def _disable_monitor(device_name):
    """
    Disables a monitor.

    Args:
        device_name (str): The name of the monitor to disable.
    """
    dm = win32api.EnumDisplaySettings(device_name, win32con.ENUM_CURRENT_SETTINGS)
    dm.PelsWidth = 0
    dm.PelsHeight = 0
    dm.Position_x = -1
    dm.Position_y = -1
    win32api.ChangeDisplaySettingsEx(device_name, dm)

def _arrange_monitors_vertically(monitors, primary_monitor):
    """
    Arranges all monitors vertically with the primary monitor at the bottom.

    Args:
        monitors (list): List of all connected monitors.
        primary_monitor (dict): The primary monitor to position at the bottom.
    """
    current_y = 0
    for monitor in sorted(monitors, key=lambda m: m['device'] == primary_monitor['device']):
        device = monitor['device']
        dm = win32api.EnumDisplaySettings(device, win32con.ENUM_CURRENT_SETTINGS)

        if monitor == primary_monitor:
            dm.Position_x = 0
            dm.Position_y = current_y
            current_y += dm.PelsHeight
        else:
            dm.Position_x = 0
            dm.Position_y = current_y
            current_y += dm.PelsHeight

        result = win32api.ChangeDisplaySettingsEx(device, dm, win32con.CDS_UPDATEREGISTRY)
        if result != win32con.DISP_CHANGE_SUCCESSFUL:
            print(f"Failed to arrange monitor: {device}")
        else:
            print(f"Monitor arranged: {device}")
