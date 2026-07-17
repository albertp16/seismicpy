from ..nscp2024.response_spectrum import DesignResponseSpectrum2024


class DesignResponseSpectrumASCE(DesignResponseSpectrum2024):
    """
    ASCE 7 / ASCE 41 general design response spectrum with the site-specific
    lower bound.

    The spectrum itself is the ASCE 7 two-parameter construction already
    implemented by DesignResponseSpectrum2024 (which NSCP 2024 adopts):

        Sms = Fa * Ss              Sm1 = Fv * S1            (MCE_R level)
        Sds = (2/3) * Sms          Sd1 = (2/3) * Sm1        (design level)
        Ts  = Sd1 / Sds            T0  = 0.2 * Ts

    What this class adds is the lower-bound curve. ASCE 7-16 Section 21.3 and
    ASCE 41-17 Section 2.4.2 both require that a design spectrum developed from
    a site-specific ground-motion hazard analysis not be taken as less than 80%
    of the spectrum built by the general procedure. That 80% floor is a separate
    curve plotted against the general spectrum — it does not replace the 2/3
    MCE_R-to-design factor, which still applies.
    """

    LOWER_BOUND_FACTOR = 0.80

    def sa_lower_bound(self, t):
        """80% of the general-procedure design Sa (g) at period t."""
        return self.LOWER_BOUND_FACTOR * self.sa(t, two_thirds=True)

    def generate_lower_bound_spectrum(self, max_period=8.0, step=0.01):
        """Return period/acceleration arrays for the 80% lower-bound curve."""
        spectrum = self.generate_spectrum(two_thirds=True, max_period=max_period,
                                          step=step)
        return {
            "periods": spectrum["periods"],
            "accelerations": [self.LOWER_BOUND_FACTOR * sa
                              for sa in spectrum["accelerations"]],
        }
