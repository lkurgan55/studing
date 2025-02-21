#include <stdio.h>
#include <stdlib.h>

#define DT 0.01  // Крок часу
#define T_MAX 10 // Максимальний час
#define N (int)(T_MAX / DT) // Кількість точок

int main() {
    // Початкові дані
    double m = 10.0;  // кг
    double b = 0.5;   // Н/м²
    double c = 10.0;  // Н/м
    double x = 10.0;  // Початкове положення, м
    double v = 1.0;   // Початкова швидкість, м/с
    double t = 0.0;   // Час

    // Запуск моделювання
    for (int i = 0; i < N; i++) {

        // Модифікований метод Ейлера
        double v_mid = v - (b / m) * v * DT / 2 - (c / m) * x * DT / 2;
        double x_mid = x + v * DT / 2;
        v = v - (b / m) * v_mid * DT - (c / m) * x_mid * DT;
        x = x + v_mid * DT;

        printf("t = %.2f, x = %.4f\n", t, x);

        t += DT;
    }

    return 0;
}
