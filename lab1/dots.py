import numpy as np
import matplotlib.pyplot as plt

samples = np.loadtxt("samples.txt")
theory  = np.loadtxt("theory.txt")

# Берём только часть выборки, чтобы не было каши
samples = samples[:25000]                  # ← вот здесь главная магия

LEFT  = -np.pi / 6
RIGHT = 5.7375

f_values = np.interp(samples, theory[:,0], theory[:,1])
y_scatter = np.random.uniform(0, f_values)

plt.figure(figsize=(11, 6.2))

plt.plot(theory[:,0], theory[:,1],
         color='darkblue', linewidth=2.6,
         label='Теоретическая плотность f(x)')

plt.scatter(samples, y_scatter,
            s=0.9,
            alpha=0.28,
            color='forestgreen',           # или '#228B22'
            rasterized=True,
            label='Сгенерированные значения')

plt.axvline(LEFT,  color='gray', ls='--', alpha=0.5)
plt.axvline(np.pi/2, color='gray', ls='--', alpha=0.5)
plt.axvline(RIGHT, color='gray', ls='--', alpha=0.5)

plt.title('Теоретическая плотность и сгенерированная выборка', fontsize=14)
plt.xlabel('x', fontsize=12)
plt.ylabel('Плотность', fontsize=12)

plt.grid(alpha=0.25, ls='--')
plt.legend(loc='upper left', fontsize=10)

plt.xlim(LEFT - 0.4, RIGHT + 0.5)
plt.ylim(0, 0.38)

plt.tight_layout()
plt.savefig('density_and_sample_cloud_clean.png', dpi=160)
plt.show()
