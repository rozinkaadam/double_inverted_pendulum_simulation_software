import numpy as np
from scipy.linalg import expm

def _continuous_to_discrete(A, B, T_s):
    """
    Convert continuous-time system matrices (A, B) to discrete-time (A_d, B_d).

    Parameters:
    A (np.ndarray): Continuous-time system matrix.
    B (np.ndarray): Continuous-time input matrix.
    T_s (float): Sampling time.

    Returns:
    A_d (np.ndarray): Discrete-time system matrix.
    B_d (np.ndarray): Discrete-time input matrix.
    """
    n_states = A.shape[0]
    aug_matrix = np.zeros((n_states + B.shape[1], n_states + B.shape[1]))
    aug_matrix[:n_states, :n_states] = A
    aug_matrix[:n_states, n_states:] = B
    exp_aug = expm(aug_matrix * T_s)
    A_d = exp_aug[:n_states, :n_states]
    B_d = exp_aug[:n_states, n_states:]
    return A_d, B_d

def _calculate_delay_steps(delay, T_s):
    """
    Calculate the number of delay steps based on delay and sampling time.

    Parameters:
    delay (float): Time delay (in seconds).
    T_s (float): Sampling time (in seconds).

    Returns:
    int: Number of discrete delay steps.
    """
    return int(np.ceil(delay / T_s))