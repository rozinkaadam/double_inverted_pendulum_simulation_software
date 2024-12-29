import numpy as np

def mov_eqn_single_pendulum(sys_consts_single, phi_frame:np.array, ddq):
    """
    Computes the motion equation for a single pendulum on a cart.

    Parameters:
    - sys_consts_single (tuple): System constants (C1, C2, m1, L1, g).
    - phi_frame (np.array): State of the pendulum [phi, dphi, ddphi, ...].
    - ddq (float): Cart acceleration.

    Returns:
    - np.array: Array containing the updated state of the pendulum [dphi, ddphi].
    """
    C1, C2, m1, L1, g = sys_consts_single

    # Extract the angle from the state frame
    phi_frame_list = phi_frame.tolist()
    phi1 = phi_frame_list[0][0]

    # Calculate sine and cosine of the angle
    X1 = np.sin(phi1) 
    X2 = np.cos(phi1)

    # Compute angular acceleration
    phi_ddot = C1 * ddq * X2 + C2 * X1

    return np.array([[phi_frame_list[2][0]], [phi_frame_list[3][0]], [phi_ddot], [0]])

def sys_matrices_double_pendulum(sys_consts_double, X_list, dphi1, dphi2):
    """
    Computes the system matrices for a double pendulum on a cart.

    Parameters:
    - sys_consts_double (tuple): System constants (C1, C2, C3, C4, C5, m1, m2, l1, l2, g).
    - X_list (list): List of trigonometric terms [sin(phi1), cos(phi1), sin(phi2), cos(phi2), sin(phi1-phi2), cos(phi1-phi2)].
    - dphi1 (float): Angular velocity of the first pendulum.
    - dphi2 (float): Angular velocity of the second pendulum.

    Returns:
    - A (np.array): State matrix.
    - B (np.array): Input matrix.
    - L (np.array): External input matrix.
    """
    C1, C2, C3, C4, C5, m1, m2, l1, l2, g = sys_consts_double
    X1, X2, X3, X4, X5, X6 = X_list

    # Determinant of the system
    s1 = C3 * C3 * X6 * X6 - C1 * C2

    # State matrix
    A = np.array([
        [0, 0, 1, 0],
        [0, 0, 0, 1],
        [0, 0, dphi1 * C3 * C3 * X6 * X5 / s1, dphi2 * C2 * C3 * X5 / s1],
        [0, 0, -dphi1 * C1 * C3 * X5 / s1, -dphi2 * C3 * C3 * X6 * X5 / s1]
    ])

    # Input matrix
    B = np.array([
        [0],
        [0],
        [-(C2 * l1 * m1 * X2 + 2 * C2 * l1 * m2 * X2 - C3 * l2 * m2 * X4 * X6) / 2 / s1],
        [(C3 * l1 * m1 * X2 * X6 - C1 * l2 * m2 * X4 + 2 * C3 * l1 * m2 * X2 * X6) / 2 / s1]
    ])

    # External input matrix
    L = np.array([
        [0],
        [0],
        [(C2 * C4 * X1 - C3 * C5 * X3 * X6) / s1],
        [(C1 * C5 * X3 - C3 * C4 * X1 * X6) / s1]
    ])

    return A, B, L

def mov_eqn_double_pendulum(sys_consts_double, phi_frame, ddq):
    """
    Computes the motion equation for a double pendulum on a cart.

    Parameters:
    - sys_consts_double (tuple): System constants (C1, C2, C3, C4, C5, m1, m2, l1, l2, g).
    - phi_frame (np.array): State of the pendulums [phi1, phi2, dphi1, dphi2].
    - ddq (float): Cart acceleration.

    Returns:
    - np.array: Updated state of the pendulums [dphi1, dphi2, ddphi1, ddphi2].
    """
    # Extract angles and angular velocities from the state frame
    phi1 = phi_frame[0][0]
    phi2 = phi_frame[1][0]
    dphi1 = phi_frame[2][0]
    dphi2 = phi_frame[3][0]

    # Compute trigonometric terms
    X1 = np.sin(phi1) 
    X2 = np.cos(phi1)
    X3 = np.sin(phi2)
    X4 = np.cos(phi2)
    X5 = np.sin(phi1 - phi2)
    X6 = np.cos(phi1 - phi2)

    # Calculate system matrices
    A, B, L = sys_matrices_double_pendulum(sys_consts_double, [X1, X2, X3, X4, X5, X6], dphi1, dphi2)

    # Compute the state derivative
    xdot = np.dot(A, phi_frame) + B * ddq + L
    return xdot
