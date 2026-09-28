import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate as intg
from matplotlib.animation import FuncAnimation

### Input parameters
l = 1  # Length of the rod
g = 10  # Gravitational acceleration

n = 10  # Number of pendulums

# Initial conditions, n pendulums with equally spaced initial positions
diff = 1e-1  # Maximum deviation of initial conditions
factors = np.linspace(1 - diff, 1 + diff, n)
phi0s = np.pi / 4 * factors
dphi0s = [0] * n

T = 10  # Integration time
N = 1000  # Number of discretization points
rtol = 1e-5  # Relative tolerance of the integrator

fps = 20  # Frames per second of the animation
t_real = T  # Actual total time of the integration (seconds)

###
omega = np.sqrt(g / l)
n = len(phi0s)


def der(t, y):
    return np.array([y[1], -(omega**2) * np.sin(y[0])])


t = np.linspace(0, T, N)

ys = np.zeros((n, 2, N))
for i in range(n):
    y0 = [phi0s[i], dphi0s[i]]
    sol = intg.solve_ivp(der, (t[0], t[-1]), y0, t_eval=t, rtol=rtol)
    ys[i, :, :] = sol.y

fig, ax = plt.subplots()
lns = []
cols = plt.cm.jet(np.linspace(0, 1, n))
for i in range(n):
    lns.append(ax.plot([], [], "o-", color=cols[i])[0])


def init():
    ax.set_xlim([-l * 1.1, l * 1.1])
    ax.set_ylim([-l * 1.1, l * 1.1])
    ax.set_aspect("equal")
    return lns


def update(ct):
    for i in range(len(phi0s)):
        lns[i].set_data(
            [0, l * np.sin(ys[i][0][ct])],
            [0, -l * np.cos(ys[i][0][ct])],
        )
    return lns


ani = FuncAnimation(
    fig,
    update,
    frames=np.arange(0, N, N // (fps * t_real)),
    init_func=init,
    blit=True,
    interval=1000 / fps,
)

plt.show()
# ani.save("images/1.2_pendulum_animation.gif")
