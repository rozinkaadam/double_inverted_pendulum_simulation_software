import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def play_animation(data, Kp, Kd, l1, l2, simTs):
    """
    Plays an animation of the double pendulum simulation based on the provided data.

    Args:
        data (list): Simulation data containing angles and timestamps.
        Kp (float): Proportional gain.
        Kd (float): Derivative gain.
        l1 (float): Length of the first rod.
        l2 (float): Length of the second rod.
        simTs (float): Simulation timestep.
    """
    # Extract angles and timestamps
    angles_and_times = [(entry[0][0][0], entry[0][1][0], entry[3]) for entry in data]
    lm = l1 + l2

    # Create figure for the animation
    fig, ax = plt.subplots()
    ax.set_xlim(-lm, lm)
    ax.set_ylim(0, lm)
    ax.set_aspect('equal')

    line1, = ax.plot([], [], 'o-', lw=2)
    line2, = ax.plot([], [], 'o-', lw=2)
    line3, = ax.plot([], [], '-', lw=1, color='gray')

    # Add text for the timestamp
    timestamp_text = ax.text(-lm * 0.8, lm * 0.8, '', fontsize=12, color='black')

    def init():
        """Initialize the animation."""
        line1.set_data([], [])
        line2.set_data([], [])
        line3.set_data([], [])
        timestamp_text.set_text('')
        return line1, line2, line3, timestamp_text

    def update(frame):
        """Update function for the animation."""
        theta1, theta2, timestamp = angles_and_times[frame]

        # Calculate positions
        x1 = l1 * np.sin(theta1)
        y1 = l1 * np.cos(theta1)

        x2 = x1 + l2 * np.sin(theta2)
        y2 = y1 + l2 * np.cos(theta2)

        # Update lines
        line1.set_data([0, x1], [0, y1])
        line2.set_data([x1, x2], [y1, y2])
        line3.set_data([0, 0], [0, l1 + l2])

        # Update timestamp text
        timestamp_text.set_text(f'Kp: {Kp} Kd: {Kd} \nTime: {timestamp:.2f} s')
        return line1, line2, line3, timestamp_text

    ani = FuncAnimation(fig, update, frames=len(angles_and_times), init_func=init, blit=False, interval=1000 * simTs)

    plt.show()
