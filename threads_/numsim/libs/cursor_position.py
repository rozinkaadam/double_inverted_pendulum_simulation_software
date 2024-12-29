import pyautogui
import time

def get_mouse_position(screen_width_px: int, const_null_pos=False):
    """
    Get the current mouse position or return a constant null position.

    Parameters:
    - screen_width_px (int): The width of the screen in pixels.
    - const_null_pos (bool): If True, returns the screen center as the position.

    Returns:
    - list: A list containing the mouse position (x-coordinate) and timestamp.
    """
    timestamp = time.time()
    pos_x = round(screen_width_px / 2)  # Default to the center of the screen
    if not const_null_pos:
        pos_x = pyautogui.position()[0]  # Get the actual mouse position

    return [pos_x, timestamp]

def update(cursor_state, plotable_datasets, screen_width_px: int, const_null_pos: bool, meter_per_pixel: float):
    """
    Update cursor state and plotable datasets based on mouse movement.

    Parameters:
    - cursor_state (dict): The current state of the cursor including position, velocity, and acceleration.
    - plotable_datasets (dict): Stores data for plotting (e.g., position, velocity, acceleration).
    - screen_width_px (int): The width of the screen in pixels.
    - const_null_pos (bool): If True, sets the cursor position to a constant value.
    - meter_per_pixel (float): Conversion factor from pixels to meters.

    Returns:
    - None
    """
    # Check if cursor state needs to be updated
    if cursor_state["cursor_replace_flag"] == 2:
        cursor_state["cursor_replace_flag"] = 0
    elif cursor_state["cursor_replace_flag"] == 1:
        return  # Skip updating if replace flag is active

    # Get mouse position and apply offset for replacement counter
    x, x_ts = get_mouse_position(screen_width_px, const_null_pos)
    x += cursor_state["replace_counter"] * (screen_width_px - 2)
    cursor_state["x"].append([x, x_ts])
    plotable_datasets["x"].append(x)

    # Calculate velocity if there are at least two position samples
    if len(cursor_state["x"]) > 1:
        dt = cursor_state["x"][-1][1] - cursor_state["x"][-2][1]  # Time difference
        at = (cursor_state["x"][-1][1] + cursor_state["x"][-2][1]) / 2  # Average timestamp
        dx = (cursor_state["x"][-1][0] - cursor_state["x"][-2][0]) / dt  # Velocity calculation
        cursor_state["dx"].append([dx, at, dt])
        plotable_datasets["dx"].append(dx)

        # Update sampling intervals
        cursor_state["h_s"].append(dt)

    # Calculate acceleration if there are at least two velocity samples
    if len(cursor_state["dx"]) > 1:
        dt = cursor_state["dx"][-1][1] - cursor_state["dx"][-2][1]  # Time difference
        at = (cursor_state["dx"][-1][1] + cursor_state["dx"][-2][1]) / 2  # Average timestamp
        ddx = (cursor_state["dx"][-1][0] - cursor_state["dx"][-2][0]) / dt  # Acceleration calculation
        cursor_state["ddx"].append([ddx, at, dt])
        plotable_datasets["ddx"].append(ddx)

        # Convert values to meters
        x_m = x * meter_per_pixel
        dx_m = dx * meter_per_pixel
        ddx_m = ddx * meter_per_pixel
        cursor_state["ddx_m"].append(ddx_m)
        cursor_state["q_array_list"].append([x_m, dx_m, ddx_m, x_ts])
        plotable_datasets["x_m"].append(x_m)
        plotable_datasets["dx_m"].append(dx_m)
        plotable_datasets["ddx_m"].append(ddx_m)
