import time
from threads_.numsim.libs import numsim_steps, move_equations, cart_force
from libs.varstructs.SIM_STATE import SIM_STATE
import numpy as np

def num_sim(double_pendulum, SIM_STATE:SIM_STATE):
    """
    Simulates the motion of a single or double pendulum system on a cart.

    Parameters:
    - double_pendulum (bool): If True, simulates a double pendulum system. Otherwise, simulates a single pendulum.
    - SIM_STATE (SIM_STATE): The current simulation state containing system constants, state variables, and inputs.

    Returns:
    - full_result (list): Contains next state, state derivatives, timestamp, force (F1), and acceleration (ddq).
    """
    # Extract relevant data from the simulation state
    latest_sys_const = SIM_STATE.get_latest_sys_consts()
    dof_state_stack = SIM_STATE.read_DoF_State_Stack()
    q_array_list = SIM_STATE.read_mouse_input("q_array_list")
    num_method = SIM_STATE.SIM_STATE_VAR["simulation_config"]["NUM_METHOD"]
    PD_m_input = SIM_STATE.SIM_STATE_VAR["PD_control"]["PD_MOUSE_INPUT"]
    PD_u_q = SIM_STATE.read_PD_u_q()

    if double_pendulum: 
        # Solve the motion equations for a double pendulum system
        next_x, d_next_x, timestamp = solve_ode(
            move_equations.mov_eqn_double_pendulum, 
            latest_sys_const,
            dof_state_stack,
            q_array_list,
            num_method,
            PD_u_q,
            PD_m_input
        )

        # Calculate the force acting on the cart and the acceleration
        F1, ddq = cart_force.cart_force_double_pendulum(
            latest_sys_const,
            next_x[2][0],
            next_x[3][0],
            d_next_x[2][0],
            d_next_x[3][0],
            np.sin(next_x[0][0]),
            np.sin(next_x[1][0]),
            np.cos(next_x[0][0]),
            np.cos(next_x[1][0]),
            q_array_list[-1][2] + PD_u_q[2]
        )

        full_result = [next_x, d_next_x, timestamp, F1, ddq]

    else:  # Single pendulum
        # Solve the motion equations for a single pendulum system
        next_x, d_next_x, timestamp = solve_ode(
            move_equations.mov_eqn_single_pendulum, 
            latest_sys_const,
            dof_state_stack,
            q_array_list,
            num_method,
            PD_u_q,
            PD_m_input
        )

        # Calculate the force acting on the cart and the acceleration
        F1, ddq = cart_force.cart_force_single_pendulum(
            latest_sys_const,
            next_x[2][0],
            d_next_x[2][0],
            np.sin(next_x[0][0]),
            np.cos(next_x[0][0]),
            q_array_list[-1][2] + PD_u_q[2]
        )

        full_result = [next_x, d_next_x, timestamp, F1, ddq]

    return full_result

def solve_ode(mov_equation, sys_consts, x, q:list, num_method, PD_u_q, PD_m_input):
    """
    Solves the ordinary differential equations (ODEs) for the pendulum system.

    Parameters:
    - mov_equation (function): The motion equation for the pendulum.
    - sys_consts (list): System constants for the pendulum system.
    - x (list): Current state of the system ([phi1, phi2, dphi1, dphi2]).
    - q (list): Input states ([x_m, dx_m, ddx_m, timestamp]).
    - num_method (str): Numerical method to use for solving ODEs (e.g., 'rk4').
    - PD_u_q (list): Control inputs for the system.
    - PD_m_input (bool): Indicates whether PD control is based on mouse input.

    Returns:
    - next_x (np.array): Next state of the system.
    - d_next_x (np.array): Derivatives of the state variables.
    - now_timestamp (float): Current timestamp.
    """
    # Retrieve the last two input states
    q_m2 = q[-2]
    q_m1 = q[-1]

    # Determine the time step (dt)
    prev_timestamp = x[2]
    if prev_timestamp is None:
        prev_timestamp = q_m2[3]
    now_timestamp = time.time()
    dt = now_timestamp - prev_timestamp

    # Extract acceleration input
    ddq = q_m1[2]

    # Include PD control input
    if PD_u_q is not None:
        if PD_m_input:
            ddq += PD_u_q[0]
        else:
            ddq = PD_u_q[0]

    # Solve the ODE using the specified numerical method
    if num_method == 'rk4':
        next_x, d_next_x = numsim_steps.rk4_step(mov_equation, sys_consts, x, ddq, dt)
    else:
        raise ValueError("Unknown method: " + num_method)

    return next_x, d_next_x, now_timestamp