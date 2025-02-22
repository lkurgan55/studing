import numpy as np
import matplotlib.pyplot as plt

# Функція для зчитування файлу з даними
def read_data(filename):
    # Зчитуємо дані, пропускаючи перший рядок (заголовок)
    data = np.loadtxt(filename, skiprows=1)
    t_values = data[:, 0]
    x_values = data[:, 1]
    v_values = data[:, 2]
    return t_values, x_values, v_values

# Вкажіть назву файлу з даними
filename = "output.txt"

# Зчитуємо дані
t, x, v = read_data(filename)

# Побудова графіків
plt.figure(figsize=(10, 5))

# Графік положення x(t)
plt.subplot(1, 2, 1)
plt.plot(t, x, label="x(t)", color="b")
plt.xlabel("Час (с)")
plt.ylabel("Положення (м)")
plt.title("Зміщення тіла")
plt.legend()
plt.grid()

# Графік швидкості v(t)
plt.subplot(1, 2, 2)
plt.plot(t, v, label="v(t)", color="r")
plt.xlabel("Час (с)")
plt.ylabel("Швидкість (м/с)")
plt.title("Швидкість тіла")
plt.legend()
plt.grid()

# Відобразити графіки
plt.show()
