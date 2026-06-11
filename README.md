# APEC SeismicPy

[![PyPI version](https://img.shields.io/pypi/v/apecseismicpy)](https://pypi.org/project/apecseismicpy/)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/github/license/albertp16/seismicpy)](https://github.com/albertp16/seismicpy/blob/main/LICENSE)

A Python library and web application for seismic engineering calculations under the **National Structural Code of the Philippines (NSCP 2015)** and the **DPWH Bridge Seismic Design Specifications (BSDS)**. Built by [APEC Engineering Consultancy](https://seismic.apeconsultancy.net).

**Live Web App:** [seismic.apeconsultancy.net](https://seismic.apeconsultancy.net)

---

## Features

### NSCP 2015 Modules
- **Site Coefficients** — Na, Nv, Ca, Cv lookup with distance interpolation (Tables 208-4 to 208-8)
- **Response Spectrum** — Design spectrum, 1.4x TH-reference envelope, and ADRS curves
- **Base Shear** — Governing lateral force per Eq. 208-8 through 208-11
- **Structural Period** — Empirical formula with zone-limited upper bound (Section 208.5.2.2)
- **Redundancy Factor** — NSCP Section 208.5.6 redundancy calculation
- **PGA Calculator** — Fukushima-Tanaka attenuation model
- **Scaling Base Shear** — SRSS-based dynamic analysis scaling

### DPWH BSDS Modules
- **Design Spectrum** — Level I and Level II response spectra with site factor interpolation (Fpga, Fa, Fv), damping ratio adjustment, and 2/3-rule minimum overlay
- **Site-Specific Spectrum** — Design response spectrum from site-specific PGA, Ss, S1 with no site factor interpolation (Fpga = Fa = Fv = 1.0) and 2/3-rule minimum overlay

### Diagram Modules
- **Story Shear** and **Overturning Moment** — Spreadsheet input with interactive plots
- **Story Displacement** — Per-story tables with TH1-TH7 load case support
- **Story Drift** and **Story Acceleration** — With user-defined limit lines

### Smart Auto-Fill
Site coefficient results (Ca, Cv, Nv, Zone) automatically populate the Response Spectrum and Base Shear input fields, visually indicated by a light green hatch on auto-filled fields.

---

## Installation

```bash
pip install apecseismicpy
```

Or install from source:

```bash
git clone https://github.com/albertp16/seismicpy.git
cd seismicpy
pip install .
```

---

## Quick Start

### Site Coefficients

```python
from apecseismicpy import site_coefficients

sc = site_coefficients(distance=5.0, source_type="B", soil_type="sd", zone=4)
result = sc.calculate()
# {'na': 1.0, 'nv': 1.29, 'ca': 0.44, 'cv': 0.72}
```

### Response Spectrum

```python
from apecseismicpy import ResponseSpectrum

rs = ResponseSpectrum(ca=0.44, cv=0.72)
x, Sa = rs.calculate(x_max=5.0)
# x  = normalized period T/Ts
# Sa = spectral acceleration (g)
print(rs.Ts, rs.T0, rs.sa_max)
```

### Structural Period

```python
from apecseismicpy import calculateStructuralPeriod, calculatePeriodWithLimit

T = calculateStructuralPeriod("concrete", hn=15.0)
# Returns period in seconds

result = calculatePeriodWithLimit("concrete", hn=15.0, zone=4)
# Returns {'period': T, 'limit': T_upper, 'governing': min(T, T_upper)}
```

### Base Shear

```python
from apecseismicpy import calculate_base_shear

bs = calculate_base_shear(
    zone=4, nv=1.29, ca=0.44, cv=0.72,
    importance_factor=1.0, response_modification=8.0,
    period=0.62, weight=21000.0
)
print(bs.totalBaseShear())    # Eq. 208-8
print(bs.maxBaseShear())      # Eq. 208-9
print(bs.minBaseShear())      # Eq. 208-10
print(bs.maxBaseShearZ4())    # Eq. 208-11 (Zone 4 only)
print(bs.governingShear())    # Governing value
```

### PGA (Fukushima-Tanaka)

```python
from apecseismicpy import calculate_pga

result = calculate_pga(magnitude=7.0, distance=25.0, soil_type="medium_soil")
```

### Redundancy Factor

```python
from apecseismicpy import calculate_redundancy

result = calculate_redundancy(v_struc=500.0, v_element=120.0, ab=200.0, factor=1.25)
```

### DPWH BSDS Design Spectrum

```python
from apecseismicpy.bsds import SeismicSiteFactor, SeismicDesignResponse

sf = SeismicSiteFactor("II", pga=0.4, ss=1.0, s1=0.4)
fpga = sf.interpolate_site_factor()
fa = sf.get_site_factor_fa()
fv = sf.get_site_factor_fv()

sdr = SeismicDesignResponse(pga=0.4, fpga=fpga, ss=1.0, s1=0.4, fa=fa, fv=fv)
level2 = sdr.generate_level2_spectrum(max_period=8.0)
level1 = sdr.generate_level1_spectrum("II", damping_ratio=0.02, max_period=8.0)
```

---

## Web Application

The package includes a FastAPI web application with interactive charts, PNG export, and spreadsheet-style data input.

**Try it live:** [seismic.apeconsultancy.net](https://seismic.apeconsultancy.net)

### Running Locally

```bash
git clone https://github.com/albertp16/seismicpy.git
cd seismicpy
pip install -r requirements.txt
pip install .
uvicorn app:app --reload
```

Then open **http://127.0.0.1:8000**.

### Web App Modules

| Module | Description |
|--------|-------------|
| **Site Coefficients** | Na, Nv, Ca, Cv for any zone, source type, and soil profile |
| **Response Spectrum** | NSCP 2015 design spectrum + 1.4x TH reference + ADRS plot |
| **Base Shear** | Governing lateral force (Eq. 208-8 to 208-11) |
| **Structural Period** | Empirical period with zone-limited upper bound |
| **Redundancy** | Redundancy factor per Section 208.5.6 |
| **PGA** | Peak ground acceleration via Fukushima-Tanaka |
| **Scaling Base Shear** | SRSS dynamic scaling |
| **BSDS Spectrum** | Level I and Level II spectra with site factors and PNG export |
| **Site-Specific Spectrum** | BSDS-shape design spectrum with Fpga = Fa = Fv = 1.0 (site-specific hazard values used directly) |
| **Story Shear** | Interactive story shear diagram from spreadsheet input |
| **Overturning Moment** | Overturning moment diagram |
| **Story Displacement** | Per-story displacement with TH1-TH7 load cases |
| **Story Drift** | Interstory drift with configurable limit line |
| **Story Acceleration** | Floor acceleration with configurable limit line |

---

## Project Structure

```
seismicpy/
├── app.py                          # FastAPI web application
├── templates/
│   └── index.html                  # Single-page UI (Bootstrap 5 + Chart.js)
├── apecseismicpy/
│   ├── __init__.py                 # Public API exports
│   ├── nscp2015/
│   │   ├── site_coefficients.py    # Na, Nv, Ca, Cv lookup tables
│   │   ├── response_spectrum.py    # Design spectrum generation
│   │   ├── baseshear.py            # Base shear equations (208-8 to 208-11)
│   │   ├── period.py               # Structural period (empirical + limit)
│   │   ├── pga.py                  # Fukushima-Tanaka attenuation
│   │   ├── redundancy.py           # Redundancy factor
│   │   └── scaling.py              # SRSS dynamic scaling
│   ├── bsds/
│   │   ├── site_factor.py          # Fpga, Fa, Fv interpolation tables
│   │   └── spectrum.py             # Level I and Level II spectrum
│   └── aci350/
│       └── hydrodynamic/           # Tank hydrodynamic analysis
├── Dockerfile                      # Production container
├── requirements.txt                # Python dependencies
├── setup.py                        # Package installer
└── CHANGELOG.md                    # Version history
```

---

## Deployment

The app is containerized and deploys to [Railway](https://railway.com) from the `main` branch.

```bash
# Build locally
docker build -t seismicpy .
docker run -p 8000:8000 -e PORT=8000 seismicpy
```

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make changes and test
4. Submit a pull request

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Author

**Albert Pamonag** — APEC Engineering Consultancy
- Email: albert@apeconsultancy.net
- Web: [seismic.apeconsultancy.net](https://seismic.apeconsultancy.net)
- Repository: [github.com/albertp16/seismicpy](https://github.com/albertp16/seismicpy)
