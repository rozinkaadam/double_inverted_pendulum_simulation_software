# Double Inverted Pendulum on Cart Simulation

## Overview
This repository contains a simulation program for a **double inverted pendulum on a cart**. It is designed to study and analyze the dynamics, control methods, and behavior of this highly non-linear system. The simulation includes various features like:

- **Single and Double Pendulum Modes**
- **Numerical Solvers** (e.g., RK4)
- **State-Space Control Methods**: LQR, \( H_\infty \), Pole Placement
- **Graphical Visualization** using Pygame
- **Simulation Data Logging**
- **Configurable Parameters** via YAML files

The project is modular and provides an easy-to-understand structure for extending functionalities.

---

## Features

1. **Simulation Modes**:
   - Single pendulum on cart
   - Double pendulum on cart

2. **Control Algorithms**:
   - LQR (Linear Quadratic Regulator) with delay compensation
   - \( H_\infty \) control with and without delay
   - Pole placement

3. **Visualization**:
   - Real-time simulation visualization using Pygame
   - Scalable and configurable rendering options

4. **Data Logging**:
   - Simulation results and control parameters are saved in organized CSV files for further analysis.

5. **User Interaction**:
   - Start/pause simulations with keyboard inputs
   - Adjustable system parameters via YAML config files

---

## Getting Started

### Prerequisites
Ensure the following dependencies are installed:
- Python 3.8+
- Required Python libraries:
  - `pygame`
  - `numpy`
  - `scipy`
  - `pyyaml`
  - `screeninfo`
  - `pywin32` (Windows-specific for display handling)

You can install dependencies using:
```bash
pip install -r requirements.txt
```

### Running the Program
1. Clone this repository:
   ```bash
   git clone https://github.com/your-repo-name.git
   cd your-repo-name
   ```
2. Configure the simulation parameters in `configs/default_parameters.yaml`.
3. Run the simulation:
   ```bash
   python run.py
   ```

---

## Directory Structure

```plaintext
.
├── config_gui/                   # GUI-related configurations
│   ├── config_settings_gui.py   # GUI for adjusting simulation settings
│   ├── reaction_time_gui.py     # Reaction time measurement tool
│
├── configs/                     # Configuration files
│   └── default_parameters.yaml  # Default parameters for the simulation
│
├── libs/                        # Core utility libraries
│   ├── varstructs/              # Data structure utilities
│   │   ├── SIM_STATE.py         # Main simulation state structure
│   ├── get_dpi_scaling.py       # DPI scaling detection
│   ├── pointer_enhance.py       # Mouse pointer control
│   ├── set_displays.py          # Display management
│
├── output_datasets/             # Saved simulation results (auto-generated)
│
├── PD_Tuning/                   # Tools for tuning PD controllers
│   └── CPU_Iterative_Tuning/    # CPU-based PD tuning modules
│
├── threads_/                    # Threads for different simulation components
│   ├── diag/                    # Diagnostics tools
│   ├── numsim/                  # Numerical simulation logic
│   ├── simgui/                  # Graphical interface for the simulation
│
├── init_program.py              # Program initializer
├── init_simulation.py           # Simulation initializer
├── program_config.yaml          # Main program configuration file
├── run.py                       # Main entry point for the simulation
```

---

## Key Components

### Configuration Files
- `configs/default_parameters.yaml`: Contains all adjustable parameters for the simulation, such as rod lengths, mass, gravity, and control settings.
- `program_config.yaml`: High-level settings for initializing the program.

### Simulation Core
- **`libs/varstructs/SIM_STATE.py`**:
  - Manages the state variables of the simulation, such as the pendulum's position, velocity, and control inputs.

- **`threads_/numsim`**:
  - Implements the numerical simulation logic, including Runge-Kutta methods and cart dynamics.

### Control Algorithms
- **LQR (`lqr_delay.py`)**:
  - Implements Linear Quadratic Regulator control with delay compensation.
- **\( H_\infty \) Control (`h_inf.py`, `h_inf_delay.py`)**:
  - Implements robust \( H_\infty \) control methods.
- **Pole Placement (`riccati_solution.py`)**:
  - Designs feedback controllers using pole placement methods.

### Visualization
- **Pygame-based Visualization (`graphics_draw_figure.py`)**:
  - Draws the pendulum, rods, and cart in real-time during simulation.

### Data Logging
- **`output_data_saver.py`**:
  - Handles the saving of simulation data, such as state variables, control inputs, and results.

---

## Usage

### Keyboard Controls
- **`SPACE`**: Start/Pause the simulation
- **`Q`**: Quit the simulation
- **`F11` or `F`**: Toggle fullscreen mode

### Configuring Parameters
Edit `configs/default_parameters.yaml` to modify:
- Rod lengths, masses, and gravity
- Control parameters (e.g., PD, LQR gains)
- Numerical method (RK4, Euler)

### Output Data
Simulation results are saved in the `output_datasets/` folder. Each run creates a timestamped folder containing:
- CSV files with logged data
- YAML configuration files for reproducibility

---

## Examples
### Single Pendulum
1. Set `DOUBLE_PENDULUM: False` in `default_parameters.yaml`.
2. Run the program.

### Double Pendulum with LQR Control
1. Set `DOUBLE_PENDULUM: True` and enable `PD_CONTROL_ON`.
2. Adjust LQR parameters in `default_parameters.yaml` under `PD_control`.
3. Run the program.

---

## Troubleshooting

### Common Issues
- **Pygame not launching in fullscreen**: Ensure your monitor configuration matches the settings in `program_config.yaml`.
- **Simulation not starting**: Ensure that all dependencies are installed and the configuration files are properly set.

### Logs
All runtime logs are displayed in the terminal. For debugging, check the `output_datasets/` folder for saved logs and data.

---

## Contributing
Feel free to submit pull requests or report issues. Contributions are welcome to improve the program's functionality, stability, and documentation.

---

## License
This project is licensed under the MIT License.

---

## Acknowledgments
This project was created to study the dynamics and control of double inverted pendulums. Special thanks to all contributors and libraries used in this project.
