import math


class ResponseSpectrum:
    """
    NSCP Ca–Cv Design Response Spectrum
    x-axis plotted as T / Ts (NSCP Figure 208-3)
    """

    def __init__(self, ca: float, cv: float):
        if ca <= 0 or cv <= 0:
            raise ValueError("Ca and Cv must be positive.")

        self.ca = ca
        self.cv = cv

        # NSCP control periods
        self.sa_max = 2.5 * ca
        self.Ts = cv / self.sa_max
        self.T0 = 0.2 * self.Ts

    def calculate(self, x_max: float = 5.0, n_points: int = 800):
        """
        Compute spectrum using normalized period x = T / Ts
        """
        step = x_max / (n_points - 1)
        x = [i * step for i in range(n_points)]
        Sa = []

        for xi in x:
            if xi <= 0.2:
                Sa.append(self.ca + (self.sa_max - self.ca) * (xi / 0.2))
            elif xi <= 1.0:
                Sa.append(self.sa_max)
            else:
                Sa.append(self.sa_max / xi)

        return x, Sa

    def generate_adrs(self, x_max: float = 5.0, n_points: int = 800):
        """
        Generate ADRS data: Sa vs Sd with actual period T.
        Sd = Sa * g * T^2 / (4 * pi^2)
        """
        g = 9.81
        x, Sa = self.calculate(x_max=x_max, n_points=n_points)
        T_actual = [xi * self.Ts for xi in x]
        Sd = [sa * g * t ** 2 / (4 * math.pi ** 2) for sa, t in zip(Sa, T_actual)]
        return Sd, Sa, T_actual

    def generate_reduced_adrs(self, SRA: float, SRV: float,
                              x_max: float = 5.0, n_points: int = 800):
        """
        Generate reduced ADRS using ATC-40 spectral reduction factors.
        SRA applies to the constant-acceleration plateau.
        SRV applies to the constant-velocity descending branch.
        The reduced Ts' = (SRV / SRA) * Ts.
        """
        g = 9.81
        step = x_max / (n_points - 1)
        x_vals = [i * step for i in range(n_points)]

        Ts_r = (SRV / SRA) * self.Ts
        sa_max_r = SRA * self.sa_max
        ca_r = SRA * self.ca

        Sa_r = []
        for xi in x_vals:
            T = xi * self.Ts  # actual period
            if T <= 0.2 * Ts_r:
                Sa_r.append(ca_r + (sa_max_r - ca_r) * (T / (0.2 * Ts_r))
                            if Ts_r > 0 else ca_r)
            elif T <= Ts_r:
                Sa_r.append(sa_max_r)
            else:
                Sa_r.append(sa_max_r * Ts_r / T if T > 0 else 0)

        T_actual = [xi * self.Ts for xi in x_vals]
        Sd_r = [sa * g * t ** 2 / (4 * math.pi ** 2) for sa, t in zip(Sa_r, T_actual)]
        return Sd_r, Sa_r, T_actual


def atc40_reduction(dy: float, ay: float, dpi: float, api_val: float,
                    structure_type: str):
    """
    ATC-40 effective damping and spectral reduction factors.

    Parameters
    ----------
    dy  : yield displacement (m)
    ay  : yield acceleration (g)
    dpi : trial performance-point displacement (m)
    api_val : trial performance-point acceleration (g)
    structure_type : 'A', 'B', or 'C'

    Returns
    -------
    dict with beta_0, kappa, beta_eff, SRA, SRV
    """
    if api_val <= 0 or dpi <= 0:
        raise ValueError("dpi and api must be positive.")

    area_ratio = (ay * dpi - dy * api_val) / (api_val * dpi)
    beta_0 = 63.7 * area_ratio

    st = structure_type.upper()
    if st == "A":
        if beta_0 <= 16.25:
            kappa = 1.0
        else:
            kappa = 1.13 - 0.51 * area_ratio
    elif st == "B":
        if beta_0 <= 16.25:
            kappa = 0.67
        else:
            kappa = 0.845 - 0.446 * area_ratio
    elif st == "C":
        kappa = 0.33
    else:
        raise ValueError(f"Unknown structure type: {structure_type}")

    beta_eff = kappa * beta_0 + 5

    SRA = (3.21 - 0.68 * math.log(beta_eff)) / 2.12
    SRV = (2.31 - 0.41 * math.log(beta_eff)) / 1.65

    SRA = max(SRA, 0.33)
    SRV = max(SRV, 0.50)

    return {
        "beta_0": round(beta_0, 2),
        "kappa": round(kappa, 3),
        "beta_eff": round(beta_eff, 2),
        "SRA": round(SRA, 3),
        "SRV": round(SRV, 3),
    }
