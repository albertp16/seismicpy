class SeismicSiteFactor:
    """
    Compute site factors based on DPWH-BSDS / NSCP 2015.

    Attributes:
        ground_type: Site classification ('I', 'II', or 'III').
        pga: Peak ground acceleration.
        ss: Spectral acceleration at 0.2s (short period).
        s1: Spectral acceleration at 1.0s (long period).
    """

    def __init__(self, ground_type, pga=None, ss=None, s1=None):
        if ground_type not in ("I", "II", "III"):
            raise ValueError("ground_type must be 'I', 'II', or 'III'.")
        if pga is not None and pga < 0:
            raise ValueError("PGA cannot be negative.")
        if ss is not None and ss < 0:
            raise ValueError("Ss cannot be negative.")
        if s1 is not None and s1 < 0:
            raise ValueError("S1 cannot be negative.")

        self.ground_type = ground_type
        self.pga = pga
        self.ss = ss
        self.s1 = s1

        self.site_factors = {
            'I':   {"0.00": 1.2, "0.10": 1.2, "0.20": 1.2, "0.30": 1.1, "0.40": 1.1, "0.50": 1.0, "0.80": 1.0},
            'II':  {"0.00": 1.6, "0.10": 1.6, "0.20": 1.4, "0.30": 1.2, "0.40": 1.0, "0.50": 0.9, "0.80": 0.85},
            'III': {"0.00": 2.5, "0.10": 2.5, "0.20": 1.7, "0.30": 1.2, "0.40": 0.9, "0.50": 0.8, "0.80": 0.75},
        }

    def interpolate_site_factor(self):
        if self.pga is None:
            raise ValueError("Cannot interpolate site factor because 'pga' is None.")
        factors_dict = self.site_factors.get(self.ground_type)
        if factors_dict is None:
            return None
        numeric_pga_keys = sorted([float(k) for k in factors_dict.keys()])
        factor_values = [factors_dict[f"{k:.2f}"] for k in numeric_pga_keys]
        return self.interpolate_factor(self.pga, numeric_pga_keys, factor_values)

    def get_site_factor_fa(self):
        if self.ss is None:
            raise ValueError("Cannot compute Fa because 'ss' is None.")
        fa_table = {
            'I':   [1.2, 1.2, 1.1, 1.0, 1.0, 1.0],
            'II':  [1.6, 1.4, 1.2, 1.0, 0.9, 0.85],
            'III': [2.5, 1.7, 1.2, 0.9, 0.8, 0.75],
        }
        ss_values = [0.25, 0.50, 0.75, 1.00, 1.25, 2.00]
        return self.interpolate_factor(self.ss, ss_values, fa_table[self.ground_type])

    def get_site_factor_fv(self):
        if self.s1 is None:
            raise ValueError("Cannot compute Fv because 's1' is None.")
        fv_table = {
            'I':   [1.7, 1.6, 1.5, 1.4, 1.4, 1.4],
            'II':  [2.4, 2.0, 1.8, 1.6, 1.5, 1.5],
            'III': [3.5, 3.2, 2.8, 2.4, 2.4, 2.0],
        }
        s1_values = [0.10, 0.20, 0.30, 0.40, 0.50, 0.80]
        return self.interpolate_factor(self.s1, s1_values, fv_table[self.ground_type])

    @staticmethod
    def interpolate_factor(value, reference_values, factors):
        if value <= reference_values[0]:
            return factors[0]
        if value >= reference_values[-1]:
            return factors[-1]
        for i in range(len(reference_values) - 1):
            if reference_values[i] <= value < reference_values[i + 1]:
                return factors[i] + (
                    (value - reference_values[i])
                    * (factors[i + 1] - factors[i])
                    / (reference_values[i + 1] - reference_values[i])
                )
        return factors[-1]
