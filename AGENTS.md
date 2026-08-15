# AGENTS.md

Guidance for Codex when working in this repo.

## What this is

`apecseismicpy` is a Python library of seismic-engineering calculations (NSCP 2015, DPWH BSDS, ACI 350 hydrodynamic) plus a FastAPI web app that wraps them in an interactive single-page UI.

Live: https://seismic.apeconsultancy.net — deployed from `main` on Railway via `Dockerfile`.

## Run locally

```bash
py -m uvicorn app:app --reload
# open http://127.0.0.1:8000
```

First-time setup:
```bash
py -m pip install -r requirements.txt
py -m pip install .
```

No test suite; verify changes by exercising the relevant module in the browser.

## Architecture

- **`app.py`** — FastAPI entry point. One Pydantic input model + one `/api/*` POST route per calculation. `GET /` renders `templates/index.html`.
- **`templates/index.html`** — the entire UI (HTML + CSS + vanilla JS, ~4000 lines). Bootstrap 5, Bootstrap Icons, Chart.js 4, chartjs-plugin-annotation, chartjs-plugin-zoom (+ Hammer.js), Google Fonts (Inter / JetBrains Mono) — all via CDN. No build step, no framework, no separate JS files.
- **`apecseismicpy/`** — the library. Each submodule owns one code/standard:
  - `nscp2015/` — site_coefficients, response_spectrum, baseshear, period, pga, redundancy, scaling
  - `nscp2024/` — site_coefficients, response_spectrum (8th Edition, two-parameter Ss/S1)
  - `asce41/` — site_coefficients, spectrum (ASCE 41-17 BSE-1E / BSE-2E)
  - `bsds/` — site_factor, spectrum (DPWH Bridge Seismic Design)
  - `aci350/hydrodynamic/` — loads, period, pressure, provision (tank analysis)
  - Public API is re-exported from `apecseismicpy/__init__.py`.

## UI patterns in index.html

The file is long but follows strict conventions — match them when extending.

### Adding a new module (pane)

1. **Sidebar link** in `<nav class="sidebar">`:
   ```html
   <a class="sidebar-link" data-target="tab-<name>" onclick="switchModule(this)">Label</a>
   ```
2. **Module pane** in `<div class="main-content">`:
   ```html
   <div class="module-pane" id="tab-<name>">
     <div class="module-title">Title</div>
     ...
   </div>
   ```
   `switchModule()` toggles the `.active` class; panes are hidden with `display:none` unless active.

### Editable tables

Tables with class `spread-table` + `td[contenteditable]` get Excel-style paste/copy for free via the global listener near `readSpreadTable`. To read values back, use `readSpreadTable(tableId)` for `{h, x, y}` rows.

### Charts

Chart instances are stored in module-scoped refs (e.g. `adrsChart`, `peerChart`, `sgsChart`) and destroyed before re-rendering. Always follow that pattern to avoid Chart.js memory leaks.

### Download helpers

Two utilities near the bottom of the script block:
- `downloadCanvas(canvasId, filename)` — 3× hi-res PNG export on a white background.
- `downloadCSV(headers, rows, filename)` — builds a CSV blob and triggers download.

Every new chart should get both buttons in its card header (matches the existing PNG/CSV pair pattern — see Response Spectrum, ADRS, PEER GM).

### Auto-fill between modules

When Site Coefficients computes Ca/Cv/Nv, `autoFill(id, value)` writes them into Response Spectrum / ADRS / Base Shear inputs and paints the `.auto-filled` green-hatch indicator. The indicator clears on the user's first manual edit. Use `autoFill` rather than setting `.value` directly when a result in module A should prefill module B.

## Backend patterns

- Every `/api/*` handler: `try { ... return {"success": True, "data": ...} } except Exception as e: return {"success": False, "error": str(e)}`. Frontend calls `postJSON(url, body)` and branches on `r.success`.
- Numeric results that render into `resultCard` are rounded server-side (usually `round(x, 3)` or `round(x, 4)`).
- Response spectrum/ADRS math lives in `ResponseSpectrum.generate_adrs` / `generate_reduced_adrs` / `atc40_reduction` — reuse, don't duplicate.

## Deployment

- `main` → Railway auto-deploy via `Dockerfile` (Python 3.12-slim, `uvicorn --host 0.0.0.0 --port ${PORT:-8000}`).
- Health check hits `/` (see `railway.json`).
- `setup.py` version (currently `0.5.0`) is only meaningful for the PyPI side; bump when publishing a library release, not for every web-app change.

## Conventions

- Commit messages: imperative, sentence case, no scope prefix — e.g. `Add CSV data download for Response Spectrum and ADRS charts`, `Fix TemplateResponse for newer Starlette`. Match what `git log` already uses.
- No separate JS files, no build tooling, no TypeScript — keep everything inline in `index.html` unless the user explicitly asks to split it.
- No test framework is configured. Don't invent one; verify by running the server and exercising the UI.
