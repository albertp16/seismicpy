import math

class DynamicProperties:
    """
    A class to compute various dynamic properties of a wall-liquid system based on ACI 350 R.9.2.4.
    
    Attributes:
        length (float): Length of the wall in parallel motion (m).
        hw (float): Wall height (m).
        tw (float): Wall thickness (m).
        wi (float): Impulsive weight (kN).
        wl (float): Liquid weight (kN).
        hl (float): Liquid height (m).
        hi (float): Height influence factor.
        ec (float): Modulus of Elasticity of Concrete (MPa).
        gamma_c (float): Concrete density (default 23.6 kN/m³).
        gamma_l (float): Liquid density (default 9.81 kN/m³).
        g (float): Acceleration due to gravity (default 9.81 m/s²).
    """
    
    def __init__(self, length, hw, tw, wi, wl, hl, hi, ec, gamma_c=23.6, gamma_l=9.81, g=9.81):
        if length <= 0 or hw <= 0 or tw <= 0 or wl <= 0 or hl <= 0 or ec <= 0:
            raise ValueError("All physical dimensions and material properties must be greater than zero.")
        
        self.length = length
        self.hw = hw
        self.tw = tw
        self.wi = wi
        self.wl = wl
        self.hl = hl
        self.hi = hi
        self.ec = ec
        self.gamma_c = gamma_c
        self.gamma_l = gamma_l
        self.g = g
    
    def compute_mw(self):
        """
        Computes the wall weight per linear meter based on ACI 350 R.9.2.4.
        
        Returns:
            dict: Value of wall weight (kg/m) and units.
        """
        KN_TO_N = 1000  # Convert kN to N
        unit_weight = (self.gamma_c * KN_TO_N) / self.g  # Convert kN/m³ to kg/m³
        value = self.hw * self.tw * unit_weight  # Compute mass per unit length
        return {"value": value, "units": "kg/m"}
    
    def compute_mi(self):
        """
        Computes the impulsive weight of contents per linear meter based on ACI 350 R.9.2.4.
        
        Returns:
            dict: Value of impulsive weight (kg/m) and units.
        """
        KN_TO_N = 1000
        unit_weight = (self.gamma_l * KN_TO_N) / self.g
        value = ((self.wi / self.wl) * (self.length / 2) * self.hl * unit_weight) * 1000
        return {"value": value, "units": "kg/m"}
    
    def compute_h(self):
        """
        Computes the equivalent cantilever wall height.
        
        Returns:
            dict: Equivalent height (m) and units.
        """
        mw = self.compute_mw()["value"]
        mi = self.compute_mi()["value"]
        value = ((0.5 * self.hw * mw) + (self.hi * mi)) / (mw + mi)
        return {"value": value, "units": "m"}
    
    def compute_k(self):
        """
        Computes the wall stiffness per linear meter.
        
        Returns:
            dict: Stiffness value (kN/m) and units.
        """
        ec_kpa = self.ec * 1000  # Convert MPa to kPa
        h_eq = self.compute_h()["value"]
        value = (ec_kpa / 4000) * math.pow(self.tw / h_eq, 3)
        return {"value": value, "units": "kN/m"}
    
    def compute_mt(self):
        """
        Computes the total weight per linear meter.
        
        Returns:
            dict: Total weight (kg/m) and units.
        """
        value = self.compute_mw()["value"] + self.compute_mi()["value"]
        return {"value": value, "units": "kg/m"}
    
    def compute_ti(self):
        """
        Computes the natural period of impulsive motion.
        
        Returns:
            dict: Period of impulsive motion (s) and units.
        """
        mt = self.compute_mt()["value"]
        k = self.compute_k()["value"]
        value = 2 * math.pi * math.sqrt(mt / k)
        return {"value": value, "units": "s"}
    
    def compute_tc(self):
        """
        Computes the natural period of the first convective mode of sloshing.
        
        Returns:
            dict: Period of convective motion (s) and units.
        """
        value = (2 * math.pi) / math.sqrt(3.16 * self.g * math.tanh(3.16 * (self.hl / self.length)))
        return {"value": value, "units": "s"}