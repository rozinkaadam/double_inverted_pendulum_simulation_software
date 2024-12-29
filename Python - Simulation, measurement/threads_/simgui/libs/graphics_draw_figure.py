import pygame
import math

def draw_figure(sim_win_ref, x, y, theta_1, theta_2, L1, L2, geometry_config, scale_vector, draw_mass, draw_rod_a, draw_rod_b, infinite_space):
    """
    Draws the double inverted pendulum system including the mass and rods based on the provided parameters.

    Args:
        sim_win_ref: Reference to the simulation window object.
        x (float): X-coordinate of the cart.
        y (float): Y-coordinate of the cart.
        theta_1 (float): Angle of the first pendulum rod relative to vertical.
        theta_2 (float): Angle of the second pendulum rod relative to vertical.
        L1 (float): Length of the first pendulum rod.
        L2 (float): Length of the second pendulum rod.
        geometry_config (dict): Contains graphical properties like colors and sizes.
        scale_vector (list): Scaling factors for length and angle.
        draw_mass (bool): Whether to draw the cart mass.
        draw_rod_a (bool): Whether to draw the first pendulum rod.
        draw_rod_b (bool): Whether to draw the second pendulum rod.
        infinite_space (bool): Whether the simulation space wraps around.

    Returns:
        tuple: End coordinates of rod A and rod B as (end_rod_a, end_rod_b).
    """
    end_rod_a = None
    end_rod_b = None

    # Draw the cart mass
    if draw_mass:
        if infinite_space:
            _draw_wrapping_rect(sim_win_ref, x, y, geometry_config["mass_color_-"], geometry_config["mass_width_px"], geometry_config["mass_height_px"])
        else:
            _draw_rect(sim_win_ref, x, y, geometry_config["mass_color_-"], geometry_config["mass_width_px"], geometry_config["mass_height_px"])

    # Draw the first pendulum rod (Rod A)
    if draw_rod_a:
        end_a_delta_x = L1 * scale_vector[1] * math.sin(theta_1 * scale_vector[2]) * -1
        end_a_delta_y = L1 * scale_vector[1] * math.cos(theta_1 * scale_vector[2]) * -1
        end_rod_a = (x + end_a_delta_x, y + end_a_delta_y)
        if infinite_space:
            _draw_wrapping_rod(sim_win_ref, (x, y), (end_rod_a[0], end_rod_a[1]), geometry_config["rod_a_thickness_px"], geometry_config["rod_a_color_-"])
        else:
            _draw_rod(sim_win_ref, (x, y), (end_rod_a[0], end_rod_a[1]), geometry_config["rod_a_thickness_px"], geometry_config["rod_a_color_-"])

    # Draw the second pendulum rod (Rod B)
    if draw_rod_b:
        end_b_delta_x = L2 * scale_vector[1] * math.sin(theta_2) * -1
        end_b_delta_y = L2 * scale_vector[1] * math.cos(theta_2) * -1
        end_rod_b = (end_rod_a[0] + end_b_delta_x, end_rod_a[1] + end_b_delta_y)
        if infinite_space:
            _draw_wrapping_rod(sim_win_ref, (end_rod_a[0], end_rod_a[1]), (end_rod_b[0], end_rod_b[1]), geometry_config["rod_b_thickness_px"], geometry_config["rod_b_color_-"])
        else:
            _draw_rod(sim_win_ref, (end_rod_a[0], end_rod_a[1]), (end_rod_b[0], end_rod_b[1]), geometry_config["rod_b_thickness_px"], geometry_config["rod_b_color_-"])

    return end_rod_a, end_rod_b

## Draws a rectangle representing the cart mass.
def _draw_rect(sim_win_ref, x, y, color, width, height):
    """
    Draws a rectangle on the screen.

    Args:
        sim_win_ref: Reference to the simulation window object.
        x (float): X-coordinate of the rectangle center.
        y (float): Y-coordinate of the rectangle center.
        color (tuple): RGB color of the rectangle.
        width (float): Width of the rectangle.
        height (float): Height of the rectangle.
    """
    pygame.draw.rect(sim_win_ref.window, color, (x - width / 2, y - height / 2, width, height))

## Draws a line representing a pendulum rod.
def _draw_rod(sim_win_ref, startVector, endVector, thickness, color):
    """
    Draws a line segment representing a rod.

    Args:
        sim_win_ref: Reference to the simulation window object.
        startVector (tuple): Starting point of the rod.
        endVector (tuple): Ending point of the rod.
        thickness (int): Thickness of the line.
        color (tuple): RGB color of the rod.
    """
    pygame.draw.line(sim_win_ref.window, color, (startVector[0], startVector[1]), (endVector[0], endVector[1]), thickness)

## Draws a rectangle that wraps around the screen edges.
def _draw_wrapping_rect(sim_win_ref, x, y, color, width, height):
    """
    Draws a rectangle that wraps around the screen.

    Args:
        sim_win_ref: Reference to the simulation window object.
        x (float): X-coordinate of the rectangle center.
        y (float): Y-coordinate of the rectangle center.
        color (tuple): RGB color of the rectangle.
        width (float): Width of the rectangle.
        height (float): Height of the rectangle.
    """
    screen_width, screen_height = sim_win_ref.window.get_size()

    rect_x, rect_y, rect_width, rect_height = x - width / 2, y - height / 2, width, height

    for offset_x in [-screen_width, 0, screen_width]:
        for offset_y in [-screen_height, 0, screen_height]:
            wrapped_rect = pygame.Rect(
                rect_x + offset_x, rect_y + offset_y, rect_width, rect_height
            )
            pygame.draw.rect(sim_win_ref.window, color, wrapped_rect, width)

## Draws a line segment that wraps around the screen edges.
def _draw_wrapping_rod(sim_win_ref, start_pos, end_pos, thickness, color):
    """
    Draws a rod that wraps around the screen.

    Args:
        sim_win_ref: Reference to the simulation window object.
        start_pos (tuple): Starting position of the rod.
        end_pos (tuple): Ending position of the rod.
        thickness (int): Thickness of the line.
        color (tuple): RGB color of the rod.
    """
    screen_width, screen_height = sim_win_ref.window.get_size()

    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]

    for offset_x in [-screen_width, 0, screen_width]:
        for offset_y in [-screen_height, 0, screen_height]:
            wrapped_start = (start_pos[0] + offset_x, start_pos[1] + offset_y)
            wrapped_end = (end_pos[0] + offset_x, end_pos[1] + offset_y)
            pygame.draw.line(sim_win_ref.window, color, wrapped_start, wrapped_end, thickness)
