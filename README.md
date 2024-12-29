# Double Inverted Pendulum on a Cart Simulation and Analysis

This private repository contains the simulation program developed for my BSc thesis in Mechatronics Engineering at the Budapest University of Technology and Economics. The simulation program investigates human balancing using a virtual double inverted pendulum system mounted on a horizontally guided cart.

## Repository Structure

### 1. Python - Simulation, Measurement
This folder contains Python scripts and tools for simulating the dynamics of the double inverted pendulum system and measuring user interactions. Key features include:

- **Simulation**: Implements numerical solvers for system dynamics.
- **Measurement**: Captures human interaction data and evaluates system response.
- **Graphical User Interface**: Allows configuration of simulation parameters, live visualization, and reaction time testing.

For more details, see the `README.md` in the Python folder.

### 2. MATLAB - Model Prescription, Data Evaluation
This folder contains MATLAB scripts and functions for modeling the DIPC system and evaluating measurement results. Key features include:

- **Model Equations**: Scripts for deriving and linearizing the system dynamics.
- **Data Analysis**: Tools for processing and analyzing simulation and experimental data.
- **Visualization**: Custom plotting functions for exploring system responses and user interactions.

For more details, see the `README.md` in the MATLAB folder.

## Features
- **Double Inverted Pendulum Simulation**: Physics-based modeling of a cart with two pendulums, including linearization and control.
- **Measurement Evaluation**: Evaluates human response based on cursor displacement and speed as inputs, and pendulum angular error and velocity as outputs.
- **Reaction Time Testing**: Integrated tool for measuring user reaction time.
- **Customizable Parameters**: Configurable settings for pendulum lengths, weights, control methods, and simulation properties.

## Prerequisites

### Python:
- Python 3.8+
- Required Libraries: numpy, scipy, pygame, matplotlib, screeninfo, pandas, PyAutoGUI, pywin32, PyYAML. (You can easily install them using the requirements.txt file in Python folder.)

### MATLAB:
- MATLAB R2020b or newer.
- Required Toolboxes: Control System Toolbox and Signal Processing Toolbox.

## Getting Started
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/rozinkaadam/double_inverted_pendulum_simulation_software.git
   ```

2. **Python Setup**:
   - Navigate to the Python folder and install dependencies.
     ```bash
     cd "Python - Simulation, measurement"
     pip install -r requirements.txt
     ```
   - Launch the simulation software:
     ```bash
     python run.py
     ```

3. **MATLAB Setup**:
   - Open MATLAB and navigate to the MATLAB folder.
   - Run the desired scripts for modeling or data analysis. 
   - For more information, see the README.md file in the Matlab folder.

4. **Experiment with Configuration**:
   - Use the configuration GUI in the Python simulation to adjust parameters.
   - Utilize MATLAB scripts for detailed data evaluation.
