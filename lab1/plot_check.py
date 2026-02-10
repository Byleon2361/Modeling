import numpy as np
import matplotlib.pyplot as plt

samples = np.loadtxt("samples.txt")
theory  = np.loadtxt("theory.txt")

LEFT  = -np.pi / 6
MID   = np.pi / 2
RIGHT = 5.7375

plt.figure(figsize=(12, 6.5))

plt.hist(samples, bins=180, density=True, alpha=0.65, color="mediumseagreen",
         label="Сгенерированная выборка")

plt.plot(theory[:,0], theory[:,1], color="darkblue", lw=2.8,
         label="Теоретическая плотность f(x)")

plt.axvline(LEFT,  color="gray", ls="--", alpha=0.6, label="Границы интервалов")
plt.axvline(MID,   color="gray", ls="--", alpha=0.6)
plt.axvline(RIGHT, color="gray", ls="--", alpha=0.6)

plt.title("Проверка метода обратных функций", fontsize=14)
plt.xlabel("x", fontsize=13)
plt.ylabel("Плотность", fontsize=13)
plt.grid(alpha=0.35, ls="--")
plt.legend()
plt.xlim(LEFT - 0.4, RIGHT + 0.4)
plt.ylim(0, 0.35)
plt.tight_layout()
plt.savefig("distribution_check.png", dpi=140)
plt.show()
