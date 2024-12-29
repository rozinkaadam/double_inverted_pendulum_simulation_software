import numpy as np

def sys_matrices_double_pendulum(sys_consts_double, X_list, dphi1, dphi2):
    """
    Compute the system matrices for a double inverted pendulum on a cart (DIPC).

    Parameters:
    - sys_consts_double (tuple): System constants including mass, lengths, and other physical parameters.
    - X_list (list): List of trigonometric functions of angles and their differences (e.g., sin and cos values).
    - dphi1 (float): Angular velocity of the first pendulum.
    - dphi2 (float): Angular velocity of the second pendulum.

    Returns:
    - A (np.ndarray): The system dynamics matrix.
    - B (np.ndarray): The input matrix.
    - L (np.ndarray): The linearized gravitational force matrix.
    """
    # Unpack system constants
    C1, C2, C3, C4, C5, m1, m2, l1, l2, g = sys_consts_double
    X1, X2, X3, X4, X5, X6 = X_list

    # Denominator for normalization in matrix calculations
    s1 = C3 * C3 * X6 * X6 - C1 * C2

    # Dynamics matrix A
    A = np.array([
        [0, 0, 1, 0],
        [0, 0, 0, 1],
        [0, 0, dphi1 * C3 * C3 * X6 * X5 / s1, dphi2 * C2 * C3 * X5 / s1],
        [0, 0, -dphi1 * C1 * C3 * X5 / s1, -dphi2 * C3 * C3 * X6 * X5 / s1]
    ])

    # Input matrix B
    B = np.array([
        [0],
        [0],
        [-(C2 * l1 * m1 * X2 + 2 * C2 * l1 * m2 * X2 - C3 * l2 * m2 * X4 * X6) / (2 * s1)],
        [(C3 * l1 * m1 * X2 * X6 - C1 * l2 * m2 * X4 + 2 * C3 * l1 * m2 * X2 * X6) / (2 * s1)]
    ])

    # Linearized gravitational forces matrix L
    L = np.array([
        [0],
        [0],
        [(C2 * C4 * X1 - C3 * C5 * X3 * X6) / s1],
        [(C1 * C5 * X3 - C3 * C4 * X1 * X6) / s1]
    ])

    return A, B, L

def linearized_DIPC_sys_matrices(sys_consts_double):
    """
    Compute the linearized system matrices for a double inverted pendulum on a cart (DIPC).

    Parameters:
    - sys_consts_double (tuple): System constants including mass, lengths, and other physical parameters.

    Returns:
    - A_lin (np.ndarray): Linearized dynamics matrix.
    - B_lin (np.ndarray): Linearized input matrix.
    """
    # Unpack system constants
    C1, C2, C3, C4, C5, m1, m2, l1, l2, g = sys_consts_double

    # Denominator for normalization in linearized matrices
    s1 = C3 * C3 - C1 * C2

    # Linearized dynamics matrix A_lin
    A_lin = np.array([
        [0, 0, 1, 0],
        [0, 0, 0, 1],
        [C2 * C4 / s1, -C3 * C5 / s1, 0, 0],
        [-C3 * C4 / s1, C1 * C5 / s1, 0, 0]
    ])

    # Linearized input matrix B_lin
    B_lin = np.array([
        [0],
        [0],
        [-(C2 * l1 * m1 + 2 * C2 * l1 * m2 - C3 * l2 * m2) / (2 * s1)],
        [(C3 * l1 * m1 - C1 * l2 * m2 + 2 * C3 * l1 * m2) / (2 * s1)]
    ])

    return A_lin, B_lin
