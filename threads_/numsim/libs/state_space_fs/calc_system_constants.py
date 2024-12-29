def calculate_system_constants_single(rho, L1, g):
    """
    Calculate the system constants for a single pendulum.

    Parameters:
    - rho (float): Linear mass density of the pendulum (mass per unit length).
    - L1 (float): Length of the pendulum rod.
    - g (float): Gravitational acceleration.

    Returns:
    - C1 (float): Inverse of the pendulum's effective length for dynamic calculations.
    - C2 (float): Gravitational constant scaled by C1.
    - m1 (float): Total mass of the pendulum.
    - L1 (float): Length of the pendulum rod (unchanged).
    - g (float): Gravitational acceleration (unchanged).
    """
    C1 = 3 / (2 * L1)  # Effective length-based constant for dynamics.
    C2 = g * C1        # Gravity-scaled dynamic constant.

    m1 = L1 * rho       # Total mass of the pendulum based on its length and density.

    return C1, C2, m1, L1, g

def calculate_system_constants_double(rho1, rho2, l1, l2, g):
    """
    Calculate the system constants for a double pendulum.

    Parameters:
    - rho1 (float): Linear mass density of the first rod (mass per unit length).
    - rho2 (float): Linear mass density of the second rod (mass per unit length).
    - l1 (float): Length of the first rod.
    - l2 (float): Length of the second rod.
    - g (float): Gravitational acceleration.

    Returns:
    - C1 (float): Effective inertia constant for the first pendulum.
    - C2 (float): Effective inertia constant for the second pendulum.
    - C3 (float): Coupling constant between the two pendulum rods.
    - C4 (float): Gravity-related constant for the first pendulum.
    - C5 (float): Gravity-related constant for the second pendulum.
    - m1 (float): Mass of the first pendulum rod.
    - m2 (float): Mass of the second pendulum rod.
    - l1 (float): Length of the first pendulum rod (unchanged).
    - l2 (float): Length of the second pendulum rod (unchanged).
    - g (float): Gravitational acceleration (unchanged).
    """
    # Compute the masses of each rod based on their lengths and densities.
    m1 = l1 * rho1
    m2 = l2 * rho2

    # Moments of inertia for each rod (about their centers of mass).
    I_S1 = m1 * l1 * l1 / 12
    I_S2 = m2 * l2 * l2 / 12

    # Compute the constants related to dynamics and gravity.
    C1 = I_S1 + l1 * l1 * (m1 / 4 + m2)  # Effective inertia for the first rod.
    C2 = I_S2 + l2 * l2 * (m2 / 4)       # Effective inertia for the second rod.
    C3 = l1 * l2 * m2 / 2                # Coupling constant.
    C4 = -g * l1 * (m1 / 2 + m2)         # Gravity effect for the first pendulum.
    C5 = -g * l2 * m2 / 2                # Gravity effect for the second pendulum.

    return C1, C2, C3, C4, C5, m1, m2, l1, l2, g
