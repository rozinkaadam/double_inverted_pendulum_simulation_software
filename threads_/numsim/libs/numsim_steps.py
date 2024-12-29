def rk4_step(f, sys_consts, x, u, dt: float):
    """
    Perform a single step of the fourth-order Runge-Kutta (RK4) method for numerical integration.

    Parameters:
    - f (function): The function representing the system's equations of motion.
      It should take the system constants, state vector, and input as arguments.
    - sys_consts (any): Constants required by the system's equations of motion.
    - x (tuple): A tuple where x[0] is the current state of the system (phi_frame_array).
    - u (float): The input to the system (e.g., control force or torque).
    - dt (float): The time step for integration.

    Returns:
    - tuple: A tuple containing:
        - Updated state vector after one RK4 step.
        - The change in the state (dx) over the time step.
    """
    # Extract the state vector from the input tuple
    phi_frame_array = x[0]

    # Compute the four intermediate slopes
    k1 = f(sys_consts, phi_frame_array, u)  # First slope (based on current state)
    k2 = f(sys_consts, phi_frame_array + 0.5 * k1 * dt, u)  # Second slope (midpoint)
    k3 = f(sys_consts, phi_frame_array + 0.5 * k2 * dt, u)  # Third slope (midpoint)
    k4 = f(sys_consts, phi_frame_array + k3 * dt, u)  # Fourth slope (endpoint)

    # Combine the slopes to calculate the state change (weighted average of slopes)
    dx = (k1 + 2 * k2 + 2 * k3 + k4) / 6.0

    # Update the state using the calculated change
    return phi_frame_array + dx * dt, dx
