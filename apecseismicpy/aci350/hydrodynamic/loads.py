
import math
import numpy as np
import matplotlib.pyplot as plt

def effective_liquid_weights(L: float, height: float, liquid_weight: float, plot: bool = False) -> dict:
    """
    Calculate the effective acceleration liquid weights based on ACI 350 (Eq. 9.2.1a & 9.2.1b),
    and optionally plot the mass factors versus L/H_L ratio.

    Parameters:
        L (float): Length of the base parallel motion (L) in meters
        height (float): Height of the tank (height) in meters 
        liquid_weight (float): Liquid Weight of the tank (liquid_weight) in kN
        plot (bool): Whether to generate a plot of mass factors vs. L/H_L ratio.

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
    
    # Generate plot if requested
    if plot:
        l_hl_ratios = np.linspace(0.5, 8, 100)
        wi_values = [math.tanh(0.866 * r) / (0.866 * r) for r in l_hl_ratios]
        wc_values = [0.264 * r * math.tanh(3.16 * (1 / r)) for r in l_hl_ratios]
        
        plt.figure(figsize=(8, 6))
        plt.plot(l_hl_ratios, wi_values, label="$W_i / W_L$", color='blue')
        plt.plot(l_hl_ratios, wc_values, label="$W_c / W_L$", color='purple')
        plt.xlabel("L / H_L Ratio")
        plt.ylabel("Mass Factors")
        plt.title("Impulsive and Convective Mass Factors vs. L/H_L Ratio")
        plt.legend()
        plt.grid(True)
        plt.show()
    
    return result

def calculate_heights_of_centers_of_gravity(l: float, h_l: float, plot: bool = False) -> dict:
    """
    Calculate the heights to centers of gravity for EBP and IBP based on ACI 350 (Section 9.2.2 & 9.2.3),
    and optionally plot the height factors versus L/H_L ratio.

    Parameters:
        l (float): Base length of the tank (parallel motion).
        h_l (float): Height of the liquid column.
        plot (bool): Whether to generate a plot of height factors vs. L/H_L ratio.

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
    
    # Generate separate plots if requested
    if plot:
        l_hl_ratios = np.linspace(0.5, 8, 100)
        h_i_values = [(0.5 - 0.09375 * r) if r < 1.333 else 0.375 for r in l_hl_ratios]
        h_c_values = [1 - (math.cosh(3.16 * (1 / r)) - 1) / (3.16 * (1 / r) * math.sinh(3.16 * (1 / r))) for r in l_hl_ratios]
        h_pi_values = [0.45 if r < 0.75 else ((0.866 * r) / (2 * math.tanh(0.866 * r)) - 1/8) for r in l_hl_ratios]
        h_pc_values = [1 - (math.cosh(3.16 * (1 / r)) - 2.01) / (3.16 * (1 / r) * math.sinh(3.16 * (1 / r))) for r in l_hl_ratios]
        
        # Plot EBP factors
        plt.figure(figsize=(8, 6))
        plt.plot(l_hl_ratios, h_i_values, label="$h_i / H_L$", color='blue')
        plt.plot(l_hl_ratios, h_c_values, label="$h_c / H_L$", color='purple')
        plt.xlabel("L / H_L Ratio")
        plt.ylabel("EBP Height Factors")
        plt.title("Impulsive and Convective Height Factors (EBP) vs. L/H_L Ratio")
        plt.legend()
        plt.grid(True)
        plt.show()
        
        # Plot IBP factors
        plt.figure(figsize=(8, 6))
        plt.plot(l_hl_ratios, h_pi_values, label="$h'_i / H_L$", color='blue')
        plt.plot(l_hl_ratios, h_pc_values, label="$h'_c / H_L$", color='purple')
        plt.xlabel("L / H_L Ratio")
        plt.ylabel("IBP Height Factors")
        plt.title("Impulsive and Convective Height Factors (IBP) vs. L/H_L Ratio")
        plt.legend()
        plt.grid(True)
        plt.show()
    
    return result


