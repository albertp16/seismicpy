import math


def calculate_redundancy(v_struc, v_element, ab, factor=1.25):
    """
    Calculate the structural redundancy factor (rho) per NSCP 2015.

    ρ = 2 - (6.1 / (r_max × √AB))

    Parameters:
        v_struc (float): Structure story shear (kN).
        v_element (float): Element story shear (kN).
        ab (float): Floor area of the building (m²).
        factor (float): Maximum redundancy factor — 1.25 for SMRF, 1.50 for Others.

    Returns:
        dict: {'r_max': float, 'rho_raw': float, 'rho': float, 'factor': float}
    """
    if v_struc <= 0:
        raise ValueError("Structure story shear must be positive.")
    if ab <= 0:
        raise ValueError("Floor area must be positive.")

    r_max = v_element / v_struc
    rho_raw = 2.0 - (6.1 / (r_max * math.sqrt(ab)))
    rho_clamped = max(rho_raw, 1.0)
    rho = min(rho_clamped, factor)

    return {
        "r_max": round(r_max, 6),
        "rho_raw": round(rho_raw, 4),
        "rho_clamped": round(rho_clamped, 4),
        "rho": round(rho, 4),
        "factor": factor,
    }
