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
        plt.plot(x, Sa, lw=2.5, color="black", label="NSCP 2015")

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

    def plotTH(self, T: float, x_max: float = 5.0):
        """
        Plot design spectrum with:
        - 1.4x amplified spectrum (red)
        - Vertical red dashed lines at 0.2T and 1.5T
        """
        x, Sa = self.calculate(x_max=x_max)

        # 1.4x spectrum
        Sa_14 = 1.4 * Sa

        plt.figure(figsize=(9, 5))

        # Original spectrum
        plt.plot(x, Sa, lw=2.5, color="black", label="NSCP 2015")

        # Amplified spectrum
        plt.plot(x, Sa_14, lw=2.0, color="red", label="1.4 × NSCP 2015")

        # Original control points
        plt.axvline(0.2, ls="--", color="gray")
        plt.axvline(1.0, ls="--", color="gray")

        # T-based vertical limits
        plt.axvline(0.2 * T, ls="--", color="red", label=r"$0.2T$")
        plt.axvline(1.5 * T, ls="--", color="red", label=r"$1.5T$")

        plt.title("Design Response Spectrum")
        plt.xlabel(r"Period, $T/T_s$")
        plt.ylabel("Spectral Acceleration, Sa (g)")
        plt.grid(True, which="both", ls="--", alpha=0.5)
        plt.xlim(0, x_max)
        plt.ylim(bottom=0)
        plt.legend()
        plt.tight_layout()
        plt.show()

    def plot_adrs(self, x_max: float = 5.0, n_points: int = 800, g: float = 9.81):
        """
        Plot ADRS curve:
        x-axis = Spectral Displacement, Sd (m)
        y-axis = Spectral Acceleration, Sa (g)

        Uses:
            T = x * Ts
            Sd = Sa * g * T^2 / (4*pi^2)
        """
        x, Sa = self.calculate(x_max=x_max, n_points=n_points)

        # Convert normalized x = T/Ts back to actual period T
        T = x * self.Ts

        # ADRS conversion
        Sd = Sa * g * T**2 / (4 * np.pi**2)

        plt.figure(figsize=(9, 5))
        plt.plot(Sd, Sa, lw=2.5, color="blue", label="ADRS Curve")

        plt.title("Acceleration-Displacement Response Spectrum (ADRS)")
        plt.xlabel("Spectral Displacement, Sd (m)")
        plt.ylabel("Spectral Acceleration, Sa (g)")
        plt.grid(True, which="both", ls="--", alpha=0.5)
        plt.xlim(left=0)
        plt.ylim(bottom=0)
        plt.legend()
        plt.tight_layout()
        plt.show()

        return Sd, Sa, T


# # ==========================
# # Example
# # ==========================
# if __name__ == "__main__":
#     Ca = 0.42
#     Cv = 0.72

#     rs = ResponseSpectrum(Ca, Cv)
#     rs.plot()
#     rs.plot_adrs()