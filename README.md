# APEC Seismic Py

[![PyPI version](https://img.shields.io/pypi/v/apecseismicpy)](https://pypi.org/project/apecseismicpy/)
[![Python](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/github/license/albertp16/apec-py)](https://github.com/albertp16/apec-py/blob/main/LICENSE)
[![Issues](https://img.shields.io/github/issues/albertp16/apec-py)](https://github.com/albertp16/apec-py/issues)

A Python library for seismic engineering calculations under the **National Structural Code of the Philippines (NSCP 2015)** and **ACI 350.3** hydrodynamic tank load provisions. Built by [APEC Engineering Consultancy](mailto:albert@apeconsultancy.net) to streamline code-compliant structural analysis workflows.

---

## Features

- **NSCP 2015 Seismic Design** — site coefficients, design response spectrum, structural period, and lateral base shear (Equations 208-4 through 208-11)
- **ACI 350.3 Hydrodynamic Loads** — impulsive and convective liquid weights, heights of centers of gravity (EBP and IBP), and dynamic periods for rectangular tanks
- **Interactive Web Application** — browser-based UI with live charts, PNG export, and LaTeX calculation report generation
- **Modular Python API** — import individual functions or classes for integration into your own workflows

---

## Installation

```bash
pip install apecseismicpy
```

Or install from source:

```bash
git clone https://github.com/albertp16/apec-py.git
cd apec-py
pip install -e .
```

---

## Quick Start

### NSCP 2015 Base Shear

```python
from apecseismicpy import site_coefficients, ResponseSpectrum, calculateStructuralPeriod, calculate_base_shear

# 1. Site coefficients
sc = site_coefficients(distance=10.0, source_type="A", soil_profile="SD")
print(sc)  # {'Na': 1.0, 'Nv': 1.6, 'Ca': 0.44, 'Cv': 0.64}

# 2. Response spectrum
rs = ResponseSpectrum(Ca=0.44, Cv=0.64)
spectrum = rs.generate(T_max=4.0)

# 3. Structural period (Method B — Rayleigh)
T = calculateStructuralPeriod(method="B", Ct=0.0731, hn=15.0)
print(T)   # {'Ti': 0.48, 'units': 's'}

# 4. Base shear
V = calculate_base_shear(zone=4, I=1.0, R=8.5, W=5000.0, Ca=0.44, Cv=0.64, T=0.48)
print(V)   # {'V': 294.1, 'units': 'kN', 'equation': '208-8'}
```

### ACI 350.3 Tank Hydrodynamic Loads

```python
from apecseismicpy import (
    effective_liquid_weights,
    calculate_heights_of_centers_of_gravity,
    DynamicProperties,
)

# Effective liquid weights
weights = effective_liquid_weights(L=6.0, height=3.0, liquid_weight=500.0)
print(weights)
# {'impulsive': {'value': 302.4, 'units': 'kN'}, 'convective': {'value': 177.6, 'units': 'kN'}}

# Heights of centers of gravity (EBP and IBP)
heights = calculate_heights_of_centers_of_gravity(l=6.0, h_l=3.0)
print(heights)
# {'EPB': {'hi': 1.125, 'hc': 1.82}, 'IBP': {'hpi': 1.35, 'hpc': 2.01}}

# Dynamic periods
dp = DynamicProperties(
    length=6.0, hw=4.0, tw=0.3,
    wi=302.4, wl=500.0, hl=3.0, hi=1.125,
    ec=27000.0
)
print(dp.compute_ti())  # {'value': 0.12, 'units': 's'}
print(dp.compute_tc())  # {'value': 3.45, 'units': 's'}
```

---

## Web Application

The package includes a FastAPI web application for interactive calculations with chart visualizations and downloadable LaTeX reports.

### Running the App

```bash
# Clone the repository
git clone https://github.com/albertp16/apec-py.git
cd apec-py

# Install dependencies
pip install fastapi uvicorn jinja2 numpy matplotlib

# Start the server
uvicorn app:app --reload
```

Then open your browser at **http://127.0.0.1:8000**.

### App Features

| Tab | Description |
|-----|-------------|
| **Site Coefficients** | Compute Na, Nv, Ca, Cv for any seismic zone, source type, and soil profile |
| **Response Spectrum** | Generate and plot the NSCP 2015 design spectrum with TH-reference and ADRS curves |
| **Base Shear** | Calculate governing lateral seismic force per NSCP 2015 Section 208 |
| **Tank Analysis** | ACI 350.3 hydrodynamic loads — impulsive/convective weights, heights, Ti, Tc |
| **LaTeX Report** | Auto-generate a formatted `.tex` calculation report from all entered values |

Each chart supports **PNG export** via the download button in the chart header.

---

## API Reference

### `site_coefficients(distance, source_type, soil_profile)`

Returns near-source factors and seismic coefficients per NSCP 2015 Table 208-4 through 208-7.

| Parameter | Type | Description |
|-----------|------|-------------|
| `distance` | `float` | Distance to seismic source (km) |
| `source_type` | `str` | Seismic source type: `"A"`, `"B"`, or `"C"` |
| `soil_profile` | `str` | Soil profile type: `"SA"` to `"SF"` |

---

### `ResponseSpectrum(Ca, Cv)`

Class for generating NSCP 2015 design response spectra.

| Method | Returns | Description |
|--------|---------|-------------|
| `generate(T_max)` | `dict` | Arrays of T and Sa values up to T_max |
| `Sa_at(T)` | `float` | Spectral acceleration at a given period |

---

### `calculateStructuralPeriod(method, **kwargs)`

Computes the fundamental period of vibration.

| Method | Required kwargs | Description |
|--------|----------------|-------------|
| `"A"` | `Ct`, `hn` | Simplified empirical formula (Eq. 208-12) |
| `"B"` | `Ct`, `hn` | Rayleigh method (Eq. 208-13) |

---

### `calculate_base_shear(zone, I, R, W, Ca, Cv, T)`

Returns the governing lateral base shear per NSCP 2015 Section 208.

| Parameter | Type | Description |
|-----------|------|-------------|
| `zone` | `int` | Seismic zone (2, 3, or 4) |
| `I` | `float` | Importance factor |
| `R` | `float` | Response modification factor |
| `W` | `float` | Seismic dead load (kN) |
| `Ca`, `Cv` | `float` | Seismic coefficients |
| `T` | `float` | Fundamental period (s) |

---

### `effective_liquid_weights(L, height, liquid_weight, plot=False)`

Computes impulsive and convective liquid weights per ACI 350.3 Eq. 9.2.1a–b.

---

### `calculate_heights_of_centers_of_gravity(l, h_l, plot=False)`

Returns hi, hc (EBP) and h'i, h'c (IBP) per ACI 350.3 Section 9.2.2–9.2.3.

---

### `DynamicProperties(length, hw, tw, wi, wl, hl, hi, ec, ...)`

Class for computing wall-liquid system dynamic properties per ACI 350.3 R.9.2.4.

| Method | Returns | Description |
|--------|---------|-------------|
| `compute_mw()` | `dict` | Wall mass per unit length (kg/m) |
| `compute_mi()` | `dict` | Impulsive liquid mass per unit length (kg/m) |
| `compute_k()` | `dict` | Wall stiffness (kN/m) |
| `compute_ti()` | `dict` | Impulsive period Ti (s) |
| `compute_tc()` | `dict` | Convective (sloshing) period Tc (s) |

---

## Project Structure

```
apec-py/
├── app.py                          # FastAPI web application
├── templates/
│   └── index.html                  # Single-page UI (Bootstrap 5 + Chart.js)
├── apecseismicpy/
│   ├── __init__.py                 # Public API exports
│   ├── nscp2015/
│   │   ├── site_coefficients.py    # Na, Nv, Ca, Cv lookup tables
│   │   ├── response_spectrum.py    # Design spectrum generation
│   │   ├── period.py               # Structural period methods
│   │   └── baseshear.py            # Base shear equations
│   └── aci350/
│       └── hydrodynamic/
│           ├── loads.py            # Liquid weights and CG heights
│           ├── period.py           # Tank dynamic periods
│           └── pressure.py         # Hydrodynamic pressure distributions
└── setup.py
```

---

## Contributing

Contributions are welcome. To get started:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes and add tests where applicable
4. Submit a pull request with a clear description of the changes

Please follow existing code style and document any new public functions with docstrings.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## Author

**Albert Pamonag** — APEC Engineering Consultancy
Email: albert@apeconsultancy.net
Repository: https://github.com/albertp16/apec-py
