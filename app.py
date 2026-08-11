import sys
import math
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

sys.path.insert(0, ".")

from apecseismicpy.nscp2015.site_coefficients import site_coefficients
from apecseismicpy.nscp2015.response_spectrum import ResponseSpectrum, atc40_reduction
from apecseismicpy.nscp2015.period import calculateStructuralPeriod, calculatePeriodWithLimit
from apecseismicpy.nscp2015.baseshear import calculate_base_shear
from apecseismicpy.nscp2015.pga import calculate_pga
from apecseismicpy.nscp2015.redundancy import calculate_redundancy
from apecseismicpy.nscp2015.scaling import calculate_scaling
from apecseismicpy.bsds import SeismicSiteFactor, SeismicDesignResponse
from apecseismicpy.nscp2024 import SiteCoefficients2024, DesignResponseSpectrum2024
from apecseismicpy.asce41 import Asce41SiteCoefficients, Asce41Spectrum

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


class BsdsInput(BaseModel):
    pga: float
    ss: float
    s1: float
    site_class: str        # I, II, III
    damping_ratio: float = 0.02
    max_period: float = 8.0


class SiteSpecificSpectrumInput(BaseModel):
    pga: float
    ss: float
    s1: float
    max_period: float = 8.0


class Nscp2024SpectrumInput(BaseModel):
    ss: float
    s1: float
    site_class: str = "D"     # A, B, C, D, E
    tl: float = 4.0           # long-period transition period
    max_period: float = 8.0
    fa: float = 0.0           # optional override; 0 = compute from tables
    fv: float = 0.0           # optional override; 0 = compute from tables


class Asce41SpectrumInput(BaseModel):
    ss: float
    s1: float
    site_class: str = "D"          # A, B, C, D, E
    default_site_class: bool = True  # Site Class D defaulted per §11.4.3?
    tl: float = 16.0               # long-period transition period
    damping: float = 0.05          # effective viscous damping ratio
    max_period: float = 8.0
    fa: float = 0.0                # optional override; 0 = compute from tables
    fv: float = 0.0                # optional override; 0 = compute from tables
    period: float = 0.0            # optional structure period for the demand readout


class PgaInput(BaseModel):
    magnitude: float
    distance: float
    soil_type: str = "medium_soil"  # rock, hard_soil, medium_soil, soft_soil


class RedundancyInput(BaseModel):
    v_struc: float
    v_element: float
    ab: float
    factor: float = 1.25  # 1.25 for SMRF, 1.50 for Others


class ScalingInput(BaseModel):
    static_shear: float
    scale_factor: float = 1.0
    dynamic_data: list  # [{"label": "MAJOR", "x": 106.27, "y": 4499.40}, ...]


class PeriodLimitInput(BaseModel):
    structure_type: str
    hn: float
    zone: int = 4


class AdrsInput(BaseModel):
    ca: float
    cv: float
    structure_type: str = ""  # A, B, C or empty = no reduction
    dy: float = 0.0
    ay: float = 0.0
    dpi: float = 0.0
    api_val: float = 0.0


# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


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
        T_actual = [xi * rs.Ts for xi in x]
        Sd = [s * 9.81 * t**2 / (4 * math.pi**2) for s, t in zip(Sa, T_actual)]

        T = data.T if data.T > 0 else 1.0
        payload = {
            "x":     x,
            "Sa":    Sa,
            "Sa_14": [1.4 * s for s in Sa],
            "Sd":    Sd,
            "Ts":    rs.Ts,
            "T0":    rs.T0,
            "sa_max": rs.sa_max,
            "T_02":  0.2 * T / rs.Ts,
            "T_15":  1.5 * T / rs.Ts,
        }
        return {"success": True, "data": payload}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/adrs")
