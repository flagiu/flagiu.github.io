import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate as intg
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider, Button


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
N = 500 #1000  # Number of discretization points
rtol = 1e-5  # Relative tolerance of the integrator

fps = 20  # Frames per second of the animation
t_real = 10  # Actual total time of the integration (seconds)

def integrate(G, n, masses, # parameters
              r_0, v_0,  # initial settings
              k, diff,   # copies with error
              T, N, rtol # time integration
              ):
    assert len(masses)==n
    assert len(r_0)==n
    assert len(v_0)==n
    for el in r_0+v_0:
        assert len(el)==3 # cartesian dimensions

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
            for j in range(i+1,n):
                r = positions[j] - positions[i]
                r_norm = np.linalg.norm(r)
                acc_ij = G * masses[j] * r / r_norm**3
                accelerations[i] += acc_ij
                accelerations[j] -= acc_ij

        dydt = np.concatenate((velocities.flatten(), accelerations.flatten()))
        return dydt

    t = np.linspace(0, T, N)
    # redundant: k = len(v_0s)

    ys = np.zeros((k, 2 * n * 3, N))
    for i in range(k):
        r0 = np.array(r_0s[i]).flatten()
        v0 = np.array(v_0s[i]).flatten()
        y0 = np.concatenate((r0, v0))
        ys[i, :, :] = intg.solve_ivp(der_n_body, (t[0], t[-1]), y0, t_eval=t, rtol=rtol).y
    return ys

fig = plt.figure()
ax = plt.axes(projection="3d")
lns = []
x,y,z = None,None,None

def init():
    global n, k, ax, lns, x, y, z
    cols = plt.cm.jet(np.linspace(0, 1, k))
    lns = []
    ax.clear()
    for i in range(n * k):
        lns.append(ax.plot3D([], [], [], "-", color=cols[i // n])[0])
    ax.set_xlim([np.min(x), np.max(x)])
    ax.set_ylim([np.min(y), np.max(y)])
    ax.set_zlim([np.min(z), np.max(z)])
    ax.set_box_aspect(aspect=(1, 1, 1))
    return lns

def run_and_init(event):
    global G_slider, n, masses, r_0, v_0, k, diff, T, N, rtol
    global x,y,z
    ys = integrate(G_slider.val, n, masses, r_0, v_0, k, diff, T, N, rtol)
              
    x = ys[:, ::3, :]
    y = ys[:, 1::3, :]
    z = ys[:, 2::3, :]
    init()
    return

def update(ct):
    global lns, n,k, x, y, z
    for i in range(k):
        for j in range(n):
            lns[i * n + j].set_data(x[i, j, :ct], y[i, j, :ct])
            lns[i * n + j].set_3d_properties(z[i, j, :ct])
    return lns

fig.subplots_adjust(bottom=0.3)
ax1 = fig.add_axes([0.25, 0.1, 0.65, 0.03])
G_slider = Slider(
    ax=ax1,
    label=r"$G$",
    valmin=0.5,
    valmax=4.0,
    valinit=G,
)
# register the update function with each slider
#G_slider.on_changed(run)


run_and_init(None)
ani = FuncAnimation(
    fig,
    update,
    frames=np.arange(0, N, N // (fps * t_real)),
    blit=True,
    interval=1000 / fps,
)

# Create a `matplotlib.widgets.Button` to reset the sliders to initial values.
resetax = fig.add_axes([0.7, 0.025, 0.2, 0.04])
resetButton = Button(resetax, "Reset Sliders", hovercolor="0.975")
def reset(event):
    G_slider.reset()
resetButton.on_clicked(reset)

# Create a `matplotlib.widgets.Button` to run the animation from scratch.
runax = fig.add_axes([0.5, 0.025, 0.1, 0.04])
runButton = Button(runax, "Run", hovercolor="0.975")
runButton.on_clicked(run_and_init)

#run(None)
plt.show()
# ani.save("images/2.3_n_body.gif")
