import numpy as np
from scipy.linalg import solve_continuous_are
from scipy.integrate import solve_ivp

def riccati_solutions_dpic(A, B, Q, R, t_span):
    """
    Computes solutions for the Algebraic Riccati Equation (ARE) and 
    Differential Riccati Equation (DRE) for a DPIC system.
    
    Parameters:
        A (numpy.ndarray): System dynamics matrix (4x4)
        B (numpy.ndarray): Input matrix (4x1)
        Q (numpy.ndarray): State weighting matrix (4x4)
        R (numpy.ndarray): Input weighting matrix (1x1)
        t_span (tuple): Time span for the DRE solution (start, end)
        
    Returns:
        P_ARE (numpy.ndarray): Solution to the algebraic Riccati equation
        P_t (list of numpy.ndarray): Time-dependent solution of the DRE
        t (numpy.ndarray): Time points corresponding to the DRE solution
        K (numpy.ndarray): State feedback gain matrix
    """
    # Solve the algebraic Riccati equation (ARE)
    P_ARE = solve_continuous_are(A, B, Q, R)
    
    inv_R = np.linalg.inv(np.array([[R]])) 
    # Calculate the optimal feedback gain matrix K
    K = inv_R @ B.T @ P_ARE
    
    # Define the Riccati differential equation (DRE)
    def dre(t, P_flat):
        P = P_flat.reshape(A.shape)  # Reshape to matrix form
        dP_dt = -(P @ A.T + A @ P - P @ B @ inv_R @ B.T @ P + Q)
        return dP_dt.flatten()  # Return as a flattened array

    # Solve the DRE using Runge-Kutta method (solve_ivp)
    P_t1_matrix = np.zeros_like(Q)  # Final condition P(t1)
    P_t1_flat = P_t1_matrix.flatten()
    sol = solve_ivp(dre, [t_span[1], t_span[0]], P_t1_flat, method='RK45', t_eval=np.linspace(t_span[1], t_span[0], 100))
    
    # Reshape the solutions back to matrices
    P_t = [P.reshape(A.shape) for P in sol.y.T]
    
    return P_ARE, P_t, sol.t, K