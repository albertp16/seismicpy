class DesignResponseSpectrum2024:
    """
    NSCP 8th Edition (2024) design response spectrum.

    Built from the mapped spectral accelerations Ss, S1 and the short/long-period
    site coefficients Fa, Fv following the ASCE 7 two-parameter approach.

    Spectral parameters
    -------------------
        Sms = Fa * Ss              Sm1 = Fv * S1            (MCE_R level)
        Sds = (2/3) * Sms          Sd1 = (2/3) * Sm1        (design level)
        Ts  = Sd1 / Sds            T0  = 0.2 * Ts
        TL  = long-period transition period (input)

    Spectrum branches (design level)
    --------------------------------
        T < T0        : Sa = Sds * (0.4 + 0.6 * T / T0)
        T0 <= T <= Ts : Sa = Sds
        Ts <  T <= TL : Sa = Sd1 / T
        T > TL        : Sa = Sd1 * TL / T^2
    """

    def __init__(self, ss, s1, fa, fv, tl=4.0):
        if ss <= 0:
            raise ValueError("Ss must be positive.")
        if s1 < 0:
            raise ValueError("S1 must be non-negative.")
        if fa <= 0 or fv <= 0:
            raise ValueError("Fa and Fv must be positive.")
        if tl <= 0:
            raise ValueError("TL must be positive.")

        self.ss = ss
        self.s1 = s1
        self.fa = fa
        self.fv = fv
        self.tl = tl

        # MCE_R spectral accelerations
        self.sms = fa * ss
        self.sm1 = fv * s1

        # Design spectral accelerations (2/3 of MCE_R)
        self.sds = (2.0 / 3.0) * self.sms
        self.sd1 = (2.0 / 3.0) * self.sm1

        # Control periods (independent of the 2/3 factor)
        self.ts = self.sd1 / self.sds if self.sds > 0 else 0.0
        self.t0 = 0.2 * self.ts

    def sa(self, t, two_thirds=True):
        """Spectral acceleration (g) at period t. two_thirds=False → MCE_R level."""
        sds = self.sds if two_thirds else self.sms
        sd1 = self.sd1 if two_thirds else self.sm1

        if self.ts <= 0:
            return 0.0
        if t < self.t0:
            return sds * (0.4 + 0.6 * t / self.t0)
        if t <= self.ts:
            return sds
        if t <= self.tl:
            return sd1 / t
        return sd1 * self.tl / (t ** 2)

    def generate_spectrum(self, two_thirds=True, max_period=8.0, step=0.01):
        """Return period/acceleration arrays for the spectrum curve."""
        periods = []
        accelerations = []
        t = 0.0
        while t <= max_period:
            periods.append(round(t, 5))
            accelerations.append(self.sa(t, two_thirds=two_thirds))
            t = round(t + step, 5)
        return {"periods": periods, "accelerations": accelerations}
