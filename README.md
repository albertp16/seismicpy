# APEC Seismic Py

[![PyPI version](https://img.shields.io/pypi/v/apecseismicpy)](https://pypi.org/project/apecseismicpy/)
[![Python](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/github/license/albertp16/apec-py)](https://github.com/albertp16/apec-py/blob/main/LICENSE)
[![Issues](https://img.shields.io/github/issues/albertp16/apec-py)](https://github.com/albertp16/apec-py/issues)

A Python library for seismic engineering calculations under the **National Structural Code of the Philippines (NSCP 2015)** and the **DPWH Bridge Seismic Design Specifications (BSDS)**. Built by [APEC Engineering Consultancy](https://seismic.apeconsultancy.net) to streamline code-compliant structural analysis workflows.

🌐 **Live Web App:** [seismic.apeconsultancy.net](https://seismic.apeconsultancy.net)

---

## Features

- **NSCP 2015 Seismic Design** — site coefficients, design response spectrum, structural period, and lateral base shear (Equations 208-4 through 208-11)
- **DPWH BSDS Design Spectrum** — Level I and Level II design response spectra with site factor interpolation (Fa, Fv, FPGA), 2/3-rule minimum overlay, and data export
- **Interactive Web Application** — browser-based UI with live charts, PNG export, and period/acceleration data download
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

### DPWH BSDS Design Response Spectrum

```python
from apecseismicpy.bsds import site_factors, generate_spectrum

# Site amplification factors
factors = site_factors(pga=0.4, site_class="D")
print(factors)
# {'Fpga': 0.9, 'Fa': 0.96, 'Fv': 1.6, 'As': 0.45, 'Sds': 1.056, 'Sd1': 0.64, 'Ts': 0.606, 'T0': 0.121}

# Level II spectrum
lv2 = generate_spectrum(Sds=1.056, Sd1=0.64, T_max=4.0, level="II")
# Returns {'T': [...], 'Sa': [...]}

# Level I spectrum (2/3 of Level II)
lv1 = generate_spectrum(Sds=1.056, Sd1=0.64, T_max=4.0, level="I")
```

---

## Web Application

The package includes a FastAPI web application for interactive calculations with chart visualizations and downloadable data.

🌐 **Try it live:** [seismic.apeconsultancy.net](https://seismic.apeconsultancy.net)

### Running Locally

```bash
# Clone the repository
git clone https://github.com/albertp16/apec-py.git
cd apec-py

# Install dependencies
pip install fastapi uvicorn jinja2

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
| **BSDS Spectrum** | DPWH BSDS Level II and Level I design response spectra with site factor table, 2/3-minimum overlay, PNG export, and period/acceleration data download |

---

## API Reference

### NSCP 2015

#### `site_coefficients(distance, source_type, soil_profile)`

Returns near-source factors and seismic coefficients per NSCP 2015 Table 208-4 through 208-7.

| Parameter | Type | Description |
|-----------|------|-------------|
| `distance` | `float` | Distance to seismic source (km) |
| `source_type` | `str` | Seismic source type: `"A"`, `"B"`, or `"C"` |
| `soil_profile` | `str` | Soil profile type: `"SA"` to `"SF"` |

---

#### `ResponseSpectrum(Ca, Cv)`

Class for generating NSCP 2015 design response spectra.

| Method | Returns | Description |
|--------|---------|-------------|
| `generate(T_max)` | `dict` | Arrays of T and Sa values up to T_max |
| `Sa_at(T)` | `float` | Spectral acceleration at a given period |

---

#### `calculateStructuralPeriod(method, **kwargs)`

Computes the fundamental period of vibration.

| Method | Required kwargs | Description |
|--------|----------------|-------------|
| `"A"` | `Ct`, `hn` | Simplified empirical formula (Eq. 208-12) |
| `"B"` | `Ct`, `hn` | Rayleigh method (Eq. 208-13) |

---

#### `calculate_base_shear(zone, I, R, W, Ca, Cv, T)`

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

### DPWH BSDS

#### `site_factors(pga, site_class)`

Returns BSDS site amplification factors and design spectral parameters.

| Parameter | Type | Description |
|-----------|------|-------------|
| `pga` | `float` | Peak ground acceleration (g) |
| `site_class` | `str` | Site class: `"A"` to `"E"` |

Returns: `Fpga`, `Fa`, `Fv`, `As`, `Sds`, `Sd1`, `Ts`, `T0`

---

#### `generate_spectrum(Sds, Sd1, T_max, level)`

Generates a BSDS design response spectrum.

| Parameter | Type | Description |
|-----------|------|-------------|
| `Sds` | `float` | Design spectral acceleration at short periods (g) |
| `Sd1` | `float` | Design spectral acceleration at 1-second period (g) |
| `T_max` | `float` | Maximum period for the spectrum (s) |
| `level` | `str` | `"I"` (1/3 probability in 75 yrs) or `"II"` (10% in 50 yrs) |

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
│   └── bsds/
│       ├── __init__.py             # BSDS public exports
│       ├── site_factor.py          # Fa, Fv, Fpga interpolation tables
│       └── spectrum.py             # Level I and Level II spectrum generation
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
Web App: https://seismic.apeconsultancy.net
Repository: https://github.com/albertp16/apec-py