async def api_adrs(data: AdrsInput):
    try:
        rs = ResponseSpectrum(data.ca, data.cv)
        Sd, Sa, T_actual = rs.generate_adrs(x_max=5.0)

        # Radial period lines
        g = 9.81
        Sd_max = max(Sd)
        Sa_max_chart = max(Sa) * 1.1
        radial_periods = [rs.Ts]
        for t in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]:
            if t not in radial_periods:
                radial_periods.append(t)
        radial_periods.sort()

        radial_lines = []
        for t in radial_periods:
            if t <= 0:
                continue
            slope = 4 * math.pi ** 2 / (g * t ** 2)
            sd_end = min(Sd_max, Sa_max_chart / slope)
            sa_end = slope * sd_end
            radial_lines.append({
                "T": round(t, 3),
                "points": [{"x": 0, "y": 0}, {"x": round(sd_end, 6), "y": round(sa_end, 6)}],
            })

        payload = {
            "Sd": Sd,
            "Sa": Sa,
            "Ts": rs.Ts,
            "T0": rs.T0,
            "sa_max": rs.sa_max,
            "radial_lines": radial_lines,
        }

        # ATC-40 reduction
        if data.structure_type and data.dpi > 0 and data.api_val > 0:
            red = atc40_reduction(data.dy, data.ay, data.dpi, data.api_val,
                                  data.structure_type)
            Sd_r, Sa_r, _ = rs.generate_reduced_adrs(red["SRA"], red["SRV"])

            # Interpolate dpn and apn at the performance point
            dpn = None
            apn = None
            for i in range(1, len(Sd_r)):
                if Sd_r[i] >= data.dpi:
                    frac = (data.dpi - Sd_r[i - 1]) / (Sd_r[i] - Sd_r[i - 1]) \
                        if Sd_r[i] != Sd_r[i - 1] else 0
                    apn = Sa_r[i - 1] + frac * (Sa_r[i] - Sa_r[i - 1])
                    dpn = data.dpi
                    break

            payload["reduction"] = {
                **red,
                "Sd_r": Sd_r,
                "Sa_r": Sa_r,
                "dpn": round(dpn, 4) if dpn is not None else None,
                "apn": round(apn, 4) if apn is not None else None,
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


@app.post("/api/period-limit")
async def api_period_limit(data: PeriodLimitInput):
    try:
        result = calculatePeriodWithLimit(data.structure_type, data.hn, data.zone)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/pga")
async def api_pga(data: PgaInput):
    try:
        result = calculate_pga(data.magnitude, data.distance, data.soil_type)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/redundancy")
async def api_redundancy(data: RedundancyInput):
    try:
        result = calculate_redundancy(data.v_struc, data.v_element, data.ab, data.factor)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/scaling")
async def api_scaling(data: ScalingInput):
    try:
        result = calculate_scaling(data.static_shear, data.scale_factor, data.dynamic_data)
        return {"success": True, "data": result}
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


@app.post("/api/bsds-spectrum")
async def api_bsds_spectrum(data: BsdsInput):
    try:
        sf = SeismicSiteFactor(data.site_class, data.pga, data.ss, data.s1)
        fpga = sf.interpolate_site_factor()
        fa = sf.get_site_factor_fa()
        fv = sf.get_site_factor_fv()

        sdr = SeismicDesignResponse(data.pga, fpga, data.ss, data.s1, fa, fv)

        level2 = sdr.generate_level2_spectrum(max_period=data.max_period)
        level1 = sdr.generate_level1_spectrum(
            data.site_class,
            damping_ratio=data.damping_ratio,
            max_period=data.max_period,
        )

        return {
            "success": True,
            "data": {
                "fpga": round(fpga, 4),
                "fa": round(fa, 4),
                "fv": round(fv, 4),
                "A_s": round(level2["A_s"], 4),
                "S_DS": round(level2["S_DS"], 4),
                "S_D1": round(level2["S_D1"], 4),
                "T_s": round(level2["T_s"], 4),
                "T_0": round(level2["T_0"], 4),
                "level2": {
                    "periods": level2["periods"],
                    "accelerations": level2["accelerations"],
                },
                "level1": {
                    "periods": level1["periods"],
                    "accelerations": level1["accelerations"],
                    "cz": level1["cz"],
                    "cD": level1["cD"],
                },
            },
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/site-specific-spectrum")
async def api_site_specific_spectrum(data: SiteSpecificSpectrumInput):
    try:
        # Site-specific hazard values are used directly: Fpga = Fa = Fv = 1.0
        sdr = SeismicDesignResponse(data.pga, 1.0, data.ss, data.s1, 1.0, 1.0)
        spectrum = sdr.generate_level2_spectrum(max_period=data.max_period)

        return {
            "success": True,
            "data": {
                "A_s": round(spectrum["A_s"], 4),
                "S_DS": round(spectrum["S_DS"], 4),
                "S_D1": round(spectrum["S_D1"], 4),
                "T_s": round(spectrum["T_s"], 4),
                "T_0": round(spectrum["T_0"], 4),
                "periods": spectrum["periods"],
                "accelerations": spectrum["accelerations"],
            },
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/nscp2024-spectrum")
async def api_nscp2024_spectrum(data: Nscp2024SpectrumInput):
    try:
        sc = SiteCoefficients2024(data.site_class, data.ss, data.s1)
        fa = data.fa if data.fa > 0 else sc.fa()
        fv = data.fv if data.fv > 0 else sc.fv()

        rs = DesignResponseSpectrum2024(data.ss, data.s1, fa, fv, tl=data.tl)
        design = rs.generate_spectrum(two_thirds=True, max_period=data.max_period)
        mce = rs.generate_spectrum(two_thirds=False, max_period=data.max_period)

        return {
            "success": True,
            "data": {
                "fa": round(fa, 4),
                "fv": round(fv, 4),
                "sms": round(rs.sms, 4),
                "sm1": round(rs.sm1, 4),
                "sds": round(rs.sds, 4),
                "sd1": round(rs.sd1, 4),
                "t0": round(rs.t0, 4),
                "ts": round(rs.ts, 4),
                "tl": round(rs.tl, 4),
                "design": {
                    "periods": design["periods"],
                    "accelerations": design["accelerations"],
                },
                "mce": {
                    "periods": mce["periods"],
                    "accelerations": mce["accelerations"],
                },
            },
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/asce41-spectrum")
async def api_asce41_spectrum(data: Asce41SpectrumInput):
    """ASCE 41-17 BSE-1E (Life Safety) and BSE-2E (Collapse Prevention) spectra."""
    try:
        sc = Asce41SiteCoefficients(
            data.site_class, data.ss, data.s1,
            default_site_class=data.default_site_class,
        )
        coef = sc.calculate()
        fa_overridden = data.fa > 0
        fv_overridden = data.fv > 0
        fa = data.fa if fa_overridden else coef["fa"]
        fv = data.fv if fv_overridden else coef["fv"]

        rs = Asce41Spectrum(data.ss, data.s1, fa, fv,
                            tl=data.tl, damping=data.damping)
        bse2e = rs.generate_spectrum(level="BSE-2E", max_period=data.max_period)
        bse1e = rs.generate_spectrum(level="BSE-1E", max_period=data.max_period)

        demand = None
        if data.period > 0:
            demand = {
                "period": round(data.period, 4),
                "sa_bse2e": round(rs.sa(data.period, level="BSE-2E"), 4),
                "sa_bse1e": round(rs.sa(data.period, level="BSE-1E"), 4),
                "branch": rs.branch_at(data.period),
                "beyond_exception2_bound": data.period > rs.exception2_bound,
            }

        return {
            "success": True,
            "data": {
                "fa": round(fa, 4),
                "fv": round(fv, 4),
                "fa_interpolated": round(coef["fa_interpolated"], 4),
                "fa_floor_applied": coef["fa_floor_applied"] and not fa_overridden,
                "fa_overridden": fa_overridden,
                "fv_overridden": fv_overridden,
                "b1": round(rs.b1, 4),
                "damping": data.damping,
                "sxs_bse2e": round(rs.sxs_bse2e, 4),
                "sx1_bse2e": round(rs.sx1_bse2e, 4),
                "sxs_bse1e": round(rs.sxs_bse1e, 4),
                "sx1_bse1e": round(rs.sx1_bse1e, 4),
                "t0": round(rs.t0, 4),
                "ts": round(rs.ts, 4),
                "tl": round(rs.tl, 4),
                "exception2_bound": round(rs.exception2_bound, 4),
                "site_specific_required": coef["site_specific_required"],
                "site_specific_reason": coef["site_specific_reason"],
                "demand": demand,
                "bse2e": {
                    "periods": bse2e["periods"],
                    "accelerations": bse2e["accelerations"],
                },
                "bse1e": {
                    "periods": bse1e["periods"],
                    "accelerations": bse1e["accelerations"],
                },
            },
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
