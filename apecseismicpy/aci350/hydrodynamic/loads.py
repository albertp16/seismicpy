
import math

def effective_liquid_weights(L: float, height: float, liquid_weight: float) -> dict:
    """
    Calculate the effective acceleration liquid weights based on ACI 350 (Eq. 9.2.1a & 9.2.1b).

    Parameters:
        L (float): Length of the base parallel motion (L) in meters
        height (float): Height of the tank (height) in meters
        liquid_weight (float): Liquid Weight of the tank (liquid_weight) in kN

    Returns:
        dict: A dictionary with the impulsive and convective weight components.
    """
    # Guard clauses for input validation
    if L <= 0 or liquid_weight <= 0 or height <= 0:
        raise ValueError("All input parameters must be positive nonzero values.")
    
    ratio_l_hl = L / height
    
    # Impulsive Weight Calculation (Eq. 9.2.1a)
    wi_ratio = math.tanh(0.866 * ratio_l_hl) / (0.866 * ratio_l_hl)
    wi = wi_ratio * liquid_weight
    
    # Convective Weight Calculation (Eq. 9.2.1b)
    wc_ratio = 0.264 * ratio_l_hl * math.tanh(3.16 * (height / L))
    wc = wc_ratio * liquid_weight
    


    result = {
        "impulsive": {
            "value" : wi,
            "units" : "kN"
            },
        "convective": {
            "value" : wc,
            "units" : "kN"
        }
        }
    
    return result

def calculate_heights_of_centers_of_gravity(l: float, h_l: float) -> dict:
    """
    Calculate the heights to centers of gravity for EBP and IBP based on ACI 350 (Section 9.2.2 & 9.2.3).

    Parameters:
        l (float): Base length of the tank (parallel motion).
        h_l (float): Height of the liquid column.

    Returns:
        dict: A dictionary containing the heights to centers of gravity for both EBP and IBP.
    """
    # Guard clauses for input validation
    if l <= 0 or h_l <= 0:
        raise ValueError("Both base length and liquid height must be positive nonzero values.")
    
    ratio_l_hl = l / h_l
    
    # Heights to centers of gravity, EBP
    hi = (0.5 - 0.09375 * ratio_l_hl) * h_l if ratio_l_hl < 1.333 else 0.375 * h_l
    hc = (1 - (math.cosh(3.16 * (h_l / l)) - 1) / (3.16 * (h_l / l) * math.sinh(3.16 * (h_l / l)))) * h_l
    
    # Heights to centers of gravity, IBP
    hpi = 0.45 * h_l if ratio_l_hl < 0.75 else ((0.866 * ratio_l_hl) / (2 * math.tanh(0.866 * ratio_l_hl)) - 1/8) * h_l
    hpc = (1 - (math.cosh(3.16 * (h_l / l)) - 2.01) / (3.16 * (h_l / l) * math.sinh(3.16 * (h_l / l)))) * h_l
    
    result = {
        "EPB" : {
            "hi": hi, 
            "hc": hc, 
        }, 
        "IBP" : {
            "hpi": hpi, 
            "hpc": hpc
        }
        }
    
    return result


