import numpy as np

def num_sim_step_pd_tune(sys_consts, x, u, dt: float):
    """
    Performs a single simulation step using the Runge-Kutta 4th order method.

    Args:
        sys_consts (list): System constants for the double pendulum.
        x (np.ndarray): Current state of the system.
        u (float): Control input.
        dt (float): Time step duration.

    Returns:
        tuple: Updated state (np.ndarray) and state derivative (np.ndarray).
    """
    f = _mov_eqn_double_pendulum
    k1 = f(sys_consts, x, u)
    k2 = f(sys_consts, x + 0.5 * k1 * dt, u)
    k3 = f(sys_consts, x + 0.5 * k2 * dt, u)
    k4 = f(sys_consts, x + k3 * dt, u)
      
    dx = (k1 + 2 * k2 + 2 * k3 + k4) / 6.0

    return x + dx * dt, dx

def _sys_matrices_double_pendulum(sys_consts_double, X_list, dphi1, dphi2):
    """
    Computes the system matrices for a double pendulum.

    Args:
        sys_consts_double (list): Constants specific to the double pendulum.
        X_list (list): List of trigonometric values derived from angles.
        dphi1 (float): Angular velocity of the first pendulum.
        dphi2 (float): Angular velocity of the second pendulum.

    Returns:
        tuple: System matrices A, B, and L.
    """
    C1, C2, C3, C4, C5, m1, m2, l1, l2, g = sys_consts_double
    X1, X2, X3, X4, X5, X6 = X_list

    s1 = C3 * C3 * X6 * X6 - C1 * C2

    A = np.array([
        [0, 0, 1, 0],
        [0, 0, 0, 1],
        [0, 0, dphi1 * C3 * C3 * X6 * X5 / s1, dphi2 * C2 * C3 * X5 / s1],
        [0, 0, -dphi1 * C1 * C3 * X5 / s1, -dphi2 * C3 * C3 * X6 * X5 / s1]
    ])

    B = np.array([
        [0],
        [0],
        [-(C2 * l1 * m1 * X2 + 2 * C2 * l1 * m2 * X2 - C3 * l2 * m2 * X4 * X6) / 2 / s1],
        [(C3 * l1 * m1 * X2 * X6 - C1 * l2 * m2 * X4 + 2 * C3 * l1 * m2 * X2 * X6) / 2 / s1]
    ])

    L = np.array([
        [0],
        [0],
        [(C2 * C4 * X1 - C3 * C5 * X3 * X6) / s1],
        [(C1 * C5 * X3 - C3 * C4 * X1 * X6) / s1]
    ])

    return A, B, L

def _mov_eqn_double_pendulum(sys_consts, x, u):
    """
    Computes the motion equations for the double pendulum.

    Args:
        sys_consts (list): Constants specific to the double pendulum.
        x (np.ndarray): Current state of the system.
        u (float): Control input.

    Returns:
        np.ndarray: State derivative.
    """
    phi1 = x[0][0]
    phi2 = x[1][0]
    dphi1 = x[2][0]
    dphi2 = x[3][0]

    X1 = np.sin(phi1)
    X2 = np.cos(phi1)
    X3 = np.sin(phi2)
    X4 = np.cos(phi2)
    X5 = np.sin(phi1 - phi2)
    X6 = np.cos(phi1 - phi2)

    A, B, L = _sys_matrices_double_pendulum(sys_consts, [X1, X2, X3, X4, X5, X6], dphi1, dphi2)

    xdot = np.dot(A, x) + B * u + L
    return xdot
