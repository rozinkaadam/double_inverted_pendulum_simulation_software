import numpy as np
from scipy.linalg import solve_continuous_are, solve_discrete_are, expm
from scipy.signal import cont2discrete
from scipy.optimize import minimize

def compute_h_infinity_only_one_rod(A, B, delay):
    """
    Compute the H_infinity gains K_p_1 and K_d_1 for a single rod system.

    Parameters:
        A (numpy.ndarray): State matrix.
        B (numpy.ndarray): Input matrix.
        delay (float): System delay in seconds.

    Returns:
        numpy.ndarray: The calculated proportional and derivative gains as a 4x1 array.
    """
    # Reduce the system to a simpler form focusing on (phi1, dphi1)
    reduced_A = np.array([
                    [0, 1],
                    [A[2, 0], 0]
                ])
    reduced_B = np.array([
                    [0],
                    [B[2, 0]]
                ])

    # Compensate for delay using the exponential of the A matrix
    A_delayed = expm(reduced_A * delay)
    B_delayed = np.dot(np.linalg.inv(reduced_A), (A_delayed - np.eye(2))).dot(reduced_B)

    def h_infinity_cost(K):
        """Cost function for H_infinity optimization."""
        K_matrix = np.array([[K[0], K[1]]])
        A_cl = A_delayed - B_delayed @ K_matrix
        eigenvalues = np.linalg.eigvals(A_cl)
        return max(abs(eigenvalues))  # Maximum absolute eigenvalue

    # Optimize using the Nelder-Mead method
    initial_guess = [0.1, 0.1]  # Initial guesses for K_p_1 and K_d_1
    result = minimize(h_infinity_cost, initial_guess, method='Nelder-Mead')

    if not result.success:
        print(f"A_lin: {A}")
        print(f"B_lin: {B}")
        raise ValueError("H_infinity optimization failed.")

    K_p_1, K_d_1 = result.x
    return np.array([[K_p_1], [0], [K_d_1], [0]])

def compute_h_infinity(A, B, C, gamma):
    """
    Compute the H_infinity controller using Riccati equations.

    Parameters:
        A (np.ndarray): State matrix (4x4).
        B (np.ndarray): Input matrix (4x1 or 4xN).
        C (np.ndarray): Output matrix (Mx4).
        gamma (float): H_infinity performance bound.

    Returns:
        np.ndarray: State feedback matrix for the H_infinity controller.
    """
    # Check input matrix dimensions
    if A.shape[0] != A.shape[1] or A.shape[0] != B.shape[0] or A.shape[1] != C.shape[1]:
        raise ValueError("Dimensions of A, B, and C matrices are inconsistent.")

    # Define weighting matrices
    Q = C.T @ C  # Output weighting matrix
    R = gamma**2 * np.eye(B.shape[1])  # Input weighting matrix

    # Solve the Riccati equation
    P = solve_continuous_are(A, B, Q, R)

    # Compute the state feedback matrix
    K = np.linalg.inv(R) @ B.T @ P

    return K

def compute_h_infinity_with_delay(A, B, C, gamma, delay):
    """
    Compute the H_infinity controller with constant delay.

    Parameters:
        A (np.ndarray): State matrix (4x4).
        B (np.ndarray): Input matrix (4x1 or 4xN).
        C (np.ndarray): Output matrix (Mx4).
        gamma (float): H_infinity performance bound.
        delay (float): Delay in seconds (e.g., 0.230).

    Returns:
        np.ndarray: State feedback matrix for the original system.
    """
    # Check input matrix dimensions
    if A.shape[0] != A.shape[1] or A.shape[0] != B.shape[0] or A.shape[1] != C.shape[1]:
        raise ValueError("Dimensions of A, B, and C matrices are inconsistent.")

    # Use Pade approximation for delay (1st order)
    pade_num, pade_den = _pade_approximation(delay, order=1)

    # State-space representation of the delay approximation
    A_delay = np.array([[-pade_den[1]]])
    B_delay = np.array([[1]])
    C_delay = np.array([[pade_num[1]]])
    D_delay = np.array([[pade_num[0]]])

    # Extend the system to include delay
    A_ext = np.block([
        [A, B @ C_delay],
        [np.zeros((1, A.shape[0])), A_delay]
    ])
    B_ext = np.block([
        [B @ D_delay],
        [B_delay]
    ])
    C_ext = np.block([C, np.zeros((C.shape[0], 1))])

    # Define weighting matrices
    Q = C_ext.T @ C_ext  # Output weighting matrix
    R = gamma**2 * np.eye(B_ext.shape[1])  # Input weighting matrix

    # Solve the Riccati equation
    P = solve_continuous_are(A_ext, B_ext, Q, R)

    # Compute the extended state feedback matrix
    K_ext = np.linalg.inv(R) @ B_ext.T @ P

    # Extract the feedback matrix for the original states
    K_original = K_ext[:, :A.shape[0]]

    return K_original

def _discretize_system_alt(A, B, T_s):
    """
    Alternate discretization of the system using scipy's cont2discrete.

    Parameters:
        A (np.ndarray): Continuous-time state matrix.
        B (np.ndarray): Continuous-time input matrix.
        T_s (float): Sampling time in seconds.

    Returns:
        tuple: Discretized state and input matrices (A_d, B_d).
    """
    system = (A, B, np.zeros((B.shape[1], A.shape[0])), 0)
    A_d, B_d, _, _, _ = cont2discrete(system, T_s, method='zoh')
    return A_d, B_d

