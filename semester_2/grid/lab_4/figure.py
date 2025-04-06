import numpy as np
import matplotlib.pyplot as plt

# Зчитування даних з файлу
def read_amplitudes(filename):
    data = np.loadtxt(filename, skiprows=1)
    omegas = data[:, 0]
    amplitudes = data[:, 1]
    return omegas, amplitudes

# Основні частоти для виділення
highlight_freqs = [0.5, 1.0, 1.5, 2.0]

# Зчитування
filename = "output.txt"
omega, amplitude = read_amplitudes(filename)

# Побудова графіка
plt.figure(figsize=(8, 5))
plt.plot(omega, amplitude, color='orange', label='A(ω)')  # Лінія без маркерів

# Додаємо лише окремі маркери
for target in highlight_freqs:
    idx = np.argmin(np.abs(omega - target))  # Знаходимо найближчий індекс
    plt.plot(omega[idx], amplitude[idx], 'o', color='black', label=f"ω = {omega[idx]:.1f}")

plt.title("Амплітудно-частотна характеристика (резонансна крива)")
plt.xlabel("Частота зовнішньої сили ω (рад/с)")
plt.ylabel("Амплітуда зміщення A (м)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
