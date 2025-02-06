import numpy as np
import matplotlib.pyplot as plt

class ResponseSpectrum:
    def __init__(self, ca, cv, R):
        self.ca = ca
        self.cv = cv
        self.R = R
        self.results = self.calculate_rs_curve()

    def calculate_rs_curve(self):
        twoptfiveCa = 2.5 * self.ca
        Ts = self.cv / twoptfiveCa
        To = 0.2 * Ts

        elastic_x = []
        elastic_y = []

        for i in range(501):  # Ensure the last point at 5 seconds is included
            seconds = i / 100
            if seconds > 5:
                break
            control_period = seconds / Ts

            if control_period == 0:
                sa_index = self.ca
            elif 0.2 < control_period <= 1:
                sa_index = twoptfiveCa
            elif 1 < control_period <= 5:
                sa_index = self.cv / seconds
            else:
                continue

            elastic_x.append(seconds)
            elastic_y.append(sa_index)

        return {
            "elastic": {"x": np.array(elastic_x), "y": np.array(elastic_y)},
            "max_sa": twoptfiveCa,
        }

    def plot(self):
        plt.figure(figsize=(10, 6))
        
        # Plot Elastic Response Spectrum
        plt.plot(self.results["elastic"]["x"], self.results["elastic"]["y"], label="Elastic Response", linestyle='-', marker='')
        
        plt.xlabel("Control Period (s)")
        plt.ylabel("Spectral Acceleration (Sa)")
        plt.title("Response Spectrum Curve")
        plt.legend()
        plt.grid(True)
        plt.xlim(0, 5)  # Ensure the x-axis extends to 5 seconds
        plt.show()

# Example usage
ca = 0.3
cv = 0.8
R = 3.0
response_spectrum = ResponseSpectrum(ca, cv, R)
response_spectrum.plot()
