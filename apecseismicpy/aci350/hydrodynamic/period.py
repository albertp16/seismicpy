import math

class dynamic:
    def __init__(self, g=9.81):
        self.g = g  # Default gravity acceleration (m/s^2)

    def compute_k(self, ec, tw, h):
        """
        Compute the spring constant k based on material properties.
        """
        if tw <= 0 or h <= 0:
            raise ValueError("tw and h must be greater than zero.")
        return (ec / (4 * 1000)) * math.pow(tw / h, 3)

    def compute_h(self, hw, mw, hi, mi):
        """
        Compute the effective height h.
        """
        if mw + mi == 0:
            raise ValueError("Total mass must be greater than zero.")
        return (hw * mw + hi * mi) / (mw + mi)

    def compute_mw(self, hw, tw, gamma_c):
        """
        Compute the mass of the wall.
        """
        if hw <= 0 or tw <= 0:
            raise ValueError("hw and tw must be greater than zero.")
        return hw * tw * (gamma_c / self.g)

    def compute_mi(self, wi, wl, l, hl, gamma_l):
        """
        Compute the mass of the influence area.
        """
        if wl <= 0 or l <= 0 or hl <= 0:
            raise ValueError("wl, l, and hl must be greater than zero.")
        return ((wi / wl) * (l / 2) * hl * (gamma_l / self.g)) * 1000

    def compute_omega_i(self, k, m):
        """
        Compute natural frequency omega_i.
        """
        if m <= 0:
            raise ValueError("Mass must be greater than zero.")
        return math.sqrt(k / m)

    def compute_ti(self, omega_i):
        """
        Compute period ti.
        """
        if omega_i <= 0:
            raise ValueError("omega_i must be greater than zero.")
        return 2 * math.pi / omega_i

    def compute_omega_c(self, lambda_, l):
        """
        Compute omega_c.
        """
        if l <= 0:
            raise ValueError("l must be greater than zero.")
        return lambda_ / math.sqrt(l)

    def compute_tc(self, lambda_, l):
        """
        Compute period tc.
        """
        if lambda_ <= 0:
            raise ValueError("lambda must be greater than zero.")
        return (2 * math.pi / lambda_) * math.sqrt(l)

    def compute_lambda(self, hl, l):
        """
        Compute wave number lambda.
        """
        if l <= 0 or hl <= 0:
            raise ValueError("l and hl must be greater than zero.")
        return math.sqrt(3.16 * self.g * math.tanh(3.16 * hl / l))
