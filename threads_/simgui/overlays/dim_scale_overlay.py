import pygame
import math

def custom_floor_round(number):
    """
    Custom rounding function that rounds a number to specific intervals (1, 2, 5, 10, etc.)
    based on its magnitude.

    Args:
        number (float): The number to round.

    Returns:
        float: The rounded number.
    """
    if number >= 1:
        magnitude = 10 ** math.floor(math.log10(number))  # Determine the magnitude of the number
        if number / magnitude >= 5:
            return 5 * magnitude
        elif number / magnitude >= 2:
            return 2 * magnitude
        else:
            return magnitude
    else:
        magnitude = 10 ** math.floor(math.log10(number))
        if number / magnitude >= 5:
            return 5 * magnitude
        elif number / magnitude >= 2:
            return 2 * magnitude
        elif number / magnitude >= 1:
            return magnitude
        else:
            return magnitude / 5

def custom_floor_round10(x):
    """
    Custom rounding function to round a number to 0.5, 1, 5, or 10 based on specific ranges.

    Args:
        x (float): The number to round.

    Returns:
        float: The rounded number.
    """
    if x < 10:
        return round(x * 2) / 2  # Round to the nearest 0.5
    elif x <= 20:
        return round(x)  # Round to the nearest integer
    elif x > 20 and x % 10 < 5:
        return 5 * round(x / 5)  # Round to the nearest 5
    else:
        return 10 * round(x / 10)  # Round to the nearest 10

def calculate_dim_scale_props(sim_win_ref, x, y, dim_scale_vector):
    """
    Calculate properties for dimension scaling and axis drawing based on window size and scaling factors.

    Args:
        sim_win_ref: Simulation window reference containing size information.
        x (int): X-coordinate of the origin.
        y (int): Y-coordinate of the origin.
        dim_scale_vector (list): Scaling factors for x, y, and rotation.

    Returns:
        tuple: Properties required for axis and scale drawing.
    """
    max_x_axis_length = sim_win_ref.win_w / 6
    max_y_axis_length = sim_win_ref.win_h / 4

    max_x_axis_length_in_m = max_x_axis_length / dim_scale_vector[0]
    max_y_axis_length_in_m = max_y_axis_length / dim_scale_vector[1]

    x_axis_unti = "m"
    y_axis_unti = "m"

    # Convert to millimeters if the length in meters is less than 1
    if max_x_axis_length_in_m < 1:
        max_x_axis_length_in_m *= 1000
        x_axis_unti = "mm"
    if max_y_axis_length_in_m < 1:
        max_y_axis_length_in_m *= 1000
        y_axis_unti = "mm"

    x_axis_length_in_m = custom_floor_round(max_x_axis_length_in_m)
    y_axis_length_in_m = custom_floor_round(max_y_axis_length_in_m)

    x_axis_length = x_axis_length_in_m * dim_scale_vector[0]  # Convert to pixels
    y_axis_length = y_axis_length_in_m * dim_scale_vector[1]
    if x_axis_unti == "mm":
        x_axis_length /= 1000
    if y_axis_unti == "mm":
        y_axis_length /= 1000

    phi_ref_deg = round(math.atan(1) * 180 / 3.1415, 2) / dim_scale_vector[2]

    phi_ref_end_x_px = y_axis_length * 0.8
    phi_ref_end_y_px = y_axis_length * 0.8

    x_axis_start_pos = [x, y]
    x_axis_end_pos = [x + x_axis_length, y]
    y_axis_start_pos = [x, y]
    y_axis_end_pos = [x, y - y_axis_length]
    rot_ref_end_pos = [x + phi_ref_end_x_px, y - phi_ref_end_y_px]

    return x_axis_start_pos, x_axis_end_pos, y_axis_start_pos, y_axis_end_pos, x_axis_length_in_m, y_axis_length_in_m, x_axis_unti, y_axis_unti, rot_ref_end_pos, phi_ref_deg

