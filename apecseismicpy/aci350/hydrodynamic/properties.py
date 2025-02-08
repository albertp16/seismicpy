import numpy as np
import math

def compute_k(ec, tw, h):
    """
    Compute the spring constant k based on material properties.
    
    Parameters:
    ec (float): Young's modulus (Pa)
    tw (float): Web thickness (m)
    h (float): Section height (m)
    
    Returns:
    float: Spring constant (N/m)
    """
    if tw <= 0 or h <= 0:
        raise ValueError("tw and h must be greater than zero.")
    return (ec / (4 * 1000)) * math.pow(tw / h, 3)

def compute_h(hw, mw, hi, mi):
    """
    Compute the effective height h.
    
    Parameters:
    hw (float): Wall height factor (m)
    mw (float): Wall mass (kg)
    hi (float): Influence height (m)
    mi (float): Influence mass (kg)
    
    Returns:
    float: Effective height (m)
    """
    if mw + mi == 0:
        raise ValueError("Total mass must be greater than zero.")
    return (hw * mw + hi * mi) / (mw + mi)

def compute_mw(hw, tw, gamma_c, g):
    """
    Compute the mass of the wall.
    
    Parameters:
    hw (float): Wall height (m)
    tw (float): Web thickness (m)
    gamma_c (float): Unit weight (kN/m^3)
    g (float): Gravity acceleration (m/s^2)
    
    Returns:
    float: Wall mass (kg)
    """
    if hw <= 0 or tw <= 0:
        raise ValueError("hw and tw must be greater than zero.")
    return hw * tw * (gamma_c / g)

def compute_mi(wi, wl, l, hl, gamma_l, g):
    """
    Compute the mass of the influence area.
    
    Parameters:
    wi (float): Influence weight (kN)
    wl (float): Total weight (kN)
    l (float): Span length (m)
    hl (float): Characteristic height (m)
    gamma_l (float): Unit weight (kN/m^3)
    g (float): Gravity acceleration (m/s^2)
    
    Returns:
    float: Influence mass (kg)
    """
    if wl <= 0 or l <= 0 or hl <= 0:
        raise ValueError("wl, l, and hl must be greater than zero.")
    return ((wi / wl) * (l / 2) * hl * (gamma_l / g)) * 1000

def compute_omega_i(k, m):
    """
    Compute natural frequency omega_i.
    
    Parameters:
    k (float): Spring constant (N/m)
    m (float): Mass (kg)
    
    Returns:
    float: Natural frequency (rad/s)
    """
    if m <= 0:
        raise ValueError("Mass must be greater than zero.")
    return math.sqrt(k / m)

def compute_ti(omega_i):
    """
    Compute period ti.
    
    Parameters:
    omega_i (float): Natural frequency (rad/s)
    
    Returns:
    float: Period (s)
    """
    if omega_i <= 0:
        raise ValueError("omega_i must be greater than zero.")
    return 2 * math.pi / omega_i

def compute_omega_c(lambda_, l):
    """
    Compute omega_c.
    
    Parameters:
    lambda_ (float): Wave number
    l (float): Characteristic length (m)
    
    Returns:
    float: Circular frequency (rad/s)
    """
    if l <= 0:
        raise ValueError("l must be greater than zero.")
    return lambda_ / math.sqrt(l)

def compute_tc(lambda_, l):
    """
    Compute period tc.
    
    Parameters:
    lambda_ (float): Wave number
    l (float): Characteristic length (m)
    
    Returns:
    float: Period (s)
    """
    if lambda_ <= 0:
        raise ValueError("lambda must be greater than zero.")
    return (2 * math.pi / lambda_) * math.sqrt(l)

def compute_lambda(g, hl, l):
    """
    Compute wave number lambda.
    
    Parameters:
    g (float): Gravity acceleration (m/s^2)
    hl (float): Characteristic height (m)
    l (float): Characteristic length (m)
    
    Returns:
    float: Wave number
    """
    if l <= 0 or hl <= 0:
        raise ValueError("l and hl must be greater than zero.")
    return math.sqrt(3.16 * g * math.tanh(3.16 * hl / l))