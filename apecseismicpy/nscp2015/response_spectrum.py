import numpy as np
import matplotlib.pyplot as plt

class ResponseSpectrum:
    """
    A simple three-segment response spectrum with:
      1) Linear ramp from T=0 to T=0.2,
      2) Plateau from T=0.2 to T=1,
      3) Hyperbolic decay for T>1.
    """

    def __init__(self, ca: float, cv: float, R: float = None):
        """
        Parameters:
            ca (float): Short-period acceleration parameter (g or m/s^2 units).
            cv (float): Long-period velocity parameter (g·s or m·s^(-1) units).
            R (float, optional): Response modification factor (not used in this simple example).
        """
        self.ca = ca
        self.cv = cv
        self.R = R

    def calculate_rs_curve(self, t_max: float = 5.0, n_points: int = 501) -> dict:
        """
        Calculate the piecewise response spectrum up to t_max seconds.

        Segments:
          - 0 <= T <= 0.2: Linear ramp from 0 to 2.5*ca
          - 0.2 < T <= 1:  Constant at 2.5*ca
          - T > 1:         cv / T

        Parameters:
            t_max (float): Maximum period (in seconds) to compute.
            n_points (int): Number of discrete points in [0, t_max].

        Returns:
            dict: Contains:
                - "elastic": A dict with keys "x" (period array) and "y" (Sa array).
                - "max_sa": The maximum spectral acceleration (2.5 * ca).
        """
        # Plateau value
        plateau_sa = 2.5 * self.ca

        # Generate an array of time values from 0 to t_max
        t_values = np.linspace(0.0, t_max, n_points)
        sa_values = []

        for T in t_values:
            if T <= 0.2:
                # Linear ramp from 0 to plateau_sa at T=0.2
                # slope = plateau_sa / 0.2, so Sa = slope * T
                sa = (plateau_sa / 0.2) * T
            elif T <= 1.0:
                # Constant plateau
                sa = plateau_sa
            else:
                # Hyperbolic decay
                sa = self.cv / T if T != 0 else plateau_sa  # Avoid division by zero

            sa_values.append(sa)

        return {
            "elastic": {
                "x": t_values,
                "y": np.array(sa_values)
            },
            "max_sa": plateau_sa,
        }

    def plot(self, t_max: float = 5.0) -> None:
        """
        Plot the piecewise response spectrum up to t_max seconds.

        Parameters:
            t_max (float): Maximum period to display on the x-axis.
        """
        rs_data = self.calculate_rs_curve(t_max=t_max)
        t = rs_data["elastic"]["x"]
        sa = rs_data["elastic"]["y"]

        plt.figure(figsize=(8, 5))
        plt.plot(t, sa, label="Elastic Response", color="blue", lw=2)
        plt.title("Custom Piecewise Response Spectrum")
        plt.xlabel("Period (s)")
        plt.ylabel("Spectral Acceleration (Sa)")
        plt.grid(True)
        plt.xlim(0, t_max)
        plt.ylim(bottom=0)
        plt.legend()
        plt.show()

# Example usage:
if __name__ == "__main__":
    # Adjust ca and cv to your project requirements
    spectrum = ResponseSpectrum(ca=0.64, cv=0.96)
    spectrum.plot(t_max=5.0)
