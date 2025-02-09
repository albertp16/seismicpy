import math

class dynamicProperties:
    def __init__(self, length,hw,tw,wi,wl,hl,hi,ec, gamma_c=23.6,gamma_l=9.81, g=9.81):
        self.g = g  # Gravity acceleration (m/s^2)
        self.length = length  # Length in Parallel Motion
        self.hw = hw  # Wall Height (meter)
        self.tw = tw  # Wall thickness (average) (meters)
        self.wi = wi  # Implusive Weight
        self.wl = wl  # Liquid Weight
        self.hl = hl  # Liquid Height      
        self.ec = ec  # Modulus of Elasciticity of Concrete (MPa)
        self.hi = hi  # Height influence
        # self.mi = mi  # Mass influence
        # self.wi = wi  # Load influence
        # self.wl = wl  # Load width
        # self.l = l  # Span length
        # self.hl = hl  # Height level
        self.gamma_c = gamma_c  # Concrete density (kN/m^3)
        self.gamma_l = gamma_l  # Live load density
        # self.lambda_ = lambda_  # Wave number
    def compute_mw(self):
        '''
        Per ACI 350 R.9.2.4 wall weight per linear meter
        '''

        if self.hw <= 0 or self.tw <= 0:
            raise ValueError("hw and tw must be greater than zero.")
        KN_TO_N = 1000  # Convert kN to N
        
        unit_weight = (self.gamma_c * KN_TO_N) / self.g  # Convert kN/m³ to kg/m³
        value = self.hw * self.tw * unit_weight  # Compute mass per unit length
        units = "kg/m" 
        return {
            "value" : value,
            "units" : units
        }

    def compute_mi(self):
        '''
        Per ACI 350 R.9.2.4 impulsive weight of contents per linear meter
        '''
        KN_TO_N = 1000  # Convert kN to N
        unit_weight = (self.gamma_l * KN_TO_N) / self.g  # Convert kN/m³ to kg/m³
        value = ((self.wi / self.wl) * (self.length / 2) * self.hl * unit_weight) * 1000
        units = "kg/m" 
        return {
            "value" : value,
            "units" : units
        }
    def compute_h(self):
        """
        equivalent cantilever wall height
        """
        mw = self.compute_mw()["value"]
        mi = self.compute_mi()["value"]
        value = ((0.5*self.hw*mw)+(self.hi*mi))/(mw+mi)
        units = "m"
        return {
            "value" : value,
            "units" : units
        }
    
    def compute_k(self):
        """
        wall stiffness per linear meter

        """
        ec_kpa = self.ec * 1000 #convert from MPa to KPa
        value = (ec_kpa / 4000) * math.pow(self.tw / self.compute_h()["value"], 3)
        units = "kN/m"
        return {
            "value" : value,
            "units" : units
        }
    def compute_mt(self):
        """
        total weight per linear meter
        """
        value = self.compute_mw()["value"] + self.compute_mi()["value"]
        units = "kg/m"
        return {
            "value" : value,
            "units" : units
        }
    def compute_ti(self):
        mt = self.compute_mt()["value"]
        k = self.compute_k()["value"]
        value = 2*math.pi*math.sqrt(mt/k)
        units = "s"
        return {
            "value" : value,
            "units" : units
        }
    def compute_tc(self):
        """
        Natural Period of the first convective mode of sloshing
        """
        value = (2 * math.pi) / math.sqrt(3.16 * self.g * math.tanh(3.16 * (self.hl / self.l)))
        units = "s"
        return {
            "value" : value,
            "units" : units
        }
    # def compute_lambda(self):
    #     if self.hl is None or self.l is None:
    #         raise ValueError("hl and l must be set.")
    #     if self.l <= 0 or self.hl <= 0:
    #         raise ValueError("l and hl must be greater than zero.")
    #     return math.sqrt(3.16 * self.g * math.tanh(3.16 * self.hl / self.l))
