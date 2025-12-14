import numpy as np
import matplotlib.pyplot as plt


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
        x = np.linspace(0.0, x_max, n_points)
        Sa = np.zeros_like(x)

        for i, xi in enumerate(x):
            if xi <= 0.2:
                # Linear ramp from Ca to 2.5Ca
                Sa[i] = self.ca + (self.sa_max - self.ca) * (xi / 0.2)

            elif xi <= 1.0:
                # Constant plateau
                Sa[i] = self.sa_max

            else:
                # Long-period decay (Cv/T -> 2.5Ca/x)
                Sa[i] = self.sa_max / xi

        return x, Sa

    def plot(self, x_max: float = 5.0):
        x, Sa = self.calculate(x_max=x_max)

        plt.figure(figsize=(9, 5))
        plt.plot(x, Sa, lw=2.5, color="black",
                 label="NSCP 2015")

        # Control points
        plt.axvline(0.2, ls="--", color="gray", label=r"0.2")
        plt.axvline(1.0, ls="--", color="gray", label=r"1.0")

        plt.title("Design Response Spectrum")
        plt.xlabel(r"Period, $T/T_s$")
        plt.ylabel("Spectral Acceleration, Sa (g)")
        plt.grid(True, which="both", ls="--", alpha=0.5)
        plt.xlim(0, x_max)
        plt.ylim(bottom=0)
        plt.legend()
        plt.tight_layout()
        plt.show()


# ==========================
# Example (your values)
# ==========================
if __name__ == "__main__":
    Ca = 0.66
    Cv = 1.28

    rs = ResponseSpectrum(Ca, Cv)
    rs.plot()
