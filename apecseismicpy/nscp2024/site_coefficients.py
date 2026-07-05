class SiteCoefficients2024:
    """
    NSCP 8th Edition (2024) short/long-period site coefficients Fa and Fv.

    Follows the ASCE 7 two-parameter approach: Fa and Fv are read from the
    site-class tables against the mapped spectral accelerations Ss and S1,
    with linear interpolation between tabulated breakpoints.

    Attributes:
        site_class: 'A', 'B', 'C', 'D', or 'E'.
        ss: mapped short-period (0.2 s) spectral acceleration.
        s1: mapped long-period (1.0 s) spectral acceleration.
    """

    SITE_CLASSES = ("A", "B", "C", "D", "E")

    # Fa — short-period site coefficient (Table 208A-x), breakpoints on Ss.
    FA_SS = [0.25, 0.50, 0.75, 1.00, 1.25]
    FA_TABLE = {
        "A": [0.8, 0.8, 0.8, 0.8, 0.8],
        "B": [1.0, 1.0, 1.0, 1.0, 1.0],
        "C": [1.2, 1.2, 1.1, 1.0, 1.0],
        "D": [1.6, 1.4, 1.2, 1.1, 1.0],
        "E": [2.5, 1.7, 1.2, 0.9, 0.9],
    }

    # Fv — long-period site coefficient (Table 208A-y), breakpoints on S1.
    FV_S1 = [0.10, 0.20, 0.30, 0.40, 0.50]
    FV_TABLE = {
        "A": [0.8, 0.8, 0.8, 0.8, 0.8],
        "B": [1.0, 1.0, 1.0, 1.0, 1.0],
        "C": [1.7, 1.6, 1.5, 1.4, 1.3],
        "D": [2.4, 2.0, 1.8, 1.6, 1.5],
        "E": [3.5, 3.2, 2.8, 2.4, 2.4],
    }

    def __init__(self, site_class, ss, s1):
        site_class = str(site_class).upper()
        if site_class not in self.SITE_CLASSES:
            raise ValueError("site_class must be one of A, B, C, D, E.")
        if ss < 0 or s1 < 0:
            raise ValueError("Ss and S1 must be non-negative.")

        self.site_class = site_class
        self.ss = ss
        self.s1 = s1

    @staticmethod
    def interpolate_factor(value, reference_values, factors):
        """Linearly interpolate a coefficient, clamping outside the table."""
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

    def fa(self):
        return self.interpolate_factor(self.ss, self.FA_SS, self.FA_TABLE[self.site_class])

    def fv(self):
        return self.interpolate_factor(self.s1, self.FV_S1, self.FV_TABLE[self.site_class])

    def calculate(self):
        return {"fa": self.fa(), "fv": self.fv()}
