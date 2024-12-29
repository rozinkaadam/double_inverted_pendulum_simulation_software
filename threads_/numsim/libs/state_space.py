from threads_.numsim.libs.state_space_fs import calc_system_constants as csC
from threads_.numsim.libs.state_space_fs import calc_system_matrices  as csM
from threads_.numsim.libs.state_space_fs.control_tuning import riccati_solution as rs
from threads_.numsim.libs.state_space_fs.control_tuning import h_inf
from threads_.numsim.libs.state_space_fs.control_tuning import h_inf_delay
from threads_.numsim.libs.state_space_fs.control_tuning import lqr_delay
import numpy as np
from scipy.signal import place_poles
import time
from scipy.linalg import eig

class state_space:
    """
    Manages the state-space representation of a double or single inverted pendulum system,
    including system constants, linearization, and control calculations.

    Attributes:
        double_pendulum (bool): Indicates if the system is a double pendulum.
        sample_rate_s (float): Sample rate for numerical integration.
        pd_delay_s (float): PD controller delay in seconds.
        rho1, rho2 (float): Mass density of pendulum rods.
        l1, l2 (float): Lengths of pendulum rods.
        g (float): Gravitational constant.
        C1, C2, C3, C4, C5 (float): System constants for dynamics.
        m1, m2 (float): Masses of pendulum rods.
        A_lin, B_lin (np.ndarray): Linearized state-space matrices.
        desired_poles (list): Desired pole locations for controller design.
        K (np.ndarray): State feedback gain matrix.
        LQR_Q, LQR_R (np.ndarray): LQR weighting matrices.
        report (dict): Contains diagnostic data about the system and controllers.
    """

    def __init__(self, double_pendulum, LQR_Q, LQR_R, sample_rate_s, pd_delay_s) -> None:
        self.double_pendulum = double_pendulum
        self.sample_rate_s = sample_rate_s
        self.pd_delay_s = pd_delay_s

        # System constants
        self.rho1 = None
        self.rho2 = None
        self.l1 = None
        self.l2 = None
        self.g = None

        self.C1 = None
        self.C2 = None
        self.C3 = None
        self.C4 = None
        self.C5 = None
        self.m1 = None
        self.m2 = None

        # Linearization
        self.A_lin = None
        self.B_lin = None

        # Control-related attributes
        self.M = None
        self.desired_poles = [-1, -2, -3, -4]  # Default desired poles
        self.K = None

        # LQR parameters
        self.P_ARE = None
        self.P_t = None
        self.t = None
        self.K_opt = None
        self.LQR_Q = LQR_Q
        self.LQR_R = LQR_R

        # Report structure
        self.report = {
            "timestamp": None,
            "M_rank": None,
            "K_gain": None,
            "LQR_Q": None,
            "LQR_R": None,
            "LQR_P_ARE": None,
            "LQR_K_opt": None,
            "t_span": None,
            "H_inf_K": None,
        }

    def update_system_constants(self, rho1, rho2, l1, l2, g):
        """
        Updates the system constants based on provided parameters.

        Parameters:
            rho1 (float): Mass density of the first rod.
            rho2 (float): Mass density of the second rod.
            l1 (float): Length of the first rod.
            l2 (float): Length of the second rod (None for single pendulum).
            g (float): Gravitational acceleration.
        """
        if l2 is None or l2 == 0:
            self.double_pendulum = False  # Switch to single pendulum mode if l2 is invalid

        self.rho1 = rho1
        self.rho2 = rho2
        self.l1 = l1
        self.l2 = l2
        self.g = g

        self._update_sys_consts()

    def _update_sys_consts(self):
        """
        Internal method to calculate and update system constants based on the current state.
        """
        C1 = None
        C2 = None
        C3 = None
        C4 = None
        C5 = None
        m1 = None
        m2 = None
        l2 = None
        g = None

        if self.double_pendulum:
            # Calculate constants for double pendulum system
            C1, C2, C3, C4, C5, m1, m2, l1, l2, g = csC.calculate_system_constants_double(
                self.rho1, self.rho2, self.l1, self.l2, self.g
            )
        else:
            # Calculate constants for single pendulum system
            C1, C2, m1, l1, g = csC.calculate_system_constants_single(self.rho1, self.l1, self.g)

        # Update attributes
        self.C1 = C1
        self.C2 = C2
        self.C3 = C3
        self.C4 = C4
        self.C5 = C5
        self.m1 = m1
        self.m2 = m2
        self.l1 = l1
        self.l2 = l2
        self.g = g

        self.K_h_inf = None  # Reset H-infinity gain

        self._update__lin_sys_matrices()

    def _update__lin_sys_matrices(self):
        """
        Internal method to update linearized system matrices based on current constants.
        """
        if self.double_pendulum:
            # Compute linearized state-space matrices for double pendulum
            self.A_lin, self.B_lin = csM.linearized_DIPC_sys_matrices(
                (self.C1, self.C2, self.C3, self.C4, self.C5, self.m1, self.m2, self.l1, self.l2, self.g)
            )
            print(f"A_lin: {self.A_lin}")
            print(f"B_lin: {self.B_lin}")
        else:
            # Linearization for single pendulum is not implemented
            pass

    def get_system_constants(self):
        """
        Retrieve the system constants for the pendulum system.

        Returns:
        - Tuple containing constants (C1, C2, C3, C4, C5, m1, m2, l1, l2, g).
        """
        return self.C1, self.C2, self.C3, self.C4, self.C5, self.m1, self.m2, self.l1, self.l2, self.g 

    def get_system_matrices(self, x_list, dphi1, dphi2):
        """
        Get the state-space matrices (A, B, L) for the pendulum system.

        Parameters:
        - x_list (list): A list of state variables such as sin/cos values of angles.
        - dphi1 (float): Angular velocity of the first pendulum.
        - dphi2 (float): Angular velocity of the second pendulum.

        Returns:
        - Tuple (A, B, L): Matrices representing the dynamics of the system, or None for a single pendulum.
        """
        if self.double_pendulum:
            A, B, L = csM.sys_matrices_double_pendulum(
                (self.C1, self.C2, self.C3, self.C4, self.C5, self.m1, self.m2, self.l1, self.l2, self.g),
                x_list, dphi1, dphi2
            )
            return A, B, L
        else:
            return None

    def get_linearized_sys_matrices(self):
        """
        Retrieve the linearized state-space matrices (A, B) for the system.

        Returns:
        - Tuple (A_lin, B_lin): Linearized system matrices.
        """
        return self.A_lin, self.B_lin

    def doReport(self):
        """
        Generate a comprehensive report of the system's state and control properties.
        This includes updating and retrieving system properties, pole placements,
        Riccati solutions, and H-infinity solutions.

        Updates:
        - Eigenvalues and frequencies of A_lin.
        - Controllability matrix (M).
        - Pole placement and feedback gains.
        - Riccati solution.
        - H-infinity controller gains.
        """
        if self.double_pendulum:

            desired_poles = self.desired_poles
            t_span = (0, 10)  # Time span for the DRE solution
            LQR_Q = self.LQR_Q
            LQR_R = self.LQR_R

            # Update system properties and solutions
            self._update_p_of_A()
            self._update_M()
            self._update_K_pole_placed()
            self._update_Riccati_sol(t_span)
            self._update_H_inf()

            # Retrieve updated values for the report
            A_lin, A_lin_eigvals, A_lin_natural_frequencies, A_lin_dominant_frequency = self.get_p_of_A()
            B_lin = self.B_lin
            M, rank_M = self.get_M()
            pole_place_K, riccati_K, cnt_K_H_inf = self.get_K()
            riccati_P_ARE, riccati_P_t, riccati_t, _ = self.get_riccati_sol()
            
            print( "==============================SYSTEM_ANALYSIS_REPORT==============================")           
            print(f"  Samplerate [s]: {self.sample_rate_s}")
            print(f"# Matrix A:")
            print(f"  Linearized A matrix is : \t{A_lin}")
            print(f"  Eigenvalues            : \t{A_lin_eigvals}")
            print(f"# Matrix B:")
            print(f"  Linearized B matrix is : \t{B_lin}")
            print(f"# Matrix M:")
            print(f"  M matrix is   : \t{M}")
            print(f"  Rank of M is  : \t{rank_M}")
            print(f"# Pole replacement:")
            print(f"  Desired poles : \t{desired_poles}")
            print(f"  K matrix      : \t{pole_place_K}")
            print( "# LQR:")            
            print(f"  LQR input Q matrix: \n{LQR_Q}")
            print(f"  LQR input R scalar: \t{LQR_R}")
            print(f"  Algebraic Riccati Solution (P_ARE): \n{riccati_P_ARE}")
            print(f"  Optimal State Feedback Gain Matrix (K_opt): \t{riccati_K}")
            print(f"  Differential Riccati Solutions (P(t)): Computed over time span {t_span}")
            print(f"# H_inf")
            print(f"  K: {cnt_K_H_inf}")
            print( "==================================================================================")   

            self.report = {
                "timestamp"             : time.time(),
                "M_rank"                : rank_M,
                "desired_poles"         : desired_poles,
                "K_gain"                : np.array(pole_place_K),
                "LQR_Q"                 : LQR_Q,
                "LQR_R"                 : LQR_R,
                "LQR_P_ARE"             : riccati_P_ARE,
                "LQR_K_opt"             : np.array(riccati_K),
                "t_span"                : t_span,
                "H_inf_K"               : cnt_K_H_inf
            }

            return self.report

    def _update_p_of_A(self):
        """
        Update eigenvalues and natural frequencies of the linearized system matrix (A_lin).

        This method calculates:
        - The eigenvalues of the A_lin matrix.
        - The natural frequencies (imaginary parts of the eigenvalues).
        - The dominant frequency (maximum natural frequency converted to Hz).
        """
        self.A_lin_eigvals = eig(self.A_lin, left=False, right=False)
        self.A_lin_natural_frequencies = np.imag(self.A_lin_eigvals)
        self.A_lin_dominant_frequency = max(self.A_lin_natural_frequencies) / (2 * np.pi)

    def _update_M(self):
        """
        Compute the controllability matrix (M) and its rank.

        The controllability matrix is constructed as:
        M = [B, AB, A^2B, A^3B]
        If rank(M) equals the state dimension (4 for this system), the system is controllable.
        """
        c_1 = self.B_lin
        c_2 = np.dot(self.A_lin, self.B_lin)
        c_3 = np.dot(self.A_lin, c_2)
        c_4 = np.dot(self.A_lin, c_3)

        self.M = np.hstack((c_1, c_2, c_3, c_4))
        self.M_rank = np.linalg.matrix_rank(self.M)

    def _update_K_pole_placed(self, desired_poles=None):
        """
        Update the state feedback gain matrix using pole placement.

        Parameters:
        - desired_poles (list of float, optional): Desired closed-loop poles.
          If not provided, the existing self.desired_poles will be used.

        Updates:
        - self.cnt_pole_place: Result of the pole placement algorithm.
        """
        if desired_poles is not None:
            self.desired_poles = desired_poles

        result = place_poles(self.A_lin, self.B_lin, self.desired_poles)
        self.cnt_pole_place = result

    def _update_Riccati_sol(self, t_span):
        """
        Solve the Riccati equation for the linearized system over a given time span.

        Parameters:
        - t_span (tuple): Time span for solving the Differential Riccati Equation (DRE).

        Updates:
        - self.cnt_Riccati_sol: Solutions of the Riccati equation and the feedback gain matrix.
        """
        self.cnt_Riccati_sol = rs.riccati_solutions_dpic(self.A_lin, self.B_lin, self.LQR_Q, self.LQR_R, t_span)

    def _update_H_inf(self, gamma=1.0):
        """
        Compute the H-infinity state feedback gain matrix.

        Parameters:
        - gamma (float): Performance threshold for the H-infinity controller.

        Updates:
        - self.cnt_K_H_inf: H-infinity state feedback gain matrix.
        """
        C = np.eye(4)  # Output matrix for full-state feedback
        self.cnt_K_H_inf = h_inf.compute_h_infinity(self.A_lin, self.B_lin, C, gamma)

    def _update_lqr_dd(self):
        """
        Compute the state feedback gain matrix using LQR with delay compensation.

        Uses predefined sampling time and delay values.

        Updates:
        - self.cnt_K_lqr_delay: LQR gain matrix with delay compensation.
        """
        self.cnt_K_lqr_delay = lqr_delay.lqr_delay_K_calc(
            self.A_lin, self.B_lin, self.LQR_Q, self.LQR_R, 0.0166666667, 0.230)

    def get_p_of_A(self):
        """
        Retrieve the linearized system matrix and its eigenvalues and frequencies.

        Returns:
        - A_lin (numpy.ndarray): Linearized system matrix.
        - A_lin_eigvals (numpy.ndarray): Eigenvalues of A_lin.
        - A_lin_natural_frequencies (numpy.ndarray): Natural frequencies of A_lin (imaginary parts of eigenvalues).
        - A_lin_dominant_frequency (float): Dominant natural frequency in Hz.
        """
        return self.A_lin, self.A_lin_eigvals, self.A_lin_natural_frequencies, self.A_lin_dominant_frequency

    def get_M(self):
        """
        Retrieve the controllability matrix and its rank.

        Returns:
        - M (numpy.ndarray): Controllability matrix.
        - rank_M (int): Rank of the controllability matrix.
        """
        return self.M, self.M_rank

    def get_K(self):
        """
        Retrieve the state feedback gain matrices from different methods.

        Returns:
        - pole_place_K (numpy.ndarray): Gain matrix from pole placement.
        - riccati_K (numpy.ndarray): Gain matrix from Riccati equation solution.
        - cnt_K_H_inf (numpy.ndarray): Gain matrix from H-infinity control.
        """
        pole_place_K = self.cnt_pole_place.gain_matrix
        _, _, _, riccati_K = self.get_riccati_sol()

        return pole_place_K, riccati_K, self.cnt_K_H_inf

    def get_riccati_sol(self):
        """
        Retrieve the solutions of the Riccati equation and the feedback gain matrix.

        Returns:
        - P_ARE (numpy.ndarray): Solution to the Algebraic Riccati Equation (ARE).
        - P_t (list of numpy.ndarray): Time-dependent solution of the Differential Riccati Equation (DRE).
        - t (numpy.ndarray): Time points corresponding to the DRE solution.
        - K (numpy.ndarray): State feedback gain matrix from the Riccati solution.
        """
        return self.cnt_Riccati_sol