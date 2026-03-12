import sys
import datetime
import numpy as np
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional

sys.path.insert(0, ".")

from apecseismicpy.nscp2015.site_coefficients import site_coefficients
from apecseismicpy.nscp2015.response_spectrum import ResponseSpectrum
from apecseismicpy.nscp2015.period import calculateStructuralPeriod
from apecseismicpy.nscp2015.baseshear import calculate_base_shear
from apecseismicpy.aci350.hydrodynamic.loads import (
    effective_liquid_weights,
    calculate_heights_of_centers_of_gravity,
)
from apecseismicpy.aci350.hydrodynamic.period import DynamicProperties

app = FastAPI(title="APEC SeismicPy")
templates = Jinja2Templates(directory="templates")


# ── Pydantic models ──────────────────────────────────────────────────────────

class SiteCoefInput(BaseModel):
    distance: float
    source_type: str   # A, B, C
    soil_type: str     # sa, sb, sc, sd, se
    zone: int          # 2 or 4


class SpectrumInput(BaseModel):
    ca: float
    cv: float
    x_max: float = 5.0
    show_th: bool = False
    T: float = 1.0


class PeriodInput(BaseModel):
    structure_type: str   # concrete, steel, other
    hn: float


class BaseShearInput(BaseModel):
    zone: int
    nv: float
    ca: float
    cv: float
    importance_factor: float
    response_modification: float
    period: float
    weight: float


class TankLoadsInput(BaseModel):
    L: float
    height: float
    liquid_weight: float


class TankDynamicsInput(BaseModel):
    length: float
    hw: float
    tw: float
    wi: float
    wl: float
    hl: float
    hi: float
    ec: float
    gamma_c: float = 23.6
    gamma_l: float = 9.81


# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/site-coefficients")
async def api_site_coefficients(data: SiteCoefInput):
    try:
        sc = site_coefficients(data.distance, data.source_type, data.soil_type, data.zone)
        result = sc.calculate()
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/response-spectrum")
async def api_response_spectrum(data: SpectrumInput):
    try:
        rs = ResponseSpectrum(data.ca, data.cv)
        x, Sa = rs.calculate(x_max=data.x_max)

        # ADRS conversion: T = x * Ts, Sd = Sa*g*T²/(4π²)
        T_actual = x * rs.Ts
        Sd = Sa * 9.81 * T_actual**2 / (4 * np.pi**2)

        T = data.T if data.T > 0 else 1.0
        payload = {
            "x":     x.tolist(),
            "Sa":    Sa.tolist(),
            "Sa_14": (1.4 * Sa).tolist(),
            "Sd":    Sd.tolist(),
            "Ts":    rs.Ts,
            "T0":    rs.T0,
            "sa_max": rs.sa_max,
            "T_02":  0.2 * T / rs.Ts,
            "T_15":  1.5 * T / rs.Ts,
        }
        return {"success": True, "data": payload}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/period")
async def api_period(data: PeriodInput):
    try:
        period = calculateStructuralPeriod(data.structure_type, data.hn)
        return {"success": True, "data": {"period": round(period, 4)}}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/base-shear")
async def api_base_shear(data: BaseShearInput):
    try:
        bs = calculate_base_shear(
            data.zone, data.nv, data.ca, data.cv,
            data.importance_factor, data.response_modification,
            data.period, data.weight,
        )
        result = {
            "total":   round(bs.totalBaseShear(), 3),
            "max":     round(bs.maxBaseShear(), 3),
            "min":     round(bs.minBaseShear(), 3),
        }
        if data.zone == 4:
            result["max_z4"]    = round(bs.maxBaseShearZ4(), 3)
            result["governing"] = round(bs.governingShear(), 3)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/tank-loads")
async def api_tank_loads(data: TankLoadsInput):
    try:
        weights = effective_liquid_weights(data.L, data.height, data.liquid_weight)
        heights = calculate_heights_of_centers_of_gravity(data.L, data.height)
        return {"success": True, "data": {"weights": weights, "heights": heights}}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/tank-dynamics")
