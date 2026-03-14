import math


def calculate_pga(magnitude, distance, soil_type="medium_soil"):
    """
    Calculate Peak Ground Acceleration using the Fukushima-Tanaka attenuation model.

    log10(A) = 0.41M - log[R + 0.032(10^0.41M)] - 0.0034R + 1.30

    Parameters:
        magnitude (float): Earthquake magnitude (M).
        distance (float): Distance to seismic source in km (R).
        soil_type (str): One of 'rock', 'hard_soil', 'medium_soil', 'soft_soil'.

    Returns:
        dict: {'pga_cm_s2': float, 'pga_g': float, 'correction_factor': float}
    """
    if magnitude <= 0:
        raise ValueError("Magnitude must be positive.")
    if distance <= 0:
        raise ValueError("Distance must be positive.")

    correction_factors = {
        "rock": 0.60,
        "hard_soil": 0.87,
        "medium_soil": 1.07,
        "soft_soil": 1.39,
    }

    if soil_type not in correction_factors:
        raise ValueError(
            f"Invalid soil_type '{soil_type}'. Must be one of: {list(correction_factors.keys())}"
        )

    M = magnitude
    R = distance

    log_a = 0.41 * M - math.log10(R + 0.032 * math.pow(10, 0.41 * M)) - 0.0034 * R + 1.30
    pga_raw = math.pow(10, log_a)

    cf = correction_factors[soil_type]
    pga_corrected = pga_raw * cf
    pga_g = pga_corrected / 980.0  # 1g = 980 cm/s²

    return {
        "pga_cm_s2": round(pga_corrected, 4),
        "pga_g": round(pga_g, 6),
        "correction_factor": cf,
    }
