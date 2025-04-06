#include <stdio.h>
#include <math.h>
#include <stdlib.h>

#define DT 0.01
#define T_MAX 100
#define N (int)(T_MAX / DT)

double m = 10.0;
double b = 0.5;
double c = 10.0;
double F_max = 10.0;

double external_force(double t, double omega) {
    return F_max * cos(omega * t);
}

double acceleration(double x, double v, double t, double omega) {
    double F_t = external_force(t, omega);
    double sign_v = (v > 0) - (v < 0);
    return -(b / m) * v * v * sign_v - (c / m) * x + F_t / m;
}

int main() {
    FILE *fa = fopen("output.txt", "w");
    fprintf(fa, "omega\tamplitude\n");

    for (double omega = 0.0; omega <= 3.0; omega += 0.01) {
        double x_vals[N];
        double x = 0.0, v = 0.0, t = 0.0;

        for (int i = 0; i < N; i++) {
            double a = acceleration(x, v, t, omega);
            double v_mid = v + (DT / 2) * a;
            double x_mid = x + (DT / 2) * v;
            double a_mid = acceleration(x_mid, v_mid, t + DT / 2, omega);
            v += DT * a_mid;
            x += DT * v_mid;

            x_vals[i] = x;
            t += DT;
        }

        // Амплітуда з останніх 30 секунд
        double max_amp = 0.0;
        for (int i = N - 3000; i < N; i++) {
            if (fabs(x_vals[i]) > max_amp) {
                max_amp = fabs(x_vals[i]);
            }
        }

        fprintf(fa, "%.2f\t%.5f\n", omega, max_amp);
    }

    fclose(fa);
    return 0;
}
