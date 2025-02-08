import math
import matplotlib.pyplot as plt

def calculate_liquid_weights(l, b, h_l, gamma_l):
    # Total Liquid Weight
    w_l = l * b * h_l * gamma_l
    
    # Impulsive Weight Calculation (Eq. 9-1)
    ratio_l_hl = l / h_l
    w_i = (math.tanh(0.866 * ratio_l_hl) / (0.866 * ratio_l_hl)) * w_l
    
    # Convective Weight Calculation (Eq. 9-2)
    w_c = 0.264 * (ratio_l_hl) * math.tanh(3.16 * (h_l / l)) * w_l
    
    return w_l, w_i, w_c

def calculate_heights_of_centers_of_gravity(l, h_l):
    # Heights to centers of gravity, EBP
    h_i = (0.5 - 0.09375 * (l / h_l)) * h_l if (l / h_l) < 1.333 else 0.375 * h_l
    h_c = (1 - (math.cosh(3.16 * (h_l / l)) - 1) / (3.16 * (h_l / l) * math.sinh(3.16 * (h_l / l)))) * h_l
    
    # Heights to centers of gravity, IBP
    h_pi = 0.45 * h_l if (l / h_l) < 0.75 else ((0.866 * (l / h_l)) / (2 * math.tanh(0.866 * (l / h_l))) - 1/8) * h_l
    h_pc = (1 - (math.cosh(3.16 * (h_l / l)) - 2.01) / (3.16 * (h_l / l) * math.sinh(3.16 * (h_l / l)))) * h_l
    
    return h_i, h_c, h_pi, h_pc

def calculate_dynamic_properties(h_w, t_w_ave, gamma_c, g, e_c):
    # Wall weight per linear meter
    m_w = h_w * t_w_ave * gamma_c / g
    
    # Impulsive weight of contents per linear meter
    m_i = ((w_i / w_l) * (l / 2) * h_l * gamma_l / g)
    
    # Equivalent cantilever wall height
    h = ((0.5 * h_w * m_w + h_i * m_i) / (m_w + m_i))
    
    # Wall stiffness per linear meter
    k = (e_c / 4) * ((t_w_ave / h) ** 3)
    
    # Total weight per linear meter
    m_t = m_w + m_i
    
    # Fundamental period of oscillation
    t_i = 2 * math.pi * math.sqrt((m_t * h) / k)
    
    return m_w, m_i, h, k, m_t, t_i

# Given Data
l = 14.5  # Parallel to Motion (m)
b = 7.2    # Perpendicular to Motion (m)
h_l = 10.0 # Liquid Height (m) - assumed value
gamma_l = 9.81  # Unit weight of liquid (kN/m^3) - assumed value
h_w = 8.0  # Wall height (m) - assumed value
t_w_ave = 0.3  # Average wall thickness (m) - assumed value
gamma_c = 25.0  # Unit weight of concrete (kN/m^3) - assumed value
g = 9.81  # Acceleration due to gravity (m/s^2)
e_c = 30e6  # Elastic modulus of concrete (kN/m^2) - assumed value

# Compute Values
w_l, w_i, w_c = calculate_liquid_weights(l, b, h_l, gamma_l)
h_i, h_c, h_pi, h_pc = calculate_heights_of_centers_of_gravity(l, h_l)
m_w, m_i, h, k, m_t, t_i = calculate_dynamic_properties(h_w, t_w_ave, gamma_c, g, e_c)

# Plotting Seismic Response Spectrum
ti_values = [i * 0.5 for i in range(20)]
ci_values = [1.1 if ti <= 1.0 else 1.0 / ti for ti in ti_values]

plt.figure(figsize=(8, 5))
plt.plot(ti_values, ci_values, marker='o', linestyle='-', color='r')
plt.axvline(x=t_i, color='b', linestyle='dashed', label=f'T_i = {t_i:.3f}s')
plt.xlabel('Period, T_i (s)')
plt.ylabel('Seismic Coefficient, C_i')
plt.title('Impulsive Design Response Spectrum')
plt.legend()
plt.grid()
plt.show()

# Display Results
print(f"Total Liquid Weight (w_l): {w_l:.3f} kN")
print(f"Impulsive Weight (w_i): {w_i:.3f} kN")
print(f"Convective Weight (w_c): {w_c:.3f} kN")
print(f"Height to center of gravity, EBP (h_i): {h_i:.3f} m")
print(f"Height to center of gravity, EBP (h_c): {h_c:.3f} m")
print(f"Height to center of gravity, IBP (h_pi): {h_pi:.3f} m")
print(f"Height to center of gravity, IBP (h_pc): {h_pc:.3f} m")
print(f"Wall weight per linear meter (m_w): {m_w:.3f} kg/m")
print(f"Impulsive weight per linear meter (m_i): {m_i:.3f} kg/m")
print(f"Equivalent cantilever wall height (h): {h:.3f} m")
print(f"Wall stiffness per linear meter (k): {k:.3f} kN/m")
print(f"Total weight per linear meter (m_t): {m_t:.3f} kg/m")
print(f"Fundamental period of oscillation (t_i): {t_i:.3f} s")