async def api_tank_dynamics(data: TankDynamicsInput):
    try:
        dp = DynamicProperties(
            data.length, data.hw, data.tw, data.wi, data.wl,
            data.hl, data.hi, data.ec, data.gamma_c, data.gamma_l,
        )
        result = {
            "mw":   dp.compute_mw(),
            "mi":   dp.compute_mi(),
            "h_eq": dp.compute_h(),
            "k":    dp.compute_k(),
            "mt":   dp.compute_mt(),
            "Ti":   dp.compute_ti(),
            "Tc":   dp.compute_tc(),
        }
        # Round the value fields for display
        for key in result:
            result[key]["value"] = round(result[key]["value"], 4)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ── LaTeX Report ─────────────────────────────────────────────────────────────

class ReportInput(BaseModel):
    project_name: str = "Seismic Design"
    project_no:   str = ""
    engineer:     str = "Engineer"
    checker:      str = ""
    date:         str = ""
    # Site
    distance:    float
    source_type: str
    soil_type:   str
    zone:        int
    # Structure
    structure_type: str = "concrete"
    hn:             float
    # Base shear
    importance_factor:     float
    response_modification: float
    weight:                float
    # Tank (optional)
    include_tank:  bool = False
    L:             Optional[float] = None
    tank_height:   Optional[float] = None
    liquid_weight: Optional[float] = None


def _e(s: str) -> str:
    """Escape special LaTeX characters."""
    for ch, rep in [("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"),
                    ("$", r"\$"), ("#", r"\#"), ("_", r"\_"),
                    ("{", r"\{"), ("}", r"\}"), ("~", r"\textasciitilde{}"),
                    ("^", r"\textasciicircum{}")]:
        s = s.replace(ch, rep)
    return s


def _v(val, d: int = 3) -> str:
    return str(round(float(val), d))


def build_report(data: ReportInput) -> str:
    # ── compute everything ───────────────────────────────────────────────────
    sc    = site_coefficients(data.distance, data.source_type, data.soil_type, data.zone)
    coefs = sc.calculate()
    na, nv, ca, cv = coefs["na"], coefs["nv"], coefs["ca"], coefs["cv"]

    ct_map = {"concrete": 0.0731, "steel": 0.0853}
    ct     = ct_map.get(data.structure_type, 0.0488)
    T_s    = calculateStructuralPeriod(data.structure_type, data.hn)

    rs = ResponseSpectrum(ca, cv)
    bs = calculate_base_shear(data.zone, nv, ca, cv,
                               data.importance_factor,
                               data.response_modification,
                               T_s, data.weight)
    v_total = bs.totalBaseShear()
    v_max   = bs.maxBaseShear()
    v_min   = bs.minBaseShear()

    date_str  = data.date or datetime.date.today().strftime("%B %d, %Y")
    soil_disp = data.soil_type.upper()
    I, R, W   = data.importance_factor, data.response_modification, data.weight

    # ── helpers ──────────────────────────────────────────────────────────────
    pn = _e(data.project_name)
    pno = _e(data.project_no)
    eng = _e(data.engineer)
    chk = _e(data.checker)
    dt  = _e(date_str)

    # ── preamble ─────────────────────────────────────────────────────────────
    doc = r"""\documentclass[11pt,a4paper]{article}
\usepackage[top=2.5cm,bottom=2.5cm,left=2.8cm,right=2.8cm]{geometry}
\usepackage{booktabs,amsmath,array,fancyhdr,xcolor,tabularx}
\usepackage[hidelinks]{hyperref}

\definecolor{apecblue}{RGB}{15,45,107}
\pagestyle{fancy}\fancyhf{}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\footrulewidth}{0.4pt}
\fancyhead[L]{\small\textbf{\textcolor{apecblue}{APEC Engineering Consultancy}}}
\fancyhead[R]{\small Seismic Design Calculation --- NSCP 2015}
\fancyfoot[L]{\small """ + pno + r"""}
\fancyfoot[C]{\small CONFIDENTIAL}
\fancyfoot[R]{\small Page \thepage}
\setlength{\parindent}{0pt}\setlength{\parskip}{6pt}

\begin{document}

% ── Title block ───────────────────────────────────────────────────────────────
\begin{center}
  \rule{\linewidth}{2pt}\\[0.4cm]
  {\LARGE\bfseries\textcolor{apecblue}{Seismic Design Calculation}}\\[0.15cm]
  {\large NSCP 2015 / ACI 350.3}\\[0.4cm]
  \rule{\linewidth}{0.5pt}\\[0.3cm]
  \begin{tabular}{@{}ll@{\hspace{2.5cm}}ll@{}}
    \textbf{Project:}  & """ + pn  + r""" & \textbf{Project No.:} & """ + pno + r""" \\[3pt]
    \textbf{Engineer:} & """ + eng + r""" & \textbf{Checker:}     & """ + chk + r""" \\[3pt]
    \textbf{Date:}     & """ + dt  + r""" & \textbf{Software:}    & APEC SeismicPy v0.2 \\
  \end{tabular}\\[0.4cm]
  \rule{\linewidth}{2pt}
\end{center}
\vspace{0.4cm}

% ══════════════════════════════════════════════════════════════════════════════
\section{Design Parameters}
% ══════════════════════════════════════════════════════════════════════════════
\begin{tabular}{@{}p{7.5cm}ll@{}}
  \toprule
  \textbf{Parameter} & \textbf{Value} & \textbf{Reference} \\
  \midrule
  Seismic Zone               & Zone """ + str(data.zone) + r"""         & NSCP 2015 Table 208-3 \\
  Soil Profile Type          & """ + soil_disp + r"""                    & NSCP 2015 Table 208-2 \\
  Seismic Source Type        & Type """ + data.source_type + r"""        & NSCP 2015 Table 208-4 \\
  Distance to Seismic Source & """ + _v(data.distance) + r""" km        & --- \\
  Importance Factor, $I$     & """ + _v(I) + r"""                        & NSCP 2015 Table 208-1 \\
  Response Modification, $R$ & """ + _v(R) + r"""                        & NSCP 2015 Table 208-11 \\
  Seismic Weight, $W$        & """ + _v(W, 1) + r""" kN                  & --- \\
  \bottomrule
\end{tabular}

% ══════════════════════════════════════════════════════════════════════════════
\section{Site Seismicity Coefficients (NSCP 2015 \S208.3)}
% ══════════════════════════════════════════════════════════════════════════════
\begin{tabular}{@{}p{3.5cm}cll@{}}
  \toprule
  \textbf{Coefficient} & \textbf{Value} & \textbf{Description} & \textbf{Table} \\
  \midrule
  $N_a$ & """ + _v(na) + r""" & Near-source acceleration factor  & 208-4 \\
  $N_v$ & """ + _v(nv) + r""" & Near-source velocity factor      & 208-5 \\
  $C_a$ & """ + _v(ca) + r""" & Seismic coefficient (accel.)     & 208-7 \\
  $C_v$ & """ + _v(cv) + r""" & Seismic coefficient (velocity)   & 208-8 \\
  \bottomrule
\end{tabular}

% ══════════════════════════════════════════════════════════════════════════════
\section{Structural Period --- Method A (NSCP 2015 Eq.\ 208-23)}
% ══════════════════════════════════════════════════════════════════════════════
For a \textit{""" + data.structure_type + r"""} lateral system: $C_t = """ + _v(ct, 4) + r"""$,
$h_n = """ + _v(data.hn, 2) + r"""$ m.
\begin{equation}
  T = C_t \cdot h_n^{3/4}
    = """ + _v(ct, 4) + r""" \times """ + _v(data.hn, 2) + r"""^{0.75}
    = \mathbf{""" + _v(T_s, 4) + r"""\ \text{s}}
\end{equation}

% ══════════════════════════════════════════════════════════════════════════════
\section{Design Response Spectrum (NSCP 2015 \S208.6, Fig.\ 208-3)}
% ══════════════════════════════════════════════════════════════════════════════
\begin{align}
  S_{a,\max} &= 2.5\,C_a = 2.5 \times """ + _v(ca) + r"""
              = \mathbf{""" + _v(rs.sa_max, 4) + r"""\ \text{g}} \\[4pt]
  T_s        &= \frac{C_v}{S_{a,\max}} = \frac{""" + _v(cv) + r"""}{""" + _v(rs.sa_max, 4) + r"""}
              = \mathbf{""" + _v(rs.Ts, 4) + r"""\ \text{s}} \\[4pt]
  T_0        &= 0.2\,T_s = 0.2 \times """ + _v(rs.Ts, 4) + r"""
              = \mathbf{""" + _v(rs.T0, 4) + r"""\ \text{s}}
\end{align}
\begin{tabular}{@{}p{5cm}cc@{}}
  \toprule
  \textbf{Parameter} & \textbf{Value} & \textbf{Units} \\
  \midrule
  $T_0$            & """ + _v(rs.T0, 4) + r"""  & s \\
  $T_s$            & """ + _v(rs.Ts, 4) + r"""  & s \\
  $S_{a,\max}$     & """ + _v(rs.sa_max, 4) + r""" & g \\
  $T$ (structure)  & """ + _v(T_s, 4) + r"""    & s \\
  \bottomrule
\end{tabular}

% ══════════════════════════════════════════════════════════════════════════════
\section{Seismic Base Shear (NSCP 2015 \S208.4.8)}
% ══════════════════════════════════════════════════════════════════════════════
\subsection*{Total Design Base Shear (Eq.\ 208-8)}
\begin{equation}
  V = \frac{C_v\,I}{R\,T}\,W
    = \frac{""" + _v(cv) + r""" \times """ + _v(I) + r"""}{""" + _v(R) + r""" \times """ + _v(T_s, 4) + r"""} \times """ + _v(W, 1) + r"""
    = \mathbf{""" + _v(v_total, 2) + r"""\ \text{kN}}
\end{equation}
\subsection*{Maximum Base Shear (Eq.\ 208-9)}
\begin{equation}
  V_{\max} = \frac{2.5\,C_a\,I}{R}\,W
    = \frac{2.5 \times """ + _v(ca) + r""" \times """ + _v(I) + r"""}{""" + _v(R) + r"""} \times """ + _v(W, 1) + r"""
    = \mathbf{""" + _v(v_max, 2) + r"""\ \text{kN}}
\end{equation}
\subsection*{Minimum Base Shear (Eq.\ 208-10)}
\begin{equation}
  V_{\min} = 0.11\,C_a\,I\,W
    = 0.11 \times """ + _v(ca) + r""" \times """ + _v(I) + r""" \times """ + _v(W, 1) + r"""
    = \mathbf{""" + _v(v_min, 2) + r"""\ \text{kN}}
\end{equation}
"""

    if data.zone == 4:
        v_max_z4 = bs.maxBaseShearZ4()
        v_gov    = bs.governingShear()
        doc += r"""\subsection*{Zone 4 Additional Check (Eq.\ 208-11)}
\begin{equation}
  V_{\max,Z4} = \frac{0.8\,Z\,N_v\,I}{R}\,W
    = \frac{0.8 \times 0.4 \times """ + _v(nv) + r""" \times """ + _v(I) + r"""}{""" + _v(R) + r"""} \times """ + _v(W, 1) + r"""
    = \mathbf{""" + _v(v_max_z4, 2) + r"""\ \text{kN}}
\end{equation}
"""
    else:
        v_gov = None

    doc += r"""
\subsection*{Summary}
\begin{center}
\begin{tabular}{@{}p{8cm}r@{\ }l@{}}
  \toprule
  \textbf{Equation} & \multicolumn{2}{c}{\textbf{Value}} \\
  \midrule
  $V$ --- Total (Eq.\ 208-8)          & """ + _v(v_total, 2) + r""" & kN \\
  $V_{\max}$ --- Maximum (Eq.\ 208-9) & """ + _v(v_max, 2)   + r""" & kN \\
  $V_{\min}$ --- Minimum (Eq.\ 208-10)& """ + _v(v_min, 2)   + r""" & kN \\
"""
    if v_gov is not None:
        doc += (r"  $V_{\max,Z4}$ --- Zone 4 Max (Eq.\ 208-11) & "
                + _v(v_max_z4, 2) + r" & kN \\" + "\n")
        doc += (r"  \midrule" + "\n"
                + r"  \textbf{Governing Design Shear} & \textbf{"
                + _v(v_gov, 2) + r"} & \textbf{kN} \\" + "\n")
    doc += r"""  \bottomrule
\end{tabular}
\end{center}
"""

    # ── optional tank section ────────────────────────────────────────────────
    if data.include_tank and data.L and data.tank_height and data.liquid_weight:
        wts  = effective_liquid_weights(data.L, data.tank_height, data.liquid_weight)
        hts  = calculate_heights_of_centers_of_gravity(data.L, data.tank_height)
        wi   = wts["impulsive"]["value"]
        wc   = wts["convective"]["value"]
        ratio = data.L / data.tank_height

        doc += r"""
% ══════════════════════════════════════════════════════════════════════════════
\section{Tank Hydrodynamic Analysis (ACI 350.3 \S9.2)}
% ══════════════════════════════════════════════════════════════════════════════
\begin{tabular}{@{}p{6.5cm}ccc@{}}
  \toprule
  \textbf{Parameter} & \textbf{Symbol} & \textbf{Value} & \textbf{Unit} \\
  \midrule
  Base length (parallel to motion) & $L$    & """ + _v(data.L, 2)           + r""" & m  \\
  Liquid height                    & $H_L$  & """ + _v(data.tank_height, 2) + r""" & m  \\
  Total liquid weight              & $W_L$  & """ + _v(data.liquid_weight, 1)+ r""" & kN \\
  $L/H_L$ ratio                   & ---    & """ + _v(ratio, 3)            + r""" & --- \\
  \bottomrule
\end{tabular}

\subsection*{Effective Liquid Weights (Eq.\ 9.2.1)}
\begin{align}
  \frac{W_i}{W_L} &= \frac{\tanh(0.866\,L/H_L)}{0.866\,L/H_L}
                   = """ + _v(wi / data.liquid_weight, 4) + r"""
    \quad\Rightarrow\quad W_i = \mathbf{""" + _v(wi, 2) + r"""\ \text{kN}} \\[4pt]
  \frac{W_c}{W_L} &= 0.264\,\tfrac{L}{H_L}\tanh\!\left(\tfrac{3.16\,H_L}{L}\right)
                   = """ + _v(wc / data.liquid_weight, 4) + r"""
    \quad\Rightarrow\quad W_c = \mathbf{""" + _v(wc, 2) + r"""\ \text{kN}}
\end{align}

\subsection*{Heights of Centers of Gravity (\S9.2.2--9.2.3)}
\begin{tabular}{@{}llcc@{}}
  \toprule
  \textbf{Case} & \textbf{Symbol} & \textbf{Value (m)} & \textbf{Description} \\
  \midrule
  EBP Impulsive  & $h_i$  & """ + _v(hts["EPB"]["hi"],  4) + r""" & Excluding base pressure \\
  EBP Convective & $h_c$  & """ + _v(hts["EPB"]["hc"],  4) + r""" & Excluding base pressure \\
  IBP Impulsive  & $h'_i$ & """ + _v(hts["IBP"]["hpi"], 4) + r""" & Including base pressure \\
  IBP Convective & $h'_c$ & """ + _v(hts["IBP"]["hpc"], 4) + r""" & Including base pressure \\
  \bottomrule
\end{tabular}
"""

    doc += r"""
\vspace{1cm}\hrule\vspace{0.3cm}
\begin{center}
  \small\textit{Generated by APEC SeismicPy v0.2. Results shall be reviewed by a licensed structural engineer.}
\end{center}
\end{document}
"""
    return doc


@app.post("/api/generate-report")
async def api_generate_report(data: ReportInput):
    try:
        content  = build_report(data)
        filename = (data.project_name or "seismic_report").replace(" ", "_") + ".tex"
        return Response(
            content=content,
            media_type="application/x-tex",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as e:
        return {"success": False, "error": str(e)}
