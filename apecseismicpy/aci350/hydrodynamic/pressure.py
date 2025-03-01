import math

def seismic_response_coefficient_ci(Ca, Z, Nv, Cv, s, Ti, Ts):
    if Ti <= Ts:
        return max(2.5 * Ca, 1.6 * Z * Nv)
    else:
        return max((Cv * s) / Ti, 1.6 * Z * Nv)

def seismic_response_coefficient_cc(Ca, Cv, s, Tc, Ts):
    if Tc <= (1.6 * s) / Ts:
        return min((1.5 * Cv * s) / Tc, 3.75 * Ca)
    else:
        return (6 * Ca * s ** 2) / Tc ** 2

def vertical_ground_motion_component(Ca, Z, Nv):
    return max(Ca, 1.6 * Z * Nv)

def effective_spectral_vertical_response_acceleration(Ct, l, b, Ri):
    return (Ct * l * b) / Ri

def effective_mass_coefficient(L, HL):
    return min(0.0151 * (L / HL) ** 2 - 0.1908 * (L / HL) + 1.021, 1.0)

def total_impulsive_force(Ca, Z, Nv, W, Ri, Cv, s, Ti, Ts):
    if Ti <= Ts:
        return max(2.5 * Ca, 1.6 * Z * Nv) * (W / Ri)
    else:
        return max((Cv * s) / Ti, 0.56 * Ca * Ri, 1.6 * Z * Nv) * (W / Ri)

def total_convective_force(Ca, Cv, s, Tc, Ts, Wc, Rc):
    if Tc > (1.6 * s ** 2) / Ts:
        return min((6 * Ca * s ** 2) / Tc ** 2, 3.75 * Ca) * (Wc / Rc)
    else:
        return min((1.5 * Cv * s) / Tc, 3.75 * Ca) * (Wc / Rc)

def wall_inertia_coefficient_dynamic(epsilon, I, Ci, Ri):
    return (epsilon * I * Ci) / Ri

def hydrodynamic_pressures(L, B, tw_ave, HW, gamma_C, tslab):
    Ww = ((L + 2 * tw_ave) * (B + 2 * tw_ave) - (L * B)) * HW * gamma_C
    Wr = (L * B) * tslab * gamma_C
    return Ww, Wr

def impulsive_pressures(Pi, HL, B, y):
    return 0.5 * Pi / (HL ** 2 * B) * (4 * HL - 6 * y - ((6 * HL - 12 * y) * (y / HL)))

def convective_pressures(Pc, HL, B, y):
    return 0.5 * Pc / (HL ** 2 * B) * (4 * HL - 6 * y - ((6 * HL - 12 * y) * (y / HL)))

def hydrostatic_pressure(gamma_L, HL):
    return gamma_L * HL

def effect_of_vertical_acceleration(u_v, q_hy):
    return u_v * q_hy

def srss_pressure(Pi_top, Pw, Pc_top):
    return math.sqrt((Pi_top + Pw) ** 2 + Pc_top ** 2)

def moment_calculation(Pi, hi, Pw, HW, Pr, tslab, Pc, hc):
    return math.sqrt((Pi * hi + Pw * HW * 0.5 + Pr * (HW - 0.5 * tslab)) ** 2 + Pc * hc ** 2)

def srss_mat(Mo, Mb, L, B):
    return (6 * (Mo - Mb)) / (L ** 2 * B)

