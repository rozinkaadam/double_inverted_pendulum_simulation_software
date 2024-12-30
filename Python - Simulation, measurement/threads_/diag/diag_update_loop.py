from libs.varstructs.SIM_STATE import SIM_STATE

def diag_update_values(SIM_STATE_VAR: SIM_STATE, diag_widget):
    """
    Updates the diagnostic widget with the current state of the simulation.

    Args:
        SIM_STATE_VAR (SIM_STATE): The current simulation state object.
        diag_widget: The widget or GUI component responsible for displaying diagnostic information.

    This function is called to refresh the diagnostic widget with the latest
    values from the simulation state. It ensures that the displayed information
    reflects the current state of the simulation.
    """
    diag_widget.update_state_var_display(SIM_STATE_VAR)
