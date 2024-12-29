import numpy as np
from scipy.linalg import solve_discrete_are
from threads_.numsim.libs.state_space_fs.control_tuning.miscs import _calculate_delay_steps, _continuous_to_discrete

def _extend_with_delay(A_d, B_d, delay_steps):
    """
    Extend system matrices to include delay steps.

    Parameters:
    A_d (np.ndarray): Discrete-time system matrix.
    B_d (np.ndarray): Discrete-time input matrix.
    delay_steps (int): Number of discrete delay steps.

    Returns:
    A_ext (np.ndarray): Extended system matrix with delay.
    B_ext (np.ndarray): Extended input matrix with delay.
    """
    n_states = A_d.shape[0]
    n_inputs = B_d.shape[1]
    total_states = n_states + delay_steps * n_inputs

    # Extend A matrix
    A_ext = np.zeros((total_states, total_states))
    A_ext[:n_states, :n_states] = A_d
    A_ext[:n_states, n_states:n_states + n_inputs] = B_d
    if delay_steps > 1:
        A_ext[n_states:n_states + (delay_steps - 1) * n_inputs, n_states + n_inputs:n_states + delay_steps * n_inputs] = np.eye((delay_steps - 1) * n_inputs)

    # Extend B matrix
    B_ext = np.zeros((total_states, n_inputs))
    B_ext[n_states + (delay_steps - 1) * n_inputs:, :] = np.eye(n_inputs)

    return A_ext, B_ext

def _extend_C(C, A_ext_shape, original_state_dim):
    """
    Extend the C matrix to match the dimensions of the extended A matrix.

    Parameters:
    C (np.ndarray): Original output matrix.
    A_ext_shape (tuple): Shape of the extended A matrix.
    original_state_dim (int): Original state dimension.

    Returns:
    C_ext (np.ndarray): Extended C matrix.
    """
    n_rows, _ = C.shape
    total_states = A_ext_shape[0]
    C_ext = np.zeros((n_rows, total_states))
    C_ext[:, :original_state_dim] = C
    return C_ext

def _h_infinity_control(A_d, B_d, C, gamma):
    """
    Compute the H-infinity gain matrix.

    Parameters:
    A_d (np.ndarray): Discrete-time system matrix.
    B_d (np.ndarray): Discrete-time input matrix.
    C (np.ndarray): Output matrix for performance.
    gamma (float): H-infinity performance bound.

    Returns:
    K (np.ndarray): H-infinity gain matrix for the original system.
    """
    n_states = A_d.shape[0]
    n_inputs = B_d.shape[1]

    # Solve the Riccati equation
    try:
        P = solve_discrete_are(A_d, B_d, C.T @ C, gamma**2 * np.eye(n_inputs))
    except Exception as e:
        raise ValueError(f"H-infinity Riccati equation solver failed: {e}")

    # Compute the H-infinity gain
    K = np.linalg.inv(B_d.T @ P @ B_d - gamma**2 * np.eye(n_inputs)) @ (B_d.T @ P @ A_d)

    # Extract relevant part of K for the original state dimensions
    K_relevant = K[:, :4]

    return K_relevant

def h_inf_delay_K_calc(A, B, gamma, T_s, delay):
    C = np.array([[0.01, 0.0, 0.0, 0.0],
                  [0.0, 0.001, 0.0, 0.0]])  # Performance weights

    # Convert to discrete-time
    A_d, B_d = _continuous_to_discrete(A, B, T_s)

    # Calculate delay steps
    delay_steps = _calculate_delay_steps(delay, T_s)

    # Extend system matrices with delay
    A_ext, B_ext = _extend_with_delay(A_d, B_d, delay_steps)

    # Extend C matrix
    C_ext = _extend_C(C, A_ext.shape, A_d.shape[0])

    try:
        K = _h_infinity_control(A_ext, B_ext, C_ext, gamma)
        print("Relevant H-infinity Gain Matrix (K):\n", K)
        return K
    except ValueError as e:
        print(f"Error: {e}")
        return None