import sys
import numpy as np
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
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
