import pygame

def msg_center_top(sim_win_ref, msg_str):
    """
    Display a message at the top center of the simulation window.

    Args:
        sim_win_ref: Reference to the simulation window object.
        msg_str (str): The message string to display. Supports multiline messages separated by '\n'.
    """
    TOP_MARGIN = 20  # Margin from the top of the screen in pixels
    FONT_SIZE = 36  # Font size for the message text

    font = pygame.font.SysFont(None, FONT_SIZE)
    black = (200, 200, 200)  # Text color (RGB)

    lines = msg_str.split('\n')  # Split message into lines for multiline support
    w, h = sim_win_ref.window.get_size()  # Get window dimensions

    y = TOP_MARGIN  # Initial y-coordinate for the first line
    for l in lines:
        text_surface = font.render(l, True, black)  # Render text as a surface
        text_rect = text_surface.get_rect()
        text_rect.center = (w / 2, y)  # Center align the text horizontally
        sim_win_ref.window.blit(text_surface, text_rect)  # Draw text on the window
        y += text_rect.height + 10  # Adjust y-coordinate for the next line with 10-pixel spacing

def msg_center(sim_win_ref, msg_str):
    """
    Display a message at the center of the simulation window.

    Args:
        sim_win_ref: Reference to the simulation window object.
        msg_str (str): The message string to display. Supports multiline messages separated by '\n'.
    """
    FONT_SIZE = 36  # Font size for the message text

    font = pygame.font.SysFont(None, FONT_SIZE)
    black = (200, 200, 200)  # Text color (RGB)

    lines = msg_str.split('\n')  # Split message into lines for multiline support
    w, h = sim_win_ref.window.get_size()  # Get window dimensions

    y = h / 2  # Initial y-coordinate for the first line, centered vertically
    for l in lines:
        text_surface = font.render(l, True, black)  # Render text as a surface
        text_rect = text_surface.get_rect()
        text_rect.center = (w / 2, y)  # Center align the text horizontally
        sim_win_ref.window.blit(text_surface, text_rect)  # Draw text on the window
        y += text_rect.height + 10  # Adjust y-coordinate for the next line with 10-pixel spacing

def msg_left_top(sim_win_ref, msg_str):
    """
    Display a message at the top-left corner of the simulation window.

    Args:
        sim_win_ref: Reference to the simulation window object.
        msg_str (str): The message string to display. Supports multiline messages separated by '\n'.
    """
    TOP_MARGIN = 20  # Margin from the top of the screen in pixels
    LEFT_MARGIN = 20  # Margin from the left of the screen in pixels
    FONT_SIZE = 18  # Font size for the message text

    font = pygame.font.SysFont(None, FONT_SIZE)
    black = (150, 150, 150)  # Text color (RGB)

    lines = msg_str.split('\n')  # Split message into lines for multiline support
    w, h = sim_win_ref.window.get_size()  # Get window dimensions

    y = TOP_MARGIN  # Initial y-coordinate for the first line
    for l in lines:
        text_surface = font.render(l, True, black)  # Render text as a surface
        text_rect = text_surface.get_rect()
        text_rect.topleft = (LEFT_MARGIN, y)  # Align the text to the top-left corner
        sim_win_ref.window.blit(text_surface, text_rect)  # Draw text on the window
        y += text_rect.height + 10  # Adjust y-coordinate for the next line with 10-pixel spacing
