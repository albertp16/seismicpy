import numpy as np
import matplotlib.pyplot as plt


class ResponseSpectrum:
    """
    NSCP-style Design Response Spectrum
    Plateau fixed from T = 0.2 s to T = 1.0 s
    Plateau level = 2.5 * Ca
    """

    def __init__(self, ca: float):
        if ca <= 0:
            raise ValueError("Ca must be positive.")

        self.ca = ca

        # Fixed NSCP-style parameters
        self.T0 = 0.2           # start of plateau
        self.Tp = 1.0           # end of plateau
        self.sa_max = 2.5 * ca  # plateau value

    def calculate(self, t_max: float = 5.0, n_points: int = 800):
        T = np.linspace(0.0, t_max, n_points)
        Sa = np.zeros_like(T)

        for i, t in enumerate(T):
            if t <= self.T0:
                # Linear ramp from Ca to 2.5Ca
                Sa[i] = self.ca + (self.sa_max - self.ca) * (t / self.T0)

            elif t <= self.Tp:
                # Constant plateau (0.2 to 1.0 s)
                Sa[i] = self.sa_max

            else:
                # Long-period decay (anchored to plateau at T = 1.0)
                Sa[i] = self.sa_max / t

        return T, Sa

    def plot(self, t_max: float = 5.0):
        T, Sa = self.calculate(t_max=t_max)

        plt.figure(figsize=(9, 5))
        plt.plot(T, Sa, lw=2.5, color="black",
                 label="Design Response Spectrum")

        # Mark plateau limits
        plt.axvline(self.T0, ls="--", color="gray", label="T = 0.2 s")
        plt.axvline(self.Tp, ls="--", color="gray", label="T = 1.0 s")

        plt.title("Design Response Spectrum (Plateau 0.2–1.0 s)")
        plt.xlabel("Period, T (s)")
        plt.ylabel("Spectral Acceleration, Sa (g)")
        plt.grid(True, which="both", ls="--", alpha=0.5)
        plt.xlim(0, t_max)
        plt.ylim(bottom=0)
        plt.legend()
        plt.tight_layout()
        plt.show()


# ==========================
# Example usage
# ==========================
if __name__ == "__main__":
    Ca = 0.66  # example value (g)
    Cv = 1.28
    rs = ResponseSpectrum(Ca)
    rs.plot()
