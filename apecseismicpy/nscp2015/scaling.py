import math


def calculate_scaling(static_shear, scale_factor, dynamic_data):
    """
    Calculate base shear scale factors using SRSS combination.

    SRT = √(x² + y²)
    ratio = scale_factor × (V_static / SRT)

    Parameters:
        static_shear (float): Static base shear V_static (kN).
        scale_factor (float): Scale factor (1.0, 0.90, or 0.80).
        dynamic_data (list of dict): Each dict has 'label', 'x', 'y' keys.
            e.g. [{'label': 'MAJOR', 'x': 106.27, 'y': 4499.40},
                  {'label': 'ORTHO', 'x': 4299.50, 'y': 85.74}]

    Returns:
        dict: {'results': [{'label': str, 'srt': float, 'ratio': float}, ...]}
    """
    if static_shear <= 0:
        raise ValueError("Static base shear must be positive.")
    if not dynamic_data:
        raise ValueError("Dynamic data must not be empty.")

    results = []
    for entry in dynamic_data:
        x = float(entry["x"])
        y = float(entry["y"])
        srt = math.sqrt(x * x + y * y)
        if srt == 0:
            raise ValueError(f"SRSS is zero for '{entry.get('label', '?')}' — cannot divide.")
        ratio = scale_factor * (static_shear / srt)
        results.append({
            "label": entry.get("label", ""),
            "srt": round(srt, 4),
            "ratio": round(ratio, 4),
        })

    return {"results": results}
