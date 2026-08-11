import math


class Asce41SiteCoefficients:
    """
    ASCE 41-17 site coefficients Fa and Fv.

    ASCE 41-17 §2.4.1.6 refers Fa and Fv to Section 11.4 of ASCE 7 — the whole
    section, not the two tables in isolation. This class therefore carries both
    the tabulated interpolation (ASCE 7-16 Tables 11.4-1 / 11.4-2) and the
    §11.4.4 floor that attaches when Site Class D is the *default* class of
    §11.4.3 (no soil investigation performed):

        "Where Site Class D is selected as the default site class per Section
        11.4.3, the value of Fa shall not be less than 1.2."

    Cells of the tables that read "See Section 11.4.8" carry no tabulated
    value; asking for one raises ValueError rather than returning a guess.

    Attributes:
        site_class: 'A', 'B', 'C', 'D' or 'E'.
        ss: mapped short-period (0.2 s) spectral acceleration, g.
        s1: mapped long-period (1.0 s) spectral acceleration, g.
        default_site_class: True when the class was *defaulted*, not determined.
    """

    SITE_CLASSES = ("A", "B", "C", "D", "E")

    # Fa — ASCE 7-16 Table 11.4-1, breakpoints on Ss. None = "See §11.4.8".
    FA_SS = [0.25, 0.50, 0.75, 1.00, 1.25, 1.50]
    FA_TABLE = {
        "A": [0.8, 0.8, 0.8, 0.8, 0.8, 0.8],
        "B": [0.9, 0.9, 0.9, 0.9, 0.9, 0.9],
        "C": [1.3, 1.3, 1.2, 1.2, 1.2, 1.2],
        "D": [1.6, 1.4, 1.2, 1.1, 1.0, 1.0],
        "E": [2.4, 1.7, 1.3, None, None, None],
    }

    # Fv — ASCE 7-16 Table 11.4-2, breakpoints on S1. None = "See §11.4.8".
    FV_S1 = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60]
    FV_TABLE = {
        "A": [0.8, 0.8, 0.8, 0.8, 0.8, 0.8],
        "B": [0.8, 0.8, 0.8, 0.8, 0.8, 0.8],
        "C": [1.5, 1.5, 1.5, 1.5, 1.5, 1.4],
        "D": [2.4, 2.2, 2.0, 1.9, 1.8, 1.7],
        "E": [4.2, None, None, None, None, None],
    }

    FA_FLOOR_DEFAULT_D = 1.2

    def __init__(self, site_class, ss, s1, default_site_class=True):
        site_class = str(site_class).upper()
        if site_class not in self.SITE_CLASSES:
            raise ValueError("site_class must be one of A, B, C, D, E.")
        if ss <= 0:
            raise ValueError("Ss must be positive.")
        if s1 < 0:
            raise ValueError("S1 must be non-negative.")

        self.site_class = site_class
        self.ss = ss
        self.s1 = s1
        self.default_site_class = bool(default_site_class)

    @staticmethod
    def interpolate_factor(value, reference_values, factors, coefficient="Fa"):
        """Linearly interpolate a coefficient, clamping outside the table.

        Raises ValueError when the value falls in a cell that reads
        "See Section 11.4.8" — a site-specific ground motion procedure is
        required there and no tabulated value exists.
        """
        if any(f is None for f in factors):
            first_none = factors.index(None)
            if value > reference_values[first_none - 1]:
                raise ValueError(
                    "%s is not tabulated at this value — the table cell reads "
                    "'See Section 11.4.8'. A site-specific ground motion "
                    "procedure (ASCE 7-16 Ch. 21) is required." % coefficient
                )
            factors = factors[:first_none]
            reference_values = reference_values[:first_none]

        if value <= reference_values[0]:
            return float(factors[0])
        if value >= reference_values[-1]:
            return float(factors[-1])
        for i in range(len(reference_values) - 1):
            if reference_values[i] <= value < reference_values[i + 1]:
                return float(factors[i]) + (
                    (value - reference_values[i])
                    * (float(factors[i + 1]) - float(factors[i]))
                    / (reference_values[i + 1] - reference_values[i])
                )
        return float(factors[-1])

    def fa_interpolated(self):
        """Fa straight off Table 11.4-1, before the §11.4.4 floor."""
        return self.interpolate_factor(
            self.ss, self.FA_SS, self.FA_TABLE[self.site_class], "Fa")

    def fa_floor_applies(self):
        """True when ASCE 7-16 §11.4.4 raises Fa to 1.2."""
        return (
            self.site_class == "D"
            and self.default_site_class
            and self.fa_interpolated() < self.FA_FLOOR_DEFAULT_D
        )

    def fa(self):
        """Governing Fa — the interpolated value or the §11.4.4 floor."""
        if self.fa_floor_applies():
            return self.FA_FLOOR_DEFAULT_D
        return self.fa_interpolated()

    def fv(self):
        return self.interpolate_factor(
            self.s1, self.FV_S1, self.FV_TABLE[self.site_class], "Fv")

    def requires_site_specific(self):
        """ASCE 7-16 §11.4.8 — is a site-specific ground motion study triggered?

        Returns (triggered, reason). Exception 2 permits the tabulated
        coefficients provided the seismic response coefficient is amplified by
        1.5 for periods beyond 1.5*Ts — see ``Asce41Spectrum.exception2_bound``.
        """
        if self.site_class == "E" and self.ss >= 1.0:
            return True, ("§11.4.8 item 2 — Site Class E with Ss = %.2f >= 1.0."
                          % self.ss)
        if self.site_class in ("D", "E") and self.s1 >= 0.20:
            return True, ("§11.4.8 item 3 — Site Class %s with S1 = %.2f >= 0.20. "
                          "Exception 2 available." % (self.site_class, self.s1))
        return False, "Not triggered."

    def calculate(self):
        triggered, reason = self.requires_site_specific()
        return {
            "fa": self.fa(),
            "fa_interpolated": self.fa_interpolated(),
            "fa_floor_applied": self.fa_floor_applies(),
            "fv": self.fv(),
            "site_specific_required": triggered,
            "site_specific_reason": reason,
        }


def damping_factor_b1(damping=0.05):
    """ASCE 41-17 Eq. (2-3): B1 = 4 / (5.6 - ln(100 * beta)).

    beta is the effective viscous damping ratio (0.05 = 5%). B1 = 1.0 at
    beta = 5% to within 0.24%, which is why 5%-damped spectra are used
    unadjusted in practice.
    """
    if damping <= 0 or damping >= 1:
        raise ValueError("damping ratio must be between 0 and 1 (exclusive).")
    denominator = 5.6 - math.log(100.0 * damping)
    if denominator <= 0:
        raise ValueError("damping ratio is too high for Eq. (2-3).")
    return 4.0 / denominator
