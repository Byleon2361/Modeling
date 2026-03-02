import numpy as np
import matplotlib.pyplot as plt

# Загрузка данных
samples = np.loadtxt("samples.txt")
theory  = np.loadtxt("theory.txt")

# Границы области
LEFT  = -np.pi / 6          # ≈ -0.5236
MID   = np.pi / 2           # ≈ 1.5708
RIGHT = MID + (1.0 - 0.375) / 0.15   # ≈ 5.737

# Сколько точек показывать (главное изменение здесь)
N_SHOW = 800

if len(samples) > N_SHOW:
    # равномерно берём N_SHOW точек
    indices = np.linspace(0, len(samples)-1, N_SHOW, dtype=int)
    samples_show = samples[indices]
else:
    samples_show = samples.copy()

# Интерполируем теоретическую плотность в точках выборки
f_values = np.interp(samples_show, theory[:, 0], theory[:, 1])

# Случайная высота под кривой (для метода обратных функций — визуализация)
y_scatter = np.random.uniform(0, f_values)

# ────────────────────────────────────────────────
plt.figure(figsize=(11.5, 6.4))

# Теоретическая плотность
plt.plot(theory[:, 0], theory[:, 1],
         color='darkblue', linewidth=2.5,
         label='Теоретическая плотность $f(x)$')

# Точки выборки — главное визуальное улучшение
plt.scatter(samples_show, y_scatter,
            s=2.8,               # сильно меньше, чем было
            color='forestgreen',
            marker='.',
            alpha=0.78,          # прозрачность — ключевое
            rasterized=True,
            label='Реализации случайной величины')

# Вертикальные линии-ограничители
plt.axvline(LEFT,  color='gray', ls='--', lw=1.0, alpha=0.6)
plt.axvline(MID,   color='gray', ls='--', lw=1.0, alpha=0.6)
plt.axvline(RIGHT, color='gray', ls='--', lw=1.0, alpha=0.6)

# Подписи к вертикальным линиям
plt.text(LEFT,  0.295, r'$-\pi/6$',   ha='center', va='bottom', fontsize=10, color='dimgray')
plt.text(MID,   0.295, r'$\pi/2$',    ha='center', va='bottom', fontsize=10, color='dimgray')
plt.text(RIGHT, 0.295, f'{RIGHT:.2f}', ha='center', va='bottom', fontsize=10, color='dimgray')

# Оформление
plt.title('Метод обратных функций: выборка и теоретическая плотность', 
          fontsize=14, pad=14)
plt.xlabel('$x$', fontsize=13)
plt.ylabel('Плотность вероятности', fontsize=13)

plt.grid(True, alpha=0.25, ls='--', zorder=0)
plt.legend(loc='upper left', fontsize=10.5, framealpha=0.9)

plt.xlim(LEFT - 0.5, RIGHT + 0.6)
plt.ylim(-0.01, 0.32)

plt.tight_layout()
plt.savefig('inverse_transform_sample_clear.png', dpi=180, bbox_inches='tight')
plt.show()
