import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button


def f(t, x0, lam):
    x = np.zeros(t.shape)
    x[0] = x0
    for i in range(1, len(t)):
        x[i] = lam * x[i - 1] * (1 - x[i - 1])
    return x


t = np.arange(25)

# Define initial parameters
init_x0 = 0.6
init_lam = 1.5

fig, ax = plt.subplots()
(line,) = ax.plot(t, f(t, init_x0, init_lam), "x-")
ax.set_xlabel("$t$")
ax.set_ylabel("$x_t$")
ax.set_ylim([0, 1])
plt.grid()

fig.subplots_adjust(bottom=0.3)

ax1 = fig.add_axes([0.25, 0.1, 0.65, 0.03])
lam_slider = Slider(
    ax=ax1,
    label=r"$\lambda$",
    valmin=0,
    valmax=4,
    valinit=init_lam,
)

ax2 = fig.add_axes([0.25, 0.15, 0.65, 0.03])
x0_slider = Slider(
    ax=ax2,
    label="$x_0$",
    valmin=0,
    valmax=1,
    valinit=init_x0,
)


def update(val):
    line.set_ydata(f(t, x0_slider.val, lam_slider.val))
    fig.canvas.draw_idle()


# register the update function with each slider
lam_slider.on_changed(update)
x0_slider.on_changed(update)

# Create a `matplotlib.widgets.Button` to reset the sliders to initial values.
resetax = fig.add_axes([0.8, 0.025, 0.1, 0.04])
button = Button(resetax, "Reset", hovercolor="0.975")


def reset(event):
    lam_slider.reset()
    x0_slider.reset()


button.on_clicked(reset)

plt.show()
