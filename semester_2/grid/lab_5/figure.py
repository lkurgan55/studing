import numpy as np
import matplotlib.pyplot as plt
import re

# Функція для зчитування файлу
def read_data(filename):
    t_values = []
    x_values = []
    v_values = []

    with open(filename, "r") as file:
        for line in file:
            match = re.search(r"t = ([\d\.]+), x = ([\d\.-]+), v = ([\d\.-]+)", line)
            if match:
                t_values.append(float(match.group(1)))
                x_values.append(float(match.group(2)))
                v_values.append(float(match.group(3)))

    return np.array(t_values), np.array(x_values), np.array(v_values)

# Вкажи назву файлу
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