def _discretize_system(A, B, T_s):
    """
    Discretize the continuous-time system using matrix exponentiation.

    Parameters:
        A (np.ndarray): Continuous-time state matrix.
        B (np.ndarray): Continuous-time input matrix.
        T_s (float): Sampling time in seconds.

    Returns:
        tuple: Discretized state and input matrices (A_d, B_d).
    """
    n = A.shape[0]
    m = B.shape[1]

    # Construct block matrix for exponential computation
    AB = np.block([
        [A, B],
        [np.zeros((m, n + m))]
    ])
    exp_AB = expm(AB * T_s)

    # Extract discrete matrices
    A_d = exp_AB[:n, :n]
    B_d = exp_AB[:n, n:n+m]

    return A_d, B_d

def _pade_approximation(delay, order=1):
    """
    Compute the Pade approximation for modeling delay.

    Parameters:
        delay (float): Delay in seconds.
        order (int): Order of the Pade approximation.

    Returns:
        tuple: Numerator and denominator coefficients of the Pade polynomial.
    """
    n = order
    num = np.zeros(n + 1)
    den = np.zeros(n + 1)
    for k in range(n + 1):
        num[k] = (-1)**k * np.math.comb(n, k)
        den[k] = np.math.comb(n, k)
    num *= delay / 2
    den *= delay / 2
    return num, den

def compute_h_infinity_discrete(A, B, C, gamma, T_s, delay):
    """
    Designs an H-infinity controller in discrete time, considering a given sampling period and delay.

    Parameters:
    - A (np.ndarray): Continuous state matrix.
    - B (np.ndarray): Continuous input matrix.
    - C (np.ndarray): Output matrix.
    - gamma (float): H-infinity performance bound.
    - T_s (float): Sampling time (in seconds).
    - delay (float): Delay time (in seconds).

    Returns:
    - K (np.ndarray): State feedback matrix for the discrete-time controller.
    """
    # Discretize the continuous system matrices.
    A_d, B_d = _discretize_system(A, B, T_s)

    # Model the delay.
    delay_steps = int(delay / T_s)  # Number of delay steps.
    if delay_steps > 0:
        A_delay = np.eye(delay_steps)
        B_delay = np.zeros((delay_steps, 1))
        C_delay = np.zeros((1, delay_steps))
        C_delay[0, -1] = 1

        # Extend the discrete-time system with delay dynamics.
        A_d_ext = np.block([
            [A_d, B_d @ C_delay],
            [np.zeros((delay_steps, A_d.shape[1])), A_delay]
        ])
        B_d_ext = np.block([
            [B_d @ np.zeros((1, 1))],
            [np.eye(delay_steps, 1)]
        ])
        C_d_ext = np.block([C, np.zeros((C.shape[0], delay_steps))])
    else:
        # No delay, use original matrices.
        A_d_ext = A_d
        B_d_ext = B_d
        C_d_ext = C

    # Weighting matrices for H-infinity design.
    Q = C_d_ext.T @ C_d_ext
    R = gamma**2 * np.eye(B_d_ext.shape[1])

    # Debugging checks for definiteness of weighting matrices.
    print("Q positive definite:", np.all(np.linalg.eigvals(Q) > 0))
    print("R positive definite:", np.all(np.linalg.eigvals(R) > 0))

    # Solve the discrete Riccati equation.
    P = solve_discrete_are(A_d_ext, B_d_ext, Q, R)

    # Compute the state feedback matrix.
    K = np.linalg.inv(B_d_ext.T @ P @ B_d_ext + R) @ (B_d_ext.T @ P @ A_d_ext)

    return K

def compute_h_infinity_discrete_with_checks(A, B, C, gamma, T_s, delay):
    """
    Designs an H-infinity controller with additional checks for numerical stability.

    Parameters:
    - A (np.ndarray): Continuous state matrix.
    - B (np.ndarray): Continuous input matrix.
    - C (np.ndarray): Output matrix.
    - gamma (float): H-infinity performance bound.
    - T_s (float): Sampling time (in seconds).
    - delay (float): Delay time (in seconds).

    Returns:
    - K (np.ndarray): State feedback matrix for the discrete-time controller.
    """
    # Discretize the system matrices using an alternative method.
    A_d, B_d = _discretize_system_alt(A, B, T_s)

    # Model the delay.
    delay_steps = int(delay / T_s)  # Number of delay steps.
    if delay_steps > 0:
        A_delay = np.eye(delay_steps)
        B_delay = np.zeros((delay_steps, 1))
        C_delay = np.zeros((1, delay_steps))
        C_delay[0, -1] = 1

        # Extend the discrete-time system with delay dynamics.
        A_d_ext = np.block([
            [A_d, B_d @ C_delay],
            [np.zeros((delay_steps, A_d.shape[1])), A_delay]
        ])
        B_d_ext = np.block([
            [B_d @ np.zeros((1, 1))],
            [np.eye(delay_steps, 1)]
        ])
        C_d_ext = np.block([C, np.zeros((C.shape[0], delay_steps))])
    else:
        # No delay, use original matrices.
        A_d_ext = A_d
        B_d_ext = B_d
        C_d_ext = C

    # Weighting matrices for H-infinity design with numerical stabilization.
    Q = C_d_ext.T @ C_d_ext
    epsilon = 1e-6  # Small stabilizing factor.
    Q += epsilon * np.eye(Q.shape[0])  # Ensure positive definiteness.
    R = gamma**2 * np.eye(B_d_ext.shape[1])

    # Debugging checks for definiteness of weighting matrices.
    print("Q positive definite:", np.all(np.linalg.eigvals(Q) > 0))
    print("R positive definite:", np.all(np.linalg.eigvals(R) > 0))

    # Solve the discrete Riccati equation.
    P = solve_discrete_are(A_d_ext, B_d_ext, Q, R)

    # Compute the state feedback matrix.
    K = np.linalg.inv(B_d_ext.T @ P @ B_d_ext + R) @ (B_d_ext.T @ P @ A_d_ext)

    return K