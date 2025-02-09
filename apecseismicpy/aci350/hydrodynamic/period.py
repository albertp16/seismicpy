import math

class dynamicProperties:
    def __init__(self, hw, tw, gamma_c=23.6, g=9.81):
        self.g = g  # Gravity acceleration (m/s^2)
        self.hw = hw  # Wall Height (meter)
        self.tw = tw  # Wall thickness (average) (meters)
        # self.h = h  # Effective height
        # self.hw = hw  # Wall height
        # self.mw = mw  # Mass of wall
        # # self.hi = hi  # Height influence
        # self.mi = mi  # Mass influence
        # self.wi = wi  # Load influence
        # self.wl = wl  # Load width
        # self.l = l  # Span length
        # self.hl = hl  # Height level
        self.gamma_c = gamma_c  # Concrete density (kN/m^3)
        # self.gamma_l = gamma_l  # Live load density
        # self.lambda_ = lambda_  # Wave number
    def compute_mw(self):
        '''
        Per ACI 350 R.9.2.4
        wall weight per linear meter
        '''

        if self.hw <= 0 or self.tw <= 0:
            raise ValueError("hw and tw must be greater than zero.")
        value = self.hw * self.tw * (self.gamma_c / self.g)
        units = "kg/m" 

        return {
            "value" : value,
            "units" : units
        }

    # def compute_mi(self):
    #     '''
    #     Per ACI 350 R.9.2.4
    #     '''
    #     if self.wi is None or self.wl is None or self.l is None or self.hl is None or self.gamma_l is None:
    #         raise ValueError("wi, wl, l, hl, and gamma_l must be set.")
    #     if self.wl <= 0 or self.l <= 0 or self.hl <= 0:
    #         raise ValueError("wl, l, and hl must be greater than zero.")
    #     return ((self.wi / self.wl) * (self.l / 2) * self.hl * (self.gamma_l / self.g)) * 1000
    
    # def compute_k(self):
    #     if self.tw is None or self.h is None or self.ec is None:
    #         raise ValueError("tw, h, and ec must be set.")
    #     if self.tw <= 0 or self.h <= 0:
    #         raise ValueError("tw and h must be greater than zero.")
    #     return (self.ec / (4 * 1000)) * math.pow(self.tw / self.h, 3)

    # def compute_h(self):
    #     if self.hw is None or self.mw is None or self.hi is None or self.mi is None:
    #         raise ValueError("hw, mw, hi, and mi must be set.")
    #     if self.mw + self.mi == 0:
    #         raise ValueError("Total mass must be greater than zero.")
    #     return (self.hw * self.mw + self.hi * self.mi) / (self.mw + self.mi)

    # def compute_omega_i(self, k, m):
    #     if m <= 0:
    #         raise ValueError("Mass must be greater than zero.")
    #     return math.sqrt(k / m)

    # def compute_ti(self, omega_i):
    #     if omega_i <= 0:
    #         raise ValueError("omega_i must be greater than zero.")
    #     return 2 * math.pi / omega_i

    # def compute_omega_c(self):
    #     if self.lambda_ is None or self.l is None:
    #         raise ValueError("lambda_ and l must be set.")
    #     if self.l <= 0:
    #         raise ValueError("l must be greater than zero.")
    #     return self.lambda_ / math.sqrt(self.l)

    # def compute_tc(self):
    #     if self.lambda_ is None or self.l is None:
    #         raise ValueError("lambda_ and l must be set.")
    #     if self.lambda_ <= 0:
    #         raise ValueError("lambda_ must be greater than zero.")
    #     return (2 * math.pi / self.lambda_) * math.sqrt(self.l)

    # def compute_lambda(self):
    #     if self.hl is None or self.l is None:
    #         raise ValueError("hl and l must be set.")
    #     if self.l <= 0 or self.hl <= 0:
    #         raise ValueError("l and hl must be greater than zero.")
    #     return math.sqrt(3.16 * self.g * math.tanh(3.16 * self.hl / self.l))
