import math

def calculateStructuralPeriod(type, hn):
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


def calculatePeriodWithLimit(type, hn, zone=4):
    """
    Calculate the seismic period and its zone-dependent upper limit.

    Parameters:
        type (str): Structure type ('concrete', 'steel', or other).
        hn (float): Height of the structure (m).
        zone (int): Seismic zone (2 or 4).

    Returns:
        dict: {'period': float, 'limit': float}
    """
    period = calculateStructuralPeriod(type, hn)

    if zone == 2:
        limit = period * 1.40
    elif zone == 4:
        limit = period * 1.70
    else:
        limit = period * 1.40

    return {"period": round(period, 4), "limit": round(limit, 4)}