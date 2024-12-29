def cart_force_single_pendulum(sys_consts_single, dphi1, ddphi1, sin_phi1, cos_phi1, ddq):
    """
    Calculate the force applied to the cart for a single inverted pendulum system.

    Parameters:
    - sys_consts_single (tuple): System constants for the single pendulum (C1, C2, m1, l1, g).
    - dphi1 (float): Angular velocity of the pendulum.
    - ddphi1 (float): Angular acceleration of the pendulum.
    - sin_phi1 (float): Sine of the pendulum angle.
    - cos_phi1 (float): Cosine of the pendulum angle.
    - ddq (float): Linear acceleration of the cart.

    Returns:
    - F_1 (float): Force applied to the cart due to the pendulum dynamics.
    - ddq (float): Linear acceleration of the cart (unchanged).
    """
    # Unpack system constants
    C1, C2, m1, l1, g = sys_consts_single

    # Calculate the force contribution from the single pendulum
    F_1 = (
        m1 * ddq +  # Contribution from the cart's acceleration
        dphi1 * dphi1 * l1 * m1 * sin_phi1 / 2 -  # Centripetal force component
        ddphi1 * l1 * m1 * cos_phi1 / 2  # Tangential force component
    )

    return F_1, ddq  # Return the force and cart acceleration


def cart_force_double_pendulum(sys_consts_double, dphi1, dphi2, ddphi1, ddphi2, sin_phi1, sin_phi2, cos_phi1, cos_phi2, ddq):
    """
    Calculate the force applied to the cart for a double inverted pendulum system.

    Parameters:
    - sys_consts_double (tuple): System constants for the double pendulum (C1, C2, C3, C4, C5, m1, m2, l1, l2, g).
    - dphi1 (float): Angular velocity of the first pendulum.
    - dphi2 (float): Angular velocity of the second pendulum.
    - ddphi1 (float): Angular acceleration of the first pendulum.
    - ddphi2 (float): Angular acceleration of the second pendulum.
    - sin_phi1 (float): Sine of the first pendulum angle.
    - sin_phi2 (float): Sine of the second pendulum angle.
    - cos_phi1 (float): Cosine of the first pendulum angle.
    - cos_phi2 (float): Cosine of the second pendulum angle.
    - ddq (float): Linear acceleration of the cart.

    Returns:
    - F_1 (float): Force applied to the cart due to the dynamics of both pendulums.
    - ddq (float): Linear acceleration of the cart (unchanged).
    """
    # Unpack system constants
    C1, C2, C3, C4, C5, m1, m2, l1, l2, g = sys_consts_double

    # Calculate the force contribution from the double pendulum
    F_1 = (
        (m1 + m2) * ddq -  # Contribution from the cart's acceleration
        (l1 * cos_phi1 * (m1 + 2 * m2)) / 2 * ddphi1 -  # Torque from the first pendulum
        (l2 * m2 * cos_phi2) / 2 * ddphi2 +  # Torque from the second pendulum
        (l1 * sin_phi1 * (m1 + 2 * m2)) / 2 * dphi1 * dphi1 +  # Centripetal force from the first pendulum
        (l2 * m2 * sin_phi2) / 2 * dphi2 * dphi2  # Centripetal force from the second pendulum
    )

    return F_1, ddq  # Return the force and cart acceleration
