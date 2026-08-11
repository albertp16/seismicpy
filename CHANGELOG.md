# Changelog

All notable changes to APEC SeismicPy are documented here.

---

## [Unreleased]

### Added
- ASCE 41-17 group with a BSE-1E / BSE-2E Spectra tab: both hazard levels from one set of inputs (BSE-1E = 2/3 BSE-2E per §2.4.1.4), ASCE 7-16 site coefficients including the §11.4.4 floor Fa >= 1.2 for a defaulted Site Class D, the Eq. (2-3) damping adjustment B1, the §11.4.8 site-specific trigger with its 1.5Ts Exception 2 bound, per-run clause notes, and PNG/CSV/MIDAS `.sgs` export
- `apecseismicpy.asce41` package (`Asce41SiteCoefficients`, `Asce41Spectrum`, `damping_factor_b1`) and the `/api/asce41-spectrum` endpoint
- ASCE 41 / ASCE 7 Design Spectrum tab and `apecseismicpy.asce` (`DesignResponseSpectrumASCE`): the general two-parameter spectrum with the 80% site-specific lower bound of ASCE 7-16 §21.3 / ASCE 41-17 §2.4.2, plotted at both MCE_R and design level, via `/api/asce-spectrum`
- NSCP 2015 vs ASCE 41 overlay tab and `/api/overlay-spectrum`
- NSCP 2024 (8th Edition) group with a Design Spectrum tab: Fa/Fv site-class interpolation, design and MCE_R curves, control periods T0/Ts/TL
- `apecseismicpy.nscp2024` package (`SiteCoefficients2024`, `DesignResponseSpectrum2024`) and the `/api/nscp2024-spectrum` endpoint
- Site-Specific Spectrum tab (DPWH BSDS group): design response spectrum built directly from site-specific PGA, Ss, and S1 with no site-factor interpolation (Fpga = Fa = Fv = 1.0), with 2/3 minimum overlay and PNG/CSV export
- `/api/site-specific-spectrum` endpoint reusing `SeismicDesignResponse` with unit site factors
- PEER GM: per-record PNG export — a PNG button on each record in the list plus a "PNG (each)" header button that exports one hi-res chart per record

### Removed
- Story Shear and Overturning Moment diagram tabs

### Fixed
- README: documented the NSCP 2024, ASCE 41-17, and ACI 350 module families, dropped the removed Story Shear and Overturning Moment entries, corrected the Site Coefficients and Structural Period example outputs, and added the HTTP API route list

---

## [0.5.0] - 2026-03-29

### Added
- Auto-fill: site coefficient results (Ca, Cv, Nv, Zone) now automatically populate Response Spectrum and Base Shear input fields
- Light green hatch indicator on auto-filled fields to distinguish extracted values from manual input
- Hatch clears when the user manually edits an auto-filled field

### Fixed
- Railway deployment: replaced editable install with standard `pip install` in Dockerfile
- Removed conflicting deploy configs (Procfile, runtime.txt, railway.toml) in favor of single Dockerfile + railway.json
- setup.py gracefully handles missing README.md during Docker build

---

## [0.4.0] - 2026-03-28

### Added
- Story Drift tab with limit line input and TH1-TH7 load case support
- Story Acceleration tab with limit line input and TH1-TH7 load case support

---

## [0.3.0] - 2026-03-27

### Added
- Story Displacement plot module with separate story table and TH1-TH7 load case tables
- Grey-on-none styling for empty displacement cells

### Changed
- Revamped Story Displacement UI with separate story table per load case

---

## [0.2.0] - 2026-03-26

### Added
- Sidebar dashboard with collapsible groups (NSCP 2015, DPWH BSDS, Diagrams)
- Story Shear and Overturning Moment diagram modules with spreadsheet tables
- Structural Period calculator with zone-limited upper bound (NSCP 2015 Section 208.5.2.2)
- Redundancy factor calculator (NSCP 2015 Section 208.5.6)
- PGA calculator using Fukushima-Tanaka attenuation model
- Scaling Base Shear module with SRSS dynamic analysis support
- DPWH BSDS Design Spectrum tab with Level II and Level I charts, site factor table, 2/3 minimum overlay, and PNG/data export

### Changed
- Redesigned UI from single-page form to multi-module sidebar dashboard
- Replaced LaTeX report generation with interactive web charts

### Removed
- Tank analysis module (moved to separate project)
- NumPy dependency (replaced with pure Python math)

---

## [0.1.0] - Initial Release

### Added
- NSCP 2015 site coefficients (Na, Nv, Ca, Cv) with interpolation tables
- NSCP 2015 design response spectrum generator
- NSCP 2015 base shear calculator (Eq. 208-8 through 208-11)
- FastAPI web application with Chart.js visualizations
- Python package installable via pip
