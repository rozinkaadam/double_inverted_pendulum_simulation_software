import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Pool
import num_sim_for_tune
import pickle
from pathlib import Path
import csv
import random

def check_matrix_shape(matrix: np.ndarray, n: int, m: int):
    """
    Checks if the provided numpy matrix has dimensions n x m.

    Args:
        matrix (np.ndarray): The matrix to check.
        n (int): Expected number of rows.
        m (int): Expected number of columns.

    Raises:
        AssertionError: If the matrix shape does not match the expected dimensions.
    """
    assert isinstance(matrix, np.ndarray), "The input is not a numpy array!"
    assert matrix.shape == (n, m), f"Matrix shape is not {n}x{m}, but {matrix.shape}, matrix content: {matrix}!"

def _PD_CL_Simulator(args):
    """
    Simulates the PD control loop for a single parameter combination.

    Args:
        args (tuple): Contains simulation parameters such as initial state, system constants, gains, delay, timestep, and more.

    Returns:
        tuple: Contains K_p, K_d, simulation data, and finish flag.
    """
    x_0, sys_consts, K_p, K_d, delay, Ts, run_time, max_angle_rad, total_iterations, iteration = args
    
    data_stream = []
    n = round(run_time / Ts)
    next_x = x_0
    delay_in_frames = round(delay / Ts)
    finish_flag = True
    ddq_stack = [0] * delay_in_frames
    time_c = 0

    for i in range(n):
        phi_1 = next_x[0][0]
        if abs(phi_1) > max_angle_rad:
            finish_flag = False
            break
        
        ddq = -(K_p * phi_1 + K_d * next_x[2][0])
        ddq_stack.append(ddq)
        u = ddq_stack[-(1 + delay_in_frames)]

        rnd_ts = random.uniform(Ts - 0.000594788871006088, Ts + 0.000594788871006088)
        next_x, d_next_x = num_sim_for_tune.num_sim_step_pd_tune(sys_consts, next_x, u, rnd_ts)
        
        check_matrix_shape(next_x, 4, 1)

        time_c += rnd_ts
        data_stream.append([next_x, d_next_x, u, time_c])
    
    percentage = round(iteration / (total_iterations / 7) * 10000) / 100
    
    if finish_flag:
        print(f"> Pass combination {iteration}/{total_iterations}: K_p={K_p:.2f}, K_d={K_d:.2f};")
    else:
        if iteration < (total_iterations / 7):
            if iteration % (round(total_iterations**0.5) + 1) == 0:
                print(f"Status: {percentage}%")

    return K_p, K_d, data_stream, finish_flag

def _iterate_in_range(x_0, sys_consts, Kp_phi1_range, Kd_phi1_range, delay, Ts, run_time, max_angle_rad, usable_cores_array):
    """
    Iterates over a range of K_p and K_d values, distributing simulations across multiple CPU cores.

    Args:
        x_0 (np.ndarray): Initial state of the system.
        sys_consts (np.ndarray): System constants.
        Kp_phi1_range (list): Range of K_p values.
        Kd_phi1_range (list): Range of K_d values.
        delay (float): Control loop delay.
        Ts (float): Timestep of the simulation.
        run_time (float): Duration of the simulation.
        max_angle_rad (float): Maximum allowable angle in radians.
        usable_cores_array (np.ndarray): Boolean array indicating usable CPU cores.

    Returns:
        list: Results of the simulations.
    """
    args_list = []
    total_iterations = len(Kp_phi1_range) * len(Kd_phi1_range)
    iteration = 0
    for Kp_phi1 in Kp_phi1_range:
        for Kd_phi1 in Kd_phi1_range:
            iteration += 1
            args_list.append((x_0, sys_consts, Kp_phi1, Kd_phi1, delay, Ts, run_time, max_angle_rad, total_iterations, iteration))

    usable_cores = np.count_nonzero(usable_cores_array)
    print(f"Evaluating {len(args_list)} combinations using {usable_cores} CPUs.")

    with Pool(processes=usable_cores) as pool:
        chunk_size = len(args_list) // (usable_cores or 1)
        results = pool.map(_PD_CL_Simulator, args_list, chunksize=chunk_size)

    return results

def M_data_iterate(M_data, x_0, usable_cores_array, Ts=1 / 60):
    """
    Iterates simulations over parameter ranges specified in the M_data structure.

    Args:
        M_data (dict): Dictionary containing simulation configuration.
        x_0 (np.ndarray): Initial state of the system.
        usable_cores_array (np.ndarray): Boolean array of usable CPU cores.
        Ts (float): Timestep of the simulation.

    Returns:
        list: Results of the simulations.
    """
    sys_consts_double = M_data["sys_consts_double"]
    delay = M_data["delay"]
    Kp_phi1_range = M_data["Kp_phi1_range"]
    Kd_phi1_range = M_data["Kd_phi1_range"]
    run_time = M_data["run_time"]
    max_rad = M_data["max_deg"] * 0.01745329252

    runs = _iterate_in_range(x_0, sys_consts_double, Kp_phi1_range, Kd_phi1_range, delay, Ts, run_time, max_rad, usable_cores_array)
    return runs

