# Constants outside the class
NEAR_SOURCE = {
    "na": {
        2: {"A": 1.5, "B": 1.3, "C": 1.0},
        5: {"A": 1.2, "B": 1.0, "C": 1.0},
        10: {"A": 1.0, "B": 1.0, "C": 1.0}
    },
    "nv": {
        2: {"A": 2.0, "B": 1.6, "C": 1.0},
        5: {"A": 1.6, "B": 1.2, "C": 1.0},
        10: {"A": 1.2, "B": 1.0, "C": 1.0},
        15: {"A": 1.0, "B": 1.0, "C": 1.0}
    }
}

SITE_COEFFICIENT = {
    "ca": {
        "sa": {2: 0.16, 4: 0.32},
        "sb": {2: 0.20, 4: 0.40},
        "sc": {2: 0.24, 4: 0.40},
        "sd": {2: 0.28, 4: 0.44},
        "se": {2: 0.34, 4: 0.44}
    },
    "nv": {
        "sa": {2: 0.16, 4: 0.32},
        "sb": {2: 0.20, 4: 0.40},
        "sc": {2: 0.32, 4: 0.56},
        "sd": {2: 0.40, 4: 0.64},
        "se": {2: 0.64, 4: 0.96}
    }
}

class site_coefficients:
    def __init__(self, distance, source_type, soil_type, zone):
        self.distance = distance
        self.source_type = source_type
        self.soil_type = soil_type
        self.zone = int(zone)  # Ensure zone is treated as an integer
        self.results = {}

    def interpolate(self, val1, val2, dist1, dist2):
        """ Linear interpolation for values between two known distances. """
        return val1 + (self.distance - dist1) * (val2 - val1) / (dist2 - dist1)

    def get_near_source(self, factor):
        """ Get interpolated near-source factor based on distance. """
        distances = sorted(NEAR_SOURCE[factor].keys())
        
        for i in range(len(distances) - 1):
            d1, d2 = distances[i], distances[i + 1]
            if self.distance <= d1:
                return NEAR_SOURCE[factor][d1][self.source_type]
            if d1 <= self.distance <= d2:
                v1 = NEAR_SOURCE[factor][d1][self.source_type]
                v2 = NEAR_SOURCE[factor][d2][self.source_type]
                return self.interpolate(v1, v2, d1, d2)
        
        return NEAR_SOURCE[factor][distances[-1]][self.source_type]

    def get_coefficient(self, factor):
        """ Get the site coefficient, applying near-source effect if applicable. """
        coef = SITE_COEFFICIENT[factor][self.soil_type][self.zone]
        if self.zone == 2:
            return coef
        near_source_factor = self.get_near_source('na' if factor == 'ca' else 'nv')
        return coef * near_source_factor

    def calculate(self):
        if self.distance is None or self.distance < 0:
            raise ValueError("Invalid distance. Must be a positive number.")

        self.results = {
            'na': self.get_near_source('na'),
            'nv': self.get_near_source('nv'),
            'ca': self.get_coefficient('ca'),
            'cv': self.get_coefficient('nv')
        }
        return self.results

# distance, source_type, soil_type, zone = 5, "A", "sd", 2

# test = site_coefficients(distance, source_type, soil_type, zone)
# print(test.calculate())