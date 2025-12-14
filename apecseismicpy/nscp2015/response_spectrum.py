import numpy as np
import matplotlib.pyplot as plt


class ResponseSpectrum:
    """
    NSCP/UBC-style elastic response spectrum using Ca and Cv with:
      1) Linear ramp: 0 <= T <= 0.2
      2) Plateau:     0.2 < T <= 1.0
      3) Decay:       T > 1.0  -> Sa = Cv / T

    Continuity fix at T=1.0:
      Use Sa_max = min(2.5*Ca, Cv) so Sa(1-) = Sa(1+) = Cv when Cv governs.
    """

    def __init__(self, ca: float, cv: float, R: float = None,
                 to: float = 0.2, tp: float = 1.0):
        """
        Parameters:
            ca (float): short-period acceleration parameter
            cv (float): long-period velocity parameter
            R (float, optional): response modification factor (not used here)
            T0 (float): ramp end period (default 0.2s)
            Tp (float): plateau end period (default 1.0s per your NSCP intent)
        """
        if ca <= 0 or cv <= 0:
            raise ValueError("ca and cv must be positive.")

        if tp <= to:
            raise ValueError("Tp (plateau end) must be greater than T0 (ramp end).")

        self.ca = ca
        self.cv = cv
        self.R = R

        self.to = to
        self.tp = tp

        # Plateau level (continuity-friendly)
        self.plateau_sa = min(2.5 * self.ca, self.cv)

    def calculate_rs_curve(self, t_max: float = 5.0, n_points: int = 501) -> dict:
        """
        Returns:
            dict with:
              elastic: {x: periods, y: Sa}
              parameters: {T0, Tp, Sa_max}
        """
        t_values = np.linspace(0.0, t_max, n_points)
        sa_values = np.zeros_like(t_values)

        for i, T in enumerate(t_values):
            if T <= self.to:
                # Linear ramp to plateau_sa at T0
                sa = self.plateau_sa * (T / self.to)

            elif T <= self.tp:
                # Constant plateau up to 1.0s (Tp)
                sa = self.plateau_sa

            else:
                # Decay branch (NSCP/UBC): Cv/T
                sa = self.cv / T

            sa_values[i] = sa

        return {
            "elastic": {"x": t_values, "y": sa_values},
            "parameters": {"to": self.to, "tp": self.tp, "Sa_max": self.plateau_sa}
        }

    def plot(self, t_max: float = 5.0, n_points: int = 501) -> None:
        rs = self.calculate_rs_curve(t_max=t_max, n_points=n_points)
        t = rs["elastic"]["x"]
        sa = rs["elastic"]["y"]
        p = rs["parameters"]

        plt.figure(figsize=(9, 5))
        plt.plot(t, sa, lw=2, color="red",label="Inelastic Response Spectrum")

        plt.axvline(p["to"], ls="--", lw=1, color="gray")
        plt.axvline(p["tp"], ls="--", lw=1, color="gray")

        plt.title("Design Response Spectrum")
        plt.xlabel("Period, T (s)")
        plt.ylabel("Spectral Acceleration, Sa")
        plt.grid(True, which="both", ls="--", alpha=0.5)
        plt.xlim(0, t_max)
        plt.ylim(bottom=0)
        plt.legend()
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    # Example values (replace with your NSCP Ca and Cv)
    ca = 0.64
    cv = 0.96

    rs = ResponseSpectrum(ca=ca, cv=cv, tp=1.0)
    rs.plot(t_max=5.0)