def calc_PD_scores(runs, simTs):
    """
    Calculates evaluation scores for the PD controller based on simulation runs.

    Args:
        runs (list): Simulation results.
        simTs (float): Simulation timestep.

    Returns:
        list: Sorted evaluation scores and associated data streams.
    """
    with_eval_scores = []

    for Kp_phi1, Kd_phi1, data_stream, finish_flag in runs:
        phi1_square_sum = 0
        for next_x, d_next_x, u, t in data_stream:
            phi1_square_sum += next_x[0][0]**2

        with_eval_scores.append([Kp_phi1, Kd_phi1, len(data_stream) * simTs, finish_flag, phi1_square_sum / len(data_stream), data_stream])

    valid_results_data = [
        {
            "Kp_phi1": res[0],
            "Kd_phi1": res[1],
            "time": res[2],
            "finish_flag": res[3],
            "phi1_square_sum": res[4],
            "data_stream": res[5],
        }
        for res in with_eval_scores
    ]
    valid_results_data_sorted = sorted(valid_results_data, key=lambda x: x["phi1_square_sum"])
    return valid_results_data_sorted

def plot_PD_plane(runs_s, D_cor_P, D_cor_D, a, tau):
    """
    Plots the PD plane and parameterized D-curve.

    Args:
        runs_s (list): Sorted simulation results.
        D_cor_P (float): Scaling factor for P-axis.
        D_cor_D (float): Scaling factor for D-axis.
        a (float): System parameter for stability.
        tau (float): Time delay.
    """
    hline_value = a * tau
    vline_value = a

    Kp_phi1 = [res["Kp_phi1"] for res in runs_s]
    Kd_phi1 = [res["Kd_phi1"] for res in runs_s]
    finflags = [res["finish_flag"] for res in runs_s]
    phi1_square_sum = [res["phi1_square_sum"] for res in runs_s]

    om = np.linspace(0.01, 100, 1000)
    S_y = D_cor_D
    S_x = D_cor_P
    p = S_x * ((a + om**2) * np.cos(om * tau) - a) + a
    d = S_y * ((a + om**2) / om * np.sin(om * tau) - a * tau) + a * tau

    fig, ax = plt.subplots(figsize=(8, 6))

    Kp_filled = [Kp for Kp, flag in zip(Kp_phi1, finflags) if flag]
    Kd_filled = [Kd for Kd, flag in zip(Kd_phi1, finflags) if flag]
    phi1_filled = [phi1 for phi1, flag in zip(phi1_square_sum, finflags) if flag]

    Kp_unfilled = [Kp for Kp, flag in zip(Kp_phi1, finflags) if not flag]
    Kd_unfilled = [Kd for Kd, flag in zip(Kd_phi1, finflags) if not flag]
    phi1_unfilled = [phi1 for phi1, flag in zip(phi1_square_sum, finflags) if not flag]

    sc_filled = ax.scatter(Kp_filled, Kd_filled, c=phi1_filled, cmap='viridis_r', s=50, marker='o', label='Successful')
    sc_unfilled = ax.scatter(Kp_unfilled, Kd_unfilled, c=phi1_unfilled, cmap='viridis_r', s=50, marker='x', label='Failed')

    plt.colorbar(sc_filled, ax=ax, label=r'$\phi1\_square\_sum$')

    if hline_value is not None:
        ax.axhline(y=hline_value, color='red', linestyle='--', label=f'Horizontal line: {hline_value}')
    if vline_value is not None:
        ax.axvline(x=vline_value, color='blue', linestyle='--', label=f'Vertical line: {vline_value}')

    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()

    ax.plot(p, d, color='black', linestyle='-', linewidth=2, label='Parameterized curve', zorder=-1, alpha=0.7)

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    ax.set_xlabel(r'$p$ (P-axis)')
    ax.set_ylabel(r'$d$ (D-axis)')
    ax.set_title('PD Plane and D-Curve')

    ax.grid(True)
    plt.show()

def save_runs_to_file(run_struct, path: Path):
    """
    Saves simulation runs to a pickle file.

    Args:
        run_struct (list): Simulation results to save.
        path (Path): Path to save the file.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'wb') as f:
        pickle.dump(run_struct, f)
    print(f"Data saved to {path}.")

def load_runs_from_file(path: Path):
    """
    Loads simulation runs from a pickle file.

    Args:
        path (Path): Path to the file.

    Returns:
        list: Loaded simulation runs.
    """
    with open(path, 'rb') as f:
        loaded_arrays = pickle.load(f)
        print(f"Data loaded from {path} successfully.")
        return loaded_arrays

def save_results_to_file(ordered_results, title):
    """
    Saves ordered simulation results to a CSV file.

    Args:
        ordered_results (list): Ordered simulation results.
        title (str): Title of the file.
    """
    ordered_results.to_csv(f"{title}.csv", index=False)
    print(f"Results saved to '{title}.csv'.")

def save_a_run_to_file(data, title):
    """
    Saves a single simulation run to a CSV file.

    Args:
        data (dict): Simulation run data.
        title (str): Title of the file.
    """
    with open(f"{title}.csv", mode="w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow(["Kp_phi1", "Kd_phi1", "time", "finish_flag", "phi1_square_sum"])
        writer.writerow([
            data["Kp_phi1"],
            data["Kd_phi1"],
            data["time"],
            data["finish_flag"],
            data["phi1_square_sum"],
        ])

        for stream in data["data_stream"]:
            row = [
                *stream[0],
                *stream[1],
                stream[2],
                stream[3]
            ]
            writer.writerow(row)

    print(f"Results saved to '{title}.csv'.")
