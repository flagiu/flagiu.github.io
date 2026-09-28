import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate as intg
from matplotlib.animation import FuncAnimation

### Input parameters
G = 1  # Gravitational constant
n = 3  # Number of bodies
masses = [1] * n  # Masses

k = 2  # Number of cases
diff = 1e-3  # Maximum difference in initial conditions

# Initial conditions
r_0 = [[1, 0, 0], [0, -1, 0], [0, -1, 1]]
v_0 = [[0, 1, 0], [0, 0, 1], [1, 0, 0]]

T = 30  # Integration time
N = 1000  # Number of discretization points
rtol = 1e-5  # Relative tolerance of the integrator

fps = 20  # Frames per second of the animation
t_real = 10  # Actual total time of the integration (seconds)

###
factors = np.linspace(1 - diff, 1 + diff, k)
v_0s = [np.array(v_0) * i for i in factors]
r_0s = [np.array(r_0) * i for i in factors]


###
def der_n_body(t, y):
    positions = y[: 3 * n]
    velocities = y[3 * n :]
    positions = positions.reshape((n, 3))
    velocities = velocities.reshape((n, 3))

    accelerations = np.zeros((n, 3))
    for i in range(n):
        for j in range(n):
            if i != j:
                r = positions[j] - positions[i]
                r_norm = np.linalg.norm(r)
                accelerations[i] += G * masses[j] * r / r_norm**3

    dydt = np.concatenate((velocities.flatten(), accelerations.flatten()))
    return dydt


t = np.linspace(0, T, N)
k = len(v_0s)

ys = np.zeros((k, 2 * n * 3, N))
for i in range(k):
    r0 = np.array(r_0s[i]).flatten()
    v0 = np.array(v_0s[i]).flatten()
    y0 = np.concatenate((r0, v0))
    ys[i, :, :] = intg.solve_ivp(der_n_body, (t[0], t[-1]), y0, t_eval=t, rtol=rtol).y

fig = plt.figure()
ax = plt.axes(projection="3d")

lns = []
cols = plt.cm.jet(np.linspace(0, 1, k))
for i in range(n * k):
    lns.append(ax.plot3D([], [], [], "-", color=cols[i // n])[0])


x = ys[:, ::3, :]
y = ys[:, 1::3, :]
z = ys[:, 2::3, :]


def init():
    ax.set_xlim([np.min(x), np.max(x)])
    ax.set_ylim([np.min(y), np.max(y)])
    ax.set_zlim([np.min(z), np.max(z)])
    ax.set_box_aspect(aspect=(1, 1, 1))
    return lns


def update(ct):
    for i in range(k):
        for j in range(n):
            lns[i * n + j].set_data(x[i, j, :ct], y[i, j, :ct])
            lns[i * n + j].set_3d_properties(z[i, j, :ct])
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
# ani.save("images/2.3_n_body.gif")
