import matplotlib.pyplot as plt
import numpy as np
import matplotlib.gridspec as gridspec

def plot_PD_planes(data_list, params_list, plot_titles=None, filename="combined_plot.eps"):
    """
    Generates multiple PD plots side-by-side with a shared color scale and fixed axis limits.

    Args:
        data_list (list): List of datasets (each dataset corresponds to one subplot).
        params_list (list): List of tuples, each containing (D_cor_P, D_cor_D, a, tau) for a subplot.
        plot_titles (list, optional): Titles for each subplot.
        filename (str): Output filename for saving the plot.
    """
    num_plots = len(data_list)

    # GridSpec creation, reserving space for the colorbar
    fig = plt.figure(figsize=(15, 5))
    gs = gridspec.GridSpec(1, num_plots + 1, width_ratios=[1] * num_plots + [0.05])

    # Normalize the color scale
    norm = plt.Normalize(
        0,
        max(
            max(res["phi1_square_sum"]**0.5 for res in dataset) 
            for dataset in data_list
        )
    )
    cmap = 'viridis_r'

    # Global axis limits based on all points
    global_x_min, global_x_max = float('inf'), float('-inf')
    global_y_min, global_y_max = float('inf'), float('-inf')

    for runs_s in data_list:
        Kp_phi1 = [res["Kp_phi1"] for res in runs_s]
        Kd_phi1 = [res["Kd_phi1"] for res in runs_s]
        global_x_min = min(global_x_min, min(Kp_phi1))
        global_x_max = max(global_x_max, max(Kp_phi1))
        global_y_min = min(global_y_min, min(Kd_phi1))
        global_y_max = max(global_y_max, max(Kd_phi1))

    # Add margins to the axes
    margin_x = 0.05 * (global_x_max - global_x_min)
    margin_y = 0.05 * (global_y_max - global_y_min)
    global_x_min -= margin_x
    global_x_max += margin_x
    global_y_min -= margin_y
    global_y_max += margin_y

    # Draw subplots
    axs = []
    for i, (runs_s, params) in enumerate(zip(data_list, params_list)):
        D_cor_P, D_cor_D, a, tau = params
        om = np.linspace(0.01, 100, 1000)
        S_y = D_cor_D
        S_x = D_cor_P
        p = S_x * ((a + om**2) * np.cos(om * tau) - a) + a
        d = S_y * ((a + om**2) / om * np.sin(om * tau) - a * tau) + a * tau

        ax = fig.add_subplot(gs[0, i])
        axs.append(ax)

        Kp_phi1 = [res["Kp_phi1"] for res in runs_s]
        Kd_phi1 = [res["Kd_phi1"] for res in runs_s]
        finflags = [res["finish_flag"] for res in runs_s]
        phi1_square_sum = [res["phi1_square_sum"] for res in runs_s]

        # Separate successful and failed points
        Kp_filled = [Kp for Kp, flag in zip(Kp_phi1, finflags) if flag]
        Kd_filled = [Kd for Kd, flag in zip(Kd_phi1, finflags) if flag]
        phi1_filled = [phi1**0.5 for phi1, flag in zip(phi1_square_sum, finflags) if flag]

        sc = ax.scatter(Kp_filled, Kd_filled, c=phi1_filled, cmap=cmap, s=50, norm=norm)

        # Add the parametric curve (may extend beyond plot bounds)
        ax.plot(p, d, color='black', linestyle='-', linewidth=2, alpha=0.7)

        # Apply global axis limits
        ax.set_xlim(global_x_min, global_x_max)
        ax.set_ylim(global_y_min, global_y_max)

        # Set subplot title
        title = plot_titles[i] if plot_titles and i < len(plot_titles) else f'Plot {i+1}'
        ax.set_title(title)

        ax.set_xlabel(r'$P$')
        ax.grid(True)

    # Add a shared colorbar in the last column
    cbar_ax = fig.add_subplot(gs[0, -1])
    cbar = fig.colorbar(sc, cax=cbar_ax)
    cbar.set_label(r'$\varphi$ RMSD')

    axs[0].set_ylabel(r'$D$')

    plt.tight_layout()
    plt.savefig(filename, format='eps', dpi=300)
    plt.show()
