import numpy as np
from scipy.linalg import solve_discrete_are
from threads_.numsim.libs.state_space_fs.control_tuning.miscs import _calculate_delay_steps, _continuous_to_discrete

def _dlqr_delay_compensation(A_d, B_d, Q, R, delay_steps):
    """
    Compute the discrete LQR gains with delay compensation.

    Parameters:
    A_d (np.ndarray): Discrete-time system matrix.
    B_d (np.ndarray): Discrete-time input matrix.
    Q (np.ndarray): State cost matrix for LQR.
    R (np.ndarray): Control effort cost matrix for LQR.
    delay_steps (int): Number of discrete steps for the delay.

    Returns:
    K (np.ndarray): LQR gain matrix for the original system.
    """
    # Get dimensions
    n_states = A_d.shape[0]
    n_inputs = B_d.shape[1]

    # Extend the state-space for delay
    total_states = n_states + delay_steps * n_inputs
    A_delay = np.zeros((total_states, total_states))
    B_delay = np.zeros((total_states, n_inputs))

    # Fill in the extended A matrix
    A_delay[:n_states, :n_states] = A_d
    if delay_steps > 0:
        A_delay[:n_states, n_states:n_states + n_inputs] = B_d
        if delay_steps > 1:
            A_delay[n_states:n_states + (delay_steps - 1) * n_inputs, n_states + n_inputs:n_states + delay_steps * n_inputs] = np.eye((delay_steps - 1) * n_inputs)

    # Fill in the extended B matrix
    B_delay[n_states + (delay_steps - 1) * n_inputs:, :] = np.eye(n_inputs)

    # Extend Q matrix to match the extended system
    Q_extended = np.zeros((total_states, total_states))
    Q_extended[:n_states, :n_states] = Q

    # Check matrix definiteness
    if not np.all(np.linalg.eigvals(Q_extended) >= 0):
        raise ValueError("Q_extended is not positive semi-definite.")
    if not np.all(np.linalg.eigvals(R) > 0):
        raise ValueError("R is not positive definite.")

    # Solve the discrete Riccati equation for the extended system
    try:
        P = solve_discrete_are(A_delay, B_delay, Q_extended, R)
    except Exception as e:
        raise ValueError(f"Riccati equation solver failed: {e}")

    # Compute the LQR gain matrix for the extended system
    K_extended = np.linalg.inv(R + B_delay.T @ P @ B_delay) @ (B_delay.T @ P @ A_delay)

    # Extract the LQR gain matrix for the original system
    K = K_extended[:, :n_states]

    return K

def lqr_delay_K_calc(A, B, Q, R, T_s, delay):
    """
    Calculate the LQR gain matrix for a system with discrete delay compensation.

    Parameters:
    A (np.ndarray): Continuous-time system matrix.
    B (np.ndarray): Continuous-time input matrix.
    Q (np.ndarray): State cost matrix for LQR. Default: Identity matrix.
    R (np.ndarray): Control cost matrix for LQR. Default: [[1.0]].
    T_s (float): Sampling time for discretization.
    delay (float): Delay in seconds.

    Returns:
    K (np.ndarray): LQR gain matrix with delay compensation.
    """
    # Discretize the system matrices
    A_d, B_d = _continuous_to_discrete(A, B, T_s)

    # Calculate delay steps
    delay_steps = _calculate_delay_steps(delay, T_s)

    # Set default Q and R matrices if not provided
    if Q is None:
        Q = np.eye(4)  # State cost matrix
    if R is None:
        R = np.array([[1.0]])  # Control cost matrix

    # Compute the LQR gain with delay compensation
    try:
        K = _dlqr_delay_compensation(A_d, B_d, Q, R, delay_steps)
        print("LQR Gain Matrix (K):\n", K)
    except ValueError as e:
        print(f"Error: {e}")

    return K
