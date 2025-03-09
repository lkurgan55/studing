#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define DT 0.01         // Крок часу, с
#define T_MAX 10.0      // Максимальний час
#define N (int)(T_MAX / DT) // Кількість точок

// Початкові параметри
double m = 10.0;  // кг
double b = 0.5;   // Н/м²
double c = 10.0;  // Н/м

// Параметри зовнішньої сили
double F_max = 0.0; // Амплітуда змушуючої сили
double omega = 0.0; // Частота змушуючої сили

// Функція зовнішньої сили F(t)
double external_force(double t) {
    return F_max * cos(omega * t);
}

// Функція для обчислення прискорення
double acceleration(double x, double v, double t) {
    double F_t = external_force(t);
    double sign_v = (v > 0) - (v < 0);
    return - (b / m) * v * v * sign_v - (c / m) * x + F_t / m;
}

int main(int argc, char *argv[]) {
    // Зчитуємо коефіцієнт тертя з командного рядка
    b = atof(argv[1]);

    // Масиви для збереження проміжних значень
    double t_vals[N], x_vals[N], v_vals[N];

    // Початкові умови
    double x = 10.0;  // Початкове положення, м
    double v = 1.0;   // Початкова швидкість, м/с
    double t = 0.0;   // Початковий час

    // Запуск симуляції
    for (int i = 0; i < N; i++) {
        t_vals[i] = t;
        x_vals[i] = x;
        v_vals[i] = v;

        double a = acceleration(x, v, t);
        double v_mid = v + (DT / 2) * a;
        double x_mid = x + (DT / 2) * v;
        double a_mid = acceleration(x_mid, v_mid, t + DT / 2);
        v = v + DT * a_mid;
        x = x + DT * v_mid;
        t += DT;
    }

    double threshold = 0.3; // Поріг зупинки системи
    printf("Кінцевий час: t = %.2f с, x = %.4f м, v = %.4f м/с\n", t, x, v);
    if (fabs(x) < threshold && fabs(v) < threshold) {
        printf("Система зупинилась.\n");

        // Записуємо проміжні значення у файл output.txt
        FILE *fp = fopen("output.txt", "w");
        fprintf(fp, "t \tx \tv\n");
        for (int i = 0; i < N; i++) {
            fprintf(fp, "%.4f\t%.4f\t%.4f\n", t_vals[i], x_vals[i], v_vals[i]);
        }
        fclose(fp);
        printf("Проміжні значення записано у файл output.txt\n");
    } else {
        printf("Система не зупинилась.\n");
    }

    return 0;
}
