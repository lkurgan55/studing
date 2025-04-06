#include <stdio.h>
#include <math.h>

#define DT 0.01  // Крок часу
#define T_MAX 10 // Максимальний час
#define N (int)(T_MAX / DT) // Кількість точок

// Початкові параметри
double m = 10.0;  // кг
double b = 0.5;   // Н/м²
double c = 10.0;  // Н/м

// Параметри зовнішньої сили
double F_max = 10.0; // Амплітуда змушуючої сили
double omega = 0.0; // Частота змушуючої сили

// Функція зовнішньої сили F(t)
double external_force(double t) {
    return F_max * cos(omega * t);
}

// Функція для обчислення прискорення
double acceleration(double x, double v, double t) {
    double F_t = external_force(t);
    double sign_v = (v > 0) - (v < 0); // sign(v)
    return - (b / m) * v * v * sign_v - (c / m) * x + F_t / m;
}

int main() {
    double x = 10.0;  // Початкове положення, м
    double v = 1.0;   // Початкова швидкість, м/с
    double t = 0.0;   // Час

    // Запуск моделювання
    for (int i = 0; i < N; i++) {
        double a = acceleration(x, v, t);  // Виклик функції прискорення

        // Проміжні значення
        double v_mid = v + (DT / 2) * a;
        double x_mid = x + (DT / 2) * v;

        // Обчислення нового прискорення
        double a_mid = acceleration(x_mid, v_mid, t + DT / 2);

        // Нові значення
        v = v + DT * a_mid;
        x = x + DT * v_mid;

        printf("t = %.2f, x = %.4f, v = %.4f\n", t, x, v);

        t += DT;
    }

    return 0;
}
