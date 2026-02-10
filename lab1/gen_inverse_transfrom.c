#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define PI 3.141592653589793
#define N 120000
#define LEFT (-PI / 6.0)
#define MID (PI / 2.0)
#define P1_AREA 0.375
#define HEIGHT2 0.15
#define RIGHT (MID + (1.0 - P1_AREA) / HEIGHT2)

double inverse_cdf(double u) {
  if (u <= 0.0)
    return LEFT;
  if (u >= 1.0)
    return RIGHT;

  if (u <= P1_AREA) {
    return acos(1.0 - 4.0 * u) - PI / 6.0;
  } else {
    return MID + (u - P1_AREA) / HEIGHT2;
  }
}

double density(double x) {
  if (x > LEFT && x <= MID) {
    return 0.25 * sin(x + PI / 6.0);
  }
  if (x > MID && x <= RIGHT) {
    return HEIGHT2;
  }
  return 0.0;
}

int main() {
  srand(time(NULL));

  FILE *f_data = fopen("samples.txt", "w");
  FILE *f_theory = fopen("theory.txt", "w");

  if (!f_data || !f_theory) {
    printf("Ошибка открытия файлов\n");
    return 1;
  }

  for (int i = 0; i < N; i++) {
    double u = (double)rand() / RAND_MAX; // [0,1)
    double x = inverse_cdf(u);
    fprintf(f_data, "%.6f\n", x);
  }

  int n_points = 800;
  double step = (RIGHT - LEFT + 0.4) / (n_points - 1);
  for (int i = 0; i < n_points; i++) {
    double x = LEFT - 0.2 + i * step;
    double fx = density(x);
    fprintf(f_theory, "%.6f %.6f\n", x, fx);
  }

  fclose(f_data);
  fclose(f_theory);

  printf("Генерация завершена.\n");
  printf("Файлы созданы:\n");
  printf("  samples.txt  — сгенерированные значения x\n");
  printf("  theory.txt   — точки теоретической плотности\n");
  printf("Левая граница  = %.4f\n", LEFT);
  printf("Переход        = %.4f\n", MID);
  printf("Правая граница = %.4f\n", RIGHT);
  printf("Площадь части 1 = %.3f\n", P1_AREA);

  return 0;
}
