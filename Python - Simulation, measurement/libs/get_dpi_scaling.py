import ctypes

def get_dpi_scaling():
    """
    Retrieves the DPI scaling factor of the primary monitor.

    This function queries the DPI setting of the primary display using the Windows API.

    Returns:
        float: The DPI scaling factor (e.g., 1.0 for 96 DPI, 1.25 for 120 DPI).
    """
    # Get the device context for the primary monitor
    hdc = ctypes.windll.user32.GetDC(0)
    
    # Query the DPI of the primary monitor (LOGPIXELSX = 88)
    dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)
    
    # Release the device context
    ctypes.windll.user32.ReleaseDC(0, hdc)
    
    # Calculate the DPI scaling factor
    return dpi / 96  # 96 DPI is the default DPI