def draw_dim_scale(sim_win_ref, x_axis_start_pos, x_axis_end_pos, y_axis_start_pos, y_axis_end_pos, x_axis_length_in_m, y_axis_length_in_m, x_axis_unti, y_axis_unti, rot_ref_end_pos, phi_ref_deg_rounded):
    """
    Draw dimension scales and axes on the simulation window.

    Args:
        sim_win_ref: Simulation window reference.
        x_axis_start_pos (list): Start position of the x-axis.
        x_axis_end_pos (list): End position of the x-axis.
        y_axis_start_pos (list): Start position of the y-axis.
        y_axis_end_pos (list): End position of the y-axis.
        x_axis_length_in_m (float): Length of the x-axis in meters.
        y_axis_length_in_m (float): Length of the y-axis in meters.
        x_axis_unti (str): Unit for the x-axis (e.g., "m" or "mm").
        y_axis_unti (str): Unit for the y-axis (e.g., "m" or "mm").
        rot_ref_end_pos (list): End position for the rotation reference.
        phi_ref_deg_rounded (float): Rounded rotation reference in degrees.
    """
    font = pygame.font.SysFont(None, 18)
    black = (160, 160, 160)

    # Draw the x-axis end marker and label
    pygame.draw.line(sim_win_ref.window, black, (x_axis_end_pos[0], x_axis_end_pos[1] - 5), (x_axis_end_pos[0], x_axis_end_pos[1] + 5), 1)
    text = font.render(f"{x_axis_length_in_m} [{x_axis_unti}]", True, black)
    sim_win_ref.window.blit(text, (x_axis_end_pos[0] + 5, x_axis_end_pos[1] - 5))

    # Draw the y-axis end marker and label
    pygame.draw.line(sim_win_ref.window, black, (y_axis_end_pos[0] - 5, y_axis_end_pos[1]), (y_axis_end_pos[0] + 5, y_axis_end_pos[1]), 1)
    text = font.render(f"{y_axis_length_in_m} [{y_axis_unti}]", True, black)
    sim_win_ref.window.blit(text, (y_axis_end_pos[0] + 10, y_axis_end_pos[1] - 5))

    # Draw the rotation reference label
    text = font.render(f"{phi_ref_deg_rounded} [deg]", True, black)
    sim_win_ref.window.blit(text, (rot_ref_end_pos[0] + 10, rot_ref_end_pos[1] - 5))

    # Draw the x-axis
    pygame.draw.line(sim_win_ref.window, black, x_axis_start_pos, x_axis_end_pos, 1)
    # Draw the y-axis
    pygame.draw.line(sim_win_ref.window, black, y_axis_start_pos, y_axis_end_pos, 1)
    # Draw the rotation reference line
    pygame.draw.line(sim_win_ref.window, black, y_axis_start_pos, rot_ref_end_pos, 1)

def calculate_fit_dim_scale(win_width, win_height, l1, l2, mass_height, figure_pos_y, meter_per_pixel, rod_section_ratio, scale_rot_, scale_x_axis_, double_pendulum):
    """
    Calculate scaling factors for the simulation to fit dimensions on the screen.

    Args:
        win_width (int): Width of the simulation window.
        win_height (int): Height of the simulation window.
        l1 (float): Length of the first pendulum rod.
        l2 (float): Length of the second pendulum rod.
        mass_height (float): Height of the cart or base.
        figure_pos_y (float): Vertical position of the cart or base.
        meter_per_pixel (float): Conversion factor from meters to pixels.
        rod_section_ratio (float): Ratio for rod section scaling.
        scale_rot_ (float): Scaling factor for rotation.
        scale_x_axis_ (float): Scaling factor for the x-axis.
        double_pendulum (bool): Whether the simulation involves a double pendulum.

    Returns:
        list: Scaling factors for the x-axis, y-axis, and y-axis, and rotation adjustments.
    """
    if not double_pendulum:
        l2=0
        
    return [1/(meter_per_pixel*1000/scale_x_axis_), ((win_height-(mass_height+figure_pos_y))*rod_section_ratio)/(l1+l2), scale_rot_] # px/m