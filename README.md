# APEC SeismicPy

[![PyPI version](https://img.shields.io/pypi/v/apecseismicpy)](https://pypi.org/project/apecseismicpy/)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/github/license/albertp16/seismicpy)](https://github.com/albertp16/seismicpy/blob/main/LICENSE)

A Python library and web application for seismic engineering calculations under the **National Structural Code of the Philippines (NSCP 2015 and 2024)**, the **DPWH Bridge Seismic Design Specifications (BSDS)**, **ASCE 41-17 Seismic Evaluation and Retrofit of Existing Buildings**, and **ACI 350 tank hydrodynamics**. Built by [Albert Pamonag Engineering Consultancy](https://seismic.apeconsultancy.net) — developed by **Albert Pamonag** and **Camille Pajarillaga**.

**Live Web App:** [seismic.apeconsultancy.net](https://seismic.apeconsultancy.net)

---

## Features

### NSCP 2015 Modules
- **Site Coefficients** — Na, Nv, Ca, Cv lookup with distance interpolation (Tables 208-4 to 208-8)
- **Response Spectrum** — Design spectrum and 1.4x time-history reference envelope
- **ADRS** — Acceleration-displacement response spectrum with radial period lines, ATC-40 spectral reduction, pushover capacity curve overlay, trial performance point, and a full calculation report
- **Base Shear** — Eq. 208-8 through 208-10 plus the Zone 4 minimum (Eq. 208-11); the governing value is returned for Zone 4 only
- **Structural Period** — Empirical formula with a zone-dependent upper bound (1.70x the period in Zone 4, 1.40x otherwise)
- **Redundancy Factor** — NSCP Section 208.5.6 redundancy calculation
- **PGA Calculator** — Fukushima-Tanaka attenuation model
- **Scaling Base Shear** — SRSS-based dynamic analysis scaling

### NSCP 2024 (8th Edition) Modules
- **Design Spectrum** — Two-parameter (Ss, S1) design response spectrum with Fa/Fv site-class interpolation, design and MCE_R curves, and control periods T0, Ts, TL

### ASCE 41 / ASCE 7 Modules
- **Design Spectrum** — The ASCE 7 two-parameter general spectrum with the 80% site-specific lower bound of ASCE 7-16 Section 21.3 and ASCE 41-17 Section 2.4.2, plotted at both the MCE_R and design levels (0.80 Sms and 0.80 Sds — the same requirement stated at two altitudes)
- **NSCP vs ASCE 41 Overlay** — NSCP 2015 and ASCE 41 design spectra on one axis with their ordinate ratio
- **BSE-1E / BSE-2E Spectra** — General horizontal response spectra for both hazard levels (Section 2.4.1.7.1). BSE-2E is the mapped MCE (Section 2.4.1.3) and BSE-1E is two-thirds of it (Section 2.4.1.4), so both share T0 and Ts. Site coefficients follow ASCE 7-16 Tables 11.4-1/11.4-2 including the Section 11.4.4 floor Fa >= 1.2 for a defaulted Site Class D, with the Eq. (2-3) damping adjustment B1, the Section 11.4.8 site-specific trigger and its 1.5Ts Exception 2 bound, and MIDAS `.sgs` export. Two interpretations are built in and worth knowing: where no 5%/50-year and 20%/50-year hazard maps exist, both BSE caps are taken from the mapped MCE, which over-states demand; and the ASCE 7 Exception 2 amplification, written for the ELF coefficient Cs, is carried onto the Section 2.4.1.7 general spectrum. Both are conservative in direction, and the app prints the governing clauses per run

### DPWH BSDS Modules
- **Design Spectrum** — Level I and Level II response spectra with site factor interpolation (Fpga, Fa, Fv), damping ratio adjustment, and 2/3-rule minimum overlay
- **Site-Specific Spectrum** — Design response spectrum from site-specific PGA, Ss, S1 with no site factor interpolation (Fpga = Fa = Fv = 1.0) and 2/3-rule minimum overlay

### ACI 350 Modules (library only — no web UI)
- **Effective Liquid Weights** — Impulsive and convective weights per Eq. 9.2.1a and 9.2.1b
- **Centers of Gravity** — Heights to the centers of gravity, excluding and including base pressure (Sections 9.2.2 and 9.2.3). Note the returned keys are `EPB` (sic) and `IBP`
- **Dynamic Properties** — Tank impulsive and convective periods

### Ground Motion Modules
- **PEER GM Record** — Upload one or more PEER NGA strong-motion records (.AT2, .VT2, .DT2, .txt, .acc, .csv) and plot the acceleration time-histories together, with CSV export, a combined PNG, and a per-record "PNG (each)" export
- **PEER → SGS Converter** — Batch-convert PEER NGA records (.AT2, .txt) to SGS format (plain decimal, no scientific notation), with time-history preview and per-record .sgs downloads
- **SGS Generator** — Build a MIDAS `.sgs` from any two-column data: paste from Excel, load a CSV/TSV/`.sgs`, or supply one column of values plus a Δt. Time-history, response-spectrum, or custom axis labels, with a live chart and file preview

### MIDAS `.sgs` Export
Every spectrum module writes a MIDAS `.sgs` alongside its PNG and CSV — NSCP 2015 (design and 1.4× reference), NSCP 2024 (design and MCE_R), ASCE 7 (design, MCE_R, and both 80% lower bounds), the NSCP vs ASCE overlay, DPWH BSDS Level I and II, Site-Specific, and ASCE 41-17 BSE-1E / BSE-2E. Output matches a MIDAS-written file byte for byte: CRLF endings, `<x>TAB,TAB<y>` rows, trailing zeros trimmed, and ASCII-only headers.

### Smart Auto-Fill
Site coefficient results (Ca, Cv, Nv, Zone) automatically populate the Response Spectrum, ADRS, and Base Shear input fields — Ca and Cv to all three, Nv and Zone to Base Shear only — visually indicated by a light green hatch on auto-filled fields.

### Interactive Charts
Every chart supports zoom and pan for inspecting spectra up close: **Ctrl + mouse wheel** (or pinch on touch devices) to zoom, **Shift + drag** to pan, and **double-click** to reset the view. Charts export as hi-res PNG and CSV, and every spectrum chart also writes a MIDAS `.sgs`.

---

## Installation

```bash
pip install apecseismicpy
```

**Note:** PyPI currently ships v0.2 while this repository is at v0.5.0. The DPWH BSDS, NSCP 2024, and ASCE 41-17 modules documented below are available only from source until the next release.

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
# {'na': 1.0, 'nv': 1.2, 'ca': 0.44, 'cv': 0.768}
```

### Response Spectrum

```python
from apecseismicpy import ResponseSpectrum

rs = ResponseSpectrum(ca=0.44, cv=0.768)   # Ca, Cv from the example above
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
# {'period': 0.5572, 'limit': 0.9472}   # limit = 1.70 x period in Zone 4
```

### Base Shear

```python
from apecseismicpy import calculate_base_shear

bs = calculate_base_shear(
    zone=4, nv=1.2, ca=0.44, cv=0.768,
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
# {'pga_cm_s2': 267.091, 'pga_g': 0.272542, 'correction_factor': 1.07}
```

### Redundancy Factor

```python
from apecseismicpy import calculate_redundancy

result = calculate_redundancy(v_struc=500.0, v_element=120.0, ab=200.0, factor=1.25)
# {'r_max': 0.24, 'rho_raw': 0.2028, 'rho_clamped': 1.0, 'rho': 1.0, 'factor': 1.25}
```

### Scaling Base Shear

```python
from apecseismicpy import calculate_scaling

result = calculate_scaling(
    static_shear=4499.4,
    scale_factor=1.0,
    dynamic_data=[{"label": "MAJOR", "x": 106.27, "y": 4499.40}],
)
# {'results': [{'label': 'MAJOR', 'srt': 4500.6548, 'ratio': 0.9997}]}
```

### NSCP 2024 Design Spectrum

```python
from apecseismicpy import SiteCoefficients2024, DesignResponseSpectrum2024

sc = SiteCoefficients2024("D", ss=1.10, s1=0.40)
# sc.calculate() -> {'fa': 1.06, 'fv': 1.6}

rs = DesignResponseSpectrum2024(ss=1.10, s1=0.40, fa=sc.fa(), fv=sc.fv(), tl=4.0)
print(rs.sds, rs.sd1, rs.ts, rs.t0)   # 0.7773  0.4267  0.5489  0.1098

design = rs.generate_spectrum(two_thirds=True, max_period=8.0)   # design level
mce    = rs.generate_spectrum(two_thirds=False, max_period=8.0)  # MCE_R level
```

### ASCE 41-17 BSE-1E / BSE-2E Spectra

```python
from apecseismicpy import Asce41SiteCoefficients, Asce41Spectrum

sc = Asce41SiteCoefficients("D", ss=1.10, s1=0.40, default_site_class=True)
sc.calculate()
# {'fa': 1.2, 'fa_interpolated': 1.06, 'fa_floor_applied': True, 'fv': 1.9,
#  'site_specific_required': True,
#  'site_specific_reason': '§11.4.8 item 3 — Site Class D with S1 = 0.40 >= 0.20. ...'}
# Fa interpolates to 1.06, but Site Class D was DEFAULTED, so the Section
# 11.4.4 floor of 1.2 governs. Pass default_site_class=False when the class
# was determined from a documented investigation.

rs = Asce41Spectrum(ss=1.10, s1=0.40, fa=sc.fa(), fv=sc.fv(), tl=16.0, damping=0.05)
print(rs.ts, rs.t0)                      # 0.5758  0.1152 — common to both levels
print(rs.sa(0.60, level="BSE-2E"))       # 1.2637 g — Collapse Prevention
print(rs.sa(0.60, level="BSE-1E"))       # 0.8425 g — Life Safety (2/3 of BSE-2E)
print(rs.branch_at(0.60))                # 'velocity branch (Ts < T <= TL)'
print(rs.exception2_bound)               # 0.8636 s — 1.5*Ts, the Section 11.4.8 Exc. 2 bound

bse2e = rs.generate_spectrum(level="BSE-2E", max_period=8.0)
```

### ACI 350 Tank Hydrodynamics

```python
from apecseismicpy import effective_liquid_weights, calculate_heights_of_centers_of_gravity

effective_liquid_weights(L=10.0, height=5.0, liquid_weight=1000.0)
# {'impulsive': {'value': 542.3163, 'units': 'kN'},
#  'convective': {'value': 485.0218, 'units': 'kN'}}

calculate_heights_of_centers_of_gravity(l=10.0, h_l=5.0)
# {'EPB': {'hi': 1.875, 'hc': 2.9164}, 'IBP': {'hpi': 3.9849, 'hpc': 4.2914}}
# the excluding-base-pressure key is spelled 'EPB' in the source
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

The package includes a FastAPI web application with a professional engineering UI: interactive charts with zoom/pan, PNG/CSV/MIDAS `.sgs` export, spreadsheet-style data input with Excel paste support, and smart auto-fill between modules. The interface is a single page built with Bootstrap 5, Bootstrap Icons, Chart.js 4 (annotation + zoom plugins), and Inter / JetBrains Mono typography — all via CDN, no build step.

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

### HTTP API

Each calculation is exposed as one `POST /api/*` route taking a JSON body:

`/api/site-coefficients` · `/api/response-spectrum` · `/api/adrs` · `/api/period` · `/api/period-limit` · `/api/base-shear` · `/api/pga` · `/api/redundancy` · `/api/scaling` · `/api/bsds-spectrum` · `/api/site-specific-spectrum` · `/api/nscp2024-spectrum` · `/api/asce-spectrum` · `/api/overlay-spectrum` · `/api/asce41-spectrum`

Every route returns the same envelope — `{"success": true, "data": {...}}` on success, `{"success": false, "error": "..."}` on failure. Request and response schemas are generated from the Pydantic models and served at **/docs** (OpenAPI JSON at **/openapi.json**), which is authoritative if the list above falls behind:

```bash
curl -X POST http://127.0.0.1:8000/api/asce41-spectrum \
  -H "Content-Type: application/json" \
  -d '{"ss": 1.10, "s1": 0.40, "site_class": "D", "tl": 16, "max_period": 8, "period": 0.60}'
```

### Web App Modules

| Module | Description |
|--------|-------------|
| **Site Coefficients** | Na, Nv, Ca, Cv for any zone, source type, and soil profile |
| **Response Spectrum** | NSCP 2015 design spectrum + 1.4x TH reference |
| **ADRS** | ATC-40 capacity spectrum: elastic/reduced ADRS, radial period lines, pushover curve overlay, calculation report |
| **Base Shear** | Lateral force per Eq. 208-8 to 208-10 with the Zone 4 minimum (Eq. 208-11) |
| **Structural Period** | Empirical period with zone-limited upper bound |
| **Redundancy** | Redundancy factor per Section 208.5.6 |
| **PGA** | Peak ground acceleration via Fukushima-Tanaka |
| **Scaling Base Shear** | SRSS dynamic scaling |
| **NSCP 2024 Design Spectrum** | 8th Edition two-parameter spectrum: design and MCE_R curves with Fa/Fv interpolation |
| **ASCE 41 / ASCE 7 Design Spectrum** | General spectrum with the 80% site-specific lower bound at both MCE_R and design level |
| **NSCP vs ASCE 41 Overlay** | NSCP 2015 and ASCE 41 spectra on one axis with their ordinate ratio |
| **ASCE 41-17 BSE-1E / BSE-2E** | Both hazard levels with the Section 11.4.4 Fa floor, B1 damping adjustment, Section 11.4.8 trigger, per-run clause notes, and PNG/CSV/`.sgs` export |
| **BSDS Spectrum** | Level I and Level II spectra with site factors, PNG export, and tab-separated `.txt` data export |
| **Site-Specific Spectrum** | BSDS-shape design spectrum with Fpga = Fa = Fv = 1.0 (site-specific hazard values used directly) |
| **PEER GM Record** | Multi-file PEER NGA time-history plot with CSV/PNG export |
| **PEER → SGS Converter** | Batch PEER .AT2 → .sgs conversion with preview |
| **SGS Generator** | Any two-column data → MIDAS .sgs, with Δt mode, file import, live chart and file preview |

---

## Project Structure

```
seismicpy/
├── app.py                          # FastAPI web application
├── templates/
│   └── index.html                  # Single-page UI (Bootstrap 5 + Chart.js 4)
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
│   ├── nscp2024/
│   │   ├── site_coefficients.py    # 8th Edition Fa, Fv interpolation
│   │   └── response_spectrum.py    # Design and MCE_R spectrum
│   ├── asce/
│   │   └── response_spectrum.py    # ASCE 7 spectrum + 80% lower bound
│   ├── asce41/
│   │   ├── site_coefficients.py    # ASCE 7-16 Fa, Fv + 11.4.4 floor, B1
│   │   └── spectrum.py             # BSE-1E and BSE-2E spectra (2.4.1.7.1)
│   ├── bsds/
│   │   ├── site_factor.py          # Fpga, Fa, Fv interpolation tables
│   │   └── spectrum.py             # Level I and Level II spectrum
│   └── aci350/
│       └── hydrodynamic/           # Tank hydrodynamic analysis (library only)
├── Dockerfile                      # Production container
├── railway.json                    # Railway build + health-check config
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

## Developers

**Albert Pamonag** — Albert Pamonag Engineering Consultancy
- Email: albert@apeconsultancy.net
- Web: [seismic.apeconsultancy.net](https://seismic.apeconsultancy.net)
- Repository: [github.com/albertp16/seismicpy](https://github.com/albertp16/seismicpy)

**Camille Pajarillaga**
