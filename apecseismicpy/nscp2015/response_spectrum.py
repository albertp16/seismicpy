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
