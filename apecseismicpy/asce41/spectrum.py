from .site_coefficients import damping_factor_b1


class Asce41Spectrum:
    """
    ASCE 41-17 general horizontal response spectrum — BSE-1E and BSE-2E.

    Hazard chain, in the order the standard sets it
    -----------------------------------------------
        §2.4.1.3  BSE-2E need not exceed BSE-2N, and BSE-2N is the MCE_R that
                  the hazard maps publish        ->  BSE-2E = mapped MCE
        §2.4.1.2  BSE-1N = (2/3) * BSE-2N
        §2.4.1.4  BSE-1E need not exceed BSE-1N  ->  BSE-1E = (2/3) * BSE-2E
        §2.4.1.6  SXS = Fa * Ss ; SX1 = Fv * S1  (Eqs. 2-1, 2-2)

    Where no 5%/50 or 20%/50 hazard maps exist (the Philippines among them),
    taking both caps is the only available construction and over-states the
    demand — conservative in direction.

    Spectrum branches, §2.4.1.7.1 with the Eq. (2-3) damping adjustment B1
    -------------------------------------------------------------------
        T < T0        : Sa = 0.4*SXS + (SXS/B1 - 0.4*SXS) * T / T0
        T0 <= T <= Ts : Sa = SXS / B1
        Ts <  T <= TL : Sa = SX1 / (B1 * T)
        T > TL        : Sa = SX1 * TL / (B1 * T^2)

    Note that the T = 0 anchor 0.4*SXS is NOT divided by B1 — that is how the
    clause is written, and it is reproduced literally here.

    Ts and T0 are common to both hazard levels: the two-thirds factor scales
    SXS and SX1 together and cancels in the quotient.

    Attributes:
        ss, s1: mapped spectral accelerations at the BSE-2E (MCE) level, g.
        fa, fv: site coefficients (see Asce41SiteCoefficients).
        tl: long-period transition period, s.
        damping: effective viscous damping ratio; b1 derives from it.
    """

    LEVELS = ("BSE-2E", "BSE-1E")
    BSE1E_FACTOR = 2.0 / 3.0     # §2.4.1.2 / §2.4.1.4 cap

    def __init__(self, ss, s1, fa, fv, tl=16.0, damping=0.05, b1=None):
        if ss <= 0:
            raise ValueError("Ss must be positive.")
        if s1 <= 0:
            # A zero one-second ordinate collapses Ts to 0 and the whole
            # descending limb with it — refuse rather than return a flat zero.
            raise ValueError("S1 must be positive.")
        if fa <= 0 or fv <= 0:
            raise ValueError("Fa and Fv must be positive.")
        if tl <= 0:
            raise ValueError("TL must be positive.")

        self.ss = ss
        self.s1 = s1
        self.fa = fa
        self.fv = fv
        self.tl = tl
        self.damping = damping
        self.b1 = damping_factor_b1(damping) if b1 is None else b1
        if self.b1 <= 0:
            raise ValueError("B1 must be positive.")

        # BSE-2E — the mapped MCE, unreduced (§2.4.1.3 + §2.4.1.6)
        self.sxs_bse2e = fa * ss
        self.sx1_bse2e = fv * s1

        # BSE-1E — two-thirds of BSE-2E (§2.4.1.4)
        self.sxs_bse1e = self.BSE1E_FACTOR * self.sxs_bse2e
        self.sx1_bse1e = self.BSE1E_FACTOR * self.sx1_bse2e

        # Control periods — identical for both levels
        self.ts = self.sx1_bse2e / self.sxs_bse2e if self.sxs_bse2e > 0 else 0.0
        self.t0 = 0.2 * self.ts

    # ── level lookup ─────────────────────────────────────────────────────────

    def _level_ordinates(self, level):
        key = str(level).upper().replace("_", "-")
        if key in ("BSE-2E", "BSE2E", "CP", "COLLAPSE PREVENTION"):
            return self.sxs_bse2e, self.sx1_bse2e
        if key in ("BSE-1E", "BSE1E", "LS", "LIFE SAFETY"):
            return self.sxs_bse1e, self.sx1_bse1e
        raise ValueError("level must be 'BSE-1E' or 'BSE-2E'.")

    @property
    def exception2_bound(self):
        """1.5*Ts — beyond this period ASCE 7-16 §11.4.8 Exception 2 requires
        the seismic response coefficient to be taken as 1.5x the computed
        value. Written for the ASCE 7 ELF coefficient Cs; carrying it onto the
        §2.4.1.7 general spectrum is an interpretation, conservative in
        direction."""
        return 1.5 * self.ts

    def branch_at(self, t):
        """Name the spectrum branch a period lands on — the answer to
        'does stiffening this frame attract more demand?'."""
        if t < self.t0:
            return "ascending (T < T0)"
        if t <= self.ts:
            return "plateau (T0 <= T <= Ts)"
        if t <= self.tl:
            return "velocity branch (Ts < T <= TL)"
        return "displacement branch (T > TL)"

    # ── ordinates ────────────────────────────────────────────────────────────

    def sa(self, t, level="BSE-2E"):
        """Spectral acceleration (g) at period t for the given hazard level."""
        sxs, sx1 = self._level_ordinates(level)
        if self.ts <= 0 or self.t0 <= 0:
            return 0.0

        plateau = sxs / self.b1
        anchor = 0.4 * sxs                 # T = 0 intercept, not divided by B1

        if t < self.t0:
            return anchor + (plateau - anchor) * (t / self.t0)
        if t <= self.ts:
            return plateau
        if t <= self.tl:
            return sx1 / (self.b1 * t)
        return sx1 * self.tl / (self.b1 * t ** 2)

    def generate_spectrum(self, level="BSE-2E", max_period=8.0, step=0.01):
        """Return period/acceleration arrays for one hazard level."""
        if max_period <= 0:
            raise ValueError("max_period must be positive.")
        if step <= 0:
            raise ValueError("step must be positive.")

        periods = []
        accelerations = []
        t = 0.0
        while t <= max_period:
            periods.append(round(t, 5))
            accelerations.append(self.sa(t, level=level))
            t = round(t + step, 5)
        return {"periods": periods, "accelerations": accelerations}

    def summary(self):
        """Every derived quantity, for the audit trail."""
        return {
            "b1": self.b1,
            "sxs_bse2e": self.sxs_bse2e,
            "sx1_bse2e": self.sx1_bse2e,
            "sxs_bse1e": self.sxs_bse1e,
            "sx1_bse1e": self.sx1_bse1e,
            "t0": self.t0,
            "ts": self.ts,
            "tl": self.tl,
            "exception2_bound": self.exception2_bound,
        }
