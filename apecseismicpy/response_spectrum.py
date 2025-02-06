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
        inelastic_x = []
        inelastic_y = []

        for i in range(500):
            seconds = i / 100
            control_period = seconds / Ts

            if control_period == 0:
                sa_index = self.ca
                in_sa_index = self.ca / self.R
            elif 0.2 < control_period <= 1:
                sa_index = twoptfiveCa
                in_sa_index = twoptfiveCa / self.R
            elif 1 < control_period < 5:
                sa_index = self.cv / seconds
                in_sa_index = (self.cv / seconds) / self.R
            else:
                continue

            elastic_x.append(control_period)
            elastic_y.append(sa_index)
            inelastic_x.append(control_period)
            inelastic_y.append(in_sa_index)

        table_x = []
        table_y = []

        for i in range(25):
            seconds = i * 0.2

            if seconds == 0:
                table_x.append(round(seconds, 3))
                table_y.append(round(self.ca, 3))
                continue

            if seconds <= To:
                continue

            if seconds <= Ts:
                sa_index = twoptfiveCa
            else:
                sa_index = self.cv / seconds

            table_x.append(round(seconds, 3))
            table_y.append(round(sa_index, 3))

        return {
            "elastic": {"x": np.array(elastic_x), "y": np.array(elastic_y)},
            "inelastic": {"x": np.array(inelastic_x), "y": np.array(inelastic_y)},
            "tabulated": {"x": np.array(table_x), "y": np.array(table_y)},
            "max_sa": twoptfiveCa,
        }

    def plot(self):
        plt.figure(figsize=(10, 6))
        
        # Plot Elastic and Inelastic Spectra
        plt.plot(self.results["elastic"]["x"], self.results["elastic"]["y"], label="Elastic Response", linestyle='-', marker='')
        plt.plot(self.results["inelastic"]["x"], self.results["inelastic"]["y"], label="Inelastic Response", linestyle='--', marker='')
        plt.scatter(self.results["tabulated"]["x"], self.results["tabulated"]["y"], color='red', label="Tabulated Points")

        plt.xlabel("Control Period (T/Ts)")
        plt.ylabel("Spectral Acceleration (Sa)")
        plt.title("Response Spectrum Curve")
        plt.legend()
        plt.grid(True)
        plt.show()

# Example usage
ca = 0.3
cv = 0.8
R = 3.0
response_spectrum = ResponseSpectrum(ca, cv, R)
response_spectrum.plot()
