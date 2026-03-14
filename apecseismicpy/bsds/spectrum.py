class SeismicDesignResponse:
    """
    Compute BSDS Level II and Level I seismic design response spectra.
    """

    def __init__(self, pga, fpga, ss, s1, fa, fv):
        if any(param < 0 for param in [pga, fpga, ss, s1, fa, fv]):
            raise ValueError("All input parameters must be non-negative.")
        self.pga = pga
        self.fpga = fpga
        self.ss = ss
        self.s1 = s1
        self.fa = fa
        self.fv = fv

    def calculate_as(self):
        return self.fpga * self.pga

    def calculate_sds(self):
        return self.fa * self.ss

    def calculate_sd1(self):
        return self.fv * self.s1

    def calculate_ts(self):
        return self.calculate_sd1() / self.calculate_sds()

    def calculate_to(self):
        return 0.2 * self.calculate_ts()

    def generate_level2_spectrum(self, max_period=8.0, step=0.01):
        """Generate BSDS Level II spectrum data points."""
        A_s = self.calculate_as()
        S_DS = self.calculate_sds()
        S_D1 = self.calculate_sd1()
        T_s = self.calculate_ts()
        T_0 = 0.2 * T_s

        periods = []
        accelerations = []

        t = 0.0
        while t <= max_period:
            if t == 0:
                accel = A_s
            elif 0 < t < T_0:
                slope = (S_DS - A_s) / T_0
                accel = A_s + slope * t
            elif T_0 <= t <= T_s:
                accel = S_DS
            else:
                accel = S_D1 / t

            periods.append(round(t, 5))
            accelerations.append(accel)
            t += step
            t = round(t, 5)

        return {
            "periods": periods,
            "accelerations": accelerations,
            "A_s": A_s,
            "S_DS": S_DS,
            "S_D1": S_D1,
            "T_s": T_s,
            "T_0": T_0,
        }

    def generate_level1_spectrum(self, site_class, damping_ratio=0.02,
                                  max_period=8.0, step=0.01):
        """Generate BSDS Level I EGM spectrum: S = cz * cD * S0."""
        S1 = self.s1
        if S1 <= 0.25:
            cz = 0.70
        elif 0.25 < S1 <= 0.35:
            cz = 0.85
        else:
            cz = 1.0

        cD = (1.5 / (40 * damping_ratio + 1)) + 0.5

        periods = []
        accelerations = []

        t = 0.0
        while t <= max_period:
            if site_class == "I":
                if t < 0.1:
                    S0 = max(0.439 * (t ** (1 / 3)) if t > 0 else 0.16, 0.16)
                elif 0.1 <= t <= 1.1:
                    S0 = 0.204
                else:
                    S0 = 0.224 / t
            elif site_class == "II":
                if t < 0.2:
                    S0 = max(0.435 * (t ** (1 / 3)) if t > 0 else 0.20, 0.20)
                elif 0.2 <= t <= 1.3:
                    S0 = 0.255
                else:
                    S0 = 0.331 / t
            elif site_class == "III":
                if t < 0.34:
                    S0 = max(0.438 * (t ** (1 / 3)) if t > 0 else 0.34, 0.34)
                elif 0.34 <= t <= 1.5:
                    S0 = 0.306
                else:
                    S0 = 0.459 / t
            else:
                raise ValueError("site_class must be 'I', 'II', or 'III'.")

            S = cz * cD * S0
            periods.append(round(t, 5))
            accelerations.append(S)
            t += step
            t = round(t, 5)

        return {
            "periods": periods,
            "accelerations": accelerations,
            "cz": cz,
            "cD": round(cD, 4),
        }
