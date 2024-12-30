# Double Inverted Pendulum on Cart Simulation

## Overview
This folder contains a simulation program for a **double inverted pendulum on a cart**. It is designed to study and analyze the dynamics, control methods, and behavior of this highly non-linear system. The simulation includes various features like:

- **Single and Double Pendulum Modes**
- **Invisible Second Pendulum**
- **Graphical Visualization** using Pygame
- **Simulation Data Recording**
- **Configurable Parameters** via GUI or YAML files
- **PD Controller**
- **Reaction Time Measurement**

The project is modular and provides an easy-to-understand structure for extending functionalities.

---

## Features

1. **Simulation Modes**:
   - Single pendulum on cart
   - Double pendulum on cart

2. **Control Algorithms**:
   - Full state feedback, by specifying a gain matrix

3. **Visualization**:
   - Real-time simulation visualization using Pygame
   - Scalable and configurable rendering options

4. **Data Logging**:
   - Simulation results and control parameters are saved in organized CSV files for further analysis.

5. **User Interaction**:
   - Start/pause simulations with keyboard inputs
   - Adjustable system parameters via GUI or YAML config files

---

## Getting Started

### Prerequisites
Ensure the following dependencies are installed:
- Python 3.8+
- Required Python libraries:
  - `pygame`
  - `numpy`
  - `scipy`
  - `PyYAML`
  - `matplotlib`
  - `pandas`
  - `PyAutoGUI`
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
   cd "./double_inverted_pendulum_simulation_software/Python - Simulation, measurement"
   ```
2. Configure the simulation parameters in `configs/default_parameters.yaml`.
3. Launch the simulation software:
   ```bash
   python run.py
   ```
- Alternatively, you can directly run the precompiled Windows executable located in the `bin` folder.

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

### Configuration File
- `configs/default_parameters.yaml`: Contains all adjustable parameters for the simulation, such as rod lengths, mass, gravity, and control settings.

### Simulation Core
- **`libs/varstructs/SIM_STATE.py`**:
  - Manages the state variables of the simulation, such as the pendulum's position, velocity, and control inputs.

- **`threads_/numsim`**:
  - Implements the numerical simulation logic, including Runge-Kutta methods and cart dynamics.

### Visualization
- **Pygame-based Visualization (`graphics_draw_figure.py`)**:
  - Draws the pendulum, rods, and cart in real-time during simulation.

### Data Logging
- **`output_data_saver.py`**:
  - Handles the saving of simulation data, such as constant parameters, state variables and control inputs.

---

## Usage

### Keyboard Controls
- **`SPACE`**: Start/End the simulation
- **`Q`**: Quit the simulation
- **`F11` or `F`**: Toggle fullscreen mode

### Output Data
Simulation results are saved in the `output_datasets/` folder. Each run creates a timestamped folder containing:
- CSV files with logged data
- YAML configuration files for reproducibility

---

## Troubleshooting

### Common Issues
- **Pygame not launching in fullscreen**: Ensure your monitor configuration matches the settings in `program_config.yaml`.
- **Pygame window does not close**: The Pygame simulation window does not close and becomes unresponsive after finishing the simulation. Unfortunately, this is a known issue with Pygame for which no reliable solution has been found. When this occurs, you need to terminate the entire program manually using the Task Manager.
