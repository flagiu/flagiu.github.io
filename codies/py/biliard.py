import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as opt
from matplotlib.animation import FuncAnimation


### Definitions
# Functions describing billiard table shapes should return < 0 when
# inside the table and > 0 otherwise.
def circle_f(x):
    return x[0] ** 2 + x[1] ** 2 - 1


# Derivative of the above function
def der_circle_f(x):
    return np.array([2 * x[0], 2 * x[1]])


# Limits of the table, for nicer plotting
circle_xlims = (-1, 1)
circle_ylims = (-1, 1)


def bunimovich_f(x):
    if x[0] < -1:
        return (x[0] + 1) ** 2 + x[1] ** 2 - 1
    elif x[0] > 1:
        return (x[0] - 1) ** 2 + x[1] ** 2 - 1
    else:
        return np.abs(x[1]) - 1


def der_bunimovich_f(x):
    if x[0] < -1:
        return np.array([2 * (x[0] + 1), 2 * x[1]])
    elif x[0] > 1:
        return np.array([2 * (x[0] - 1), 2 * x[1]])
    else:
        return np.array([0, 1])


bunimovich_xlims = (-2, 2)
bunimovich_ylims = (-1, 1)


def sinai_f(x):
    if x[0] ** 2 + x[1] ** 2 < 0.7:
        return 0.5**2 - x[0] ** 2 - x[1] ** 2
    else:
        return np.max(np.abs(x)) - 1


def der_sinai_f(x):
    if x[0] ** 2 + x[1] ** 2 < 0.7:
        return np.array([2 * x[0], 2 * x[1]])
    elif np.abs(x[0]) > 0.99:
        return np.array([1, 0])
    else:
        return np.array([0, 1])


sinai_xlims = (-1, 1)
sinai_ylims = (-1, 1)

### Input parameters
n = 50  # Number of billiard balls

# Initial conditions, n balls with equally spaced initial velocities
diff = 1e-2  # Maximum deviation of initial conditions
factors = np.linspace(1 - diff, 1 + diff, n)
angles = np.pi / 3 * factors
vx0s = 1 * np.cos(angles)
vy0s = 1 * np.sin(angles)
x0s = [0.6] * n
y0s = [0] * n

# Shape of the billiard table and its limits
# f = circle_f
# der_f = der_circle_f
# xlims = circle_xlims
# ylims = circle_ylims
f = bunimovich_f
der_f = der_bunimovich_f
xlims = bunimovich_xlims
ylims = bunimovich_ylims
# f = sinai_f
# der_f = der_sinai_f
# xlims = sinai_xlims
# ylims = sinai_ylims

T = 50  # Integration time
N = 1000  # Number of discretization points
rtol = 1e-5  # Relative tolerance of the integrator

fps = 20  # Frames per second of the animation
t_real = T  # Actual total time of the integration
tail_length = 50  # Length of the tail balls leave in the animation (seconds)

###
n = len(x0s)
t = np.linspace(0, T, N)
dt = t[1] - t[0]

vs = np.zeros((n, 2, N))
vs[:, 0, 0] = np.array(vx0s)
vs[:, 1, 0] = np.array(vy0s)
xs = np.zeros((n, 2, N))
xs[:, 0, 0] = np.array(x0s)
xs[:, 1, 0] = np.array(y0s)

for i in range(1, N):
    for j in range(n):
        xs[j, :, i] = xs[j, :, i - 1] + vs[j, :, i - 1] * dt
        if f(xs[j, :, i]) < 0:
            vs[j, :, i] = vs[j, :, i - 1]
        else:
            func = lambda tt: f(xs[j, :, i - 1] + tt * (xs[j, :, i] - xs[j, :, i - 1]))
            if func(0) * func(1) < 0:
                t_col = opt.bisect(func, 0, 1, rtol=rtol)
                x_col = xs[j, :, i - 1] + t_col * (xs[j, :, i] - xs[j, :, i - 1])
            else:
                t_col = 1
                x_col = xs[j, :, i]

            normal = der_f(x_col)
            normal = normal / np.linalg.norm(normal)
            tangent = np.array([-normal[1], normal[0]])

            vs[j, :, i] = (
                np.dot(vs[j, :, i - 1], tangent) * tangent
                - np.dot(vs[j, :, i - 1], normal) * normal
            )
            xs[j, :, i] = (
                xs[j, :, i - 1]
                + vs[j, :, i - 1] * dt * t_col
                + vs[j, :, i] * dt * (1 - t_col)
            )


fig, ax = plt.subplots()
lns = []
cols = plt.cm.jet(np.linspace(0, 1, n))
for i in range(n):
    lns.append(ax.plot([], [], "-", color=cols[i])[0])

M = 1000
xx, yy = np.meshgrid(np.linspace(*xlims, M), np.linspace(*ylims, M))
f_vals = np.zeros(np.shape(xx))
for i in range(xx.shape[0]):
    for j in range(xx.shape[1]):
        f_vals[i, j] = f(np.array([xx[i, j], yy[i, j]]))
plt.contour(xx, yy, f_vals, levels=[0], colors="k", linewidths=1.0)


def init():
    ax.set_xlim(xlims)
    ax.set_ylim(ylims)
    ax.set_aspect("equal")
    return lns


def update(ct):
    for i in range(n):
        if ct > tail_length:
            lns[i].set_data(
                xs[i, 0, (ct - tail_length) : ct], xs[i, 1, (ct - tail_length) : ct]
            )
        else:
            lns[i].set_data(xs[i, 0, :ct], xs[i, 1, :ct])
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
# ani.save("images/2.2_sinai_billiard.gif")
