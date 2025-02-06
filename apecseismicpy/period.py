import math

def calculate(type, hn):
    """
    Calculate the seismic period based on the type of structure and height.

    Parameters:
    type (str): The type of structure ('concrete', 'steel', or other).
    hn (float): The height of the structure.

    Returns:
    float: The calculated seismic period.
    """
    if not isinstance(type, str) or not isinstance(hn, (int, float)):
        raise ValueError("Invalid input: 'type' must be a string and 'hn' must be a number.")
    
    if type == 'concrete':
        ct = 0.0731
    elif type == 'steel':
        ct = 0.0853
    else:
        ct = 0.0488
    
    period = ct * math.pow(hn, 0.75)
    return period