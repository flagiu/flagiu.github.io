import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate as intg
from matplotlib.animation import FuncAnimation

### Input parameters
sigma = 10
b = 8 / 3
r = 28

n = 5  # Number of cases

# Initial conditions, n cases with equally spaced initial positions
diff = 1e-3  # Maximum deviation of initial conditions
factors = np.linspace(1 - diff, 1 + diff, n)
Z0s = 20 * factors
Y0s = [10] * n
X0s = [10] * n

T = 10  # Integration time
N = 1000  # Number of discretization points
rtol = 1e-5  # Relative tolerance of the integrator

fps = 20  # Frames per second of the animation
t_real = T  # Actual total time of the integration (seconds)


###
def lorenz_der(t, yy):
    """
    Diferencialne enačbe Lorenzovega modela
    yy = [x,y,z]
    dyy = [dx/dt,dy/dt,dz/dt]
    params = (sigma,r,beta)
    """
    dyy = np.zeros(3)
    dyy[0] = sigma * (yy[1] - yy[0])
    dyy[1] = yy[0] * (r - yy[2]) - yy[1]
    dyy[2] = yy[0] * yy[1] - b * yy[2]
    return dyy


t = np.linspace(0, T, N)
ys = np.zeros((n, 3, N))
for i in range(n):
    y0 = [X0s[i], Y0s[i], Z0s[i]]
    sol = intg.solve_ivp(lorenz_der, (t[0], t[-1]), y0, t_eval=t, rtol=rtol)
    ys[i, :, :] = sol.y


fig = plt.figure()
ax = plt.axes(projection="3d")
lns = []
cols = plt.cm.jet(np.linspace(0, 1, n))
for i in range(n):
    lns.append(ax.plot3D([], [], [], "-", color=cols[i])[0])


def init():
    ax.set_xlim([-20, 20])
    ax.set_ylim([-25, 25])
    ax.set_zlim([0, 50])
    ax.set_xlabel("$X$")
    ax.set_ylabel("$Y$")
    ax.set_zlabel("$Z$")
    return lns


def update(ct):
    for i in range(n):
        lns[i].set_data(ys[i, 0, :ct], ys[i, 1, :ct])
        lns[i].set_3d_properties(ys[i, 2, :ct])
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
# ani.save("images/2.5_lorenz.gif")
