import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from matplotlib.animation import FuncAnimation
from functools import partial

"""
TO BDE COMPLETED!

Field-Golubitsky symmetric attractors
https://paulbourke.net/fractals/symmetryinchaos/
profconradi.com

modified:
     f(z) = z (a_0 + a_1 z z* + a_2 Re[z^n] + a_3 |z| Re[(z/|z|)^(n*p) ] ) + a_4 z*^(n-1)
 original:
     f(z) = z (a_0 + a_1 z z* + a_2 Re[z^n] + a_3 i ] ) + a_4 z*^(n-1)
     f(z) = z (lambda + alpha z z* + beta Re[z^n] +  i omega ] ) + gamma z*^(n-1)
     lambda -> a0
     alpha -> a1
     beta -> a2
     omega -> a3
     gamma -> a4
    z is complex; a0, ..., a4 are real parameters; n,p are positive integers?
    A rough guide to parameters.
        - The value of n determines the rotational symmetry of the image, it should be greater than or equal to 2.
        - a0 is usually between -3 and 3, values between -1 and 1 are generally less interesting.
        - a1 should have the opposite sign as a0, and be in the same range.
        - a2 perturbs the attractor, it can be 0.
        - a3 controls bilateral symmetry, 0 will result in mirror symmetry. Otherwise typical values are between -1 and 1.
        - a4 typically between -1 and 1 and not too close to zero.
    
Drawing method:
    1 iterate the map for about 1000 times, to get the boundaries
    2 iterate for about 10-1000 milion times and count a 2D histogram 
    3 draw the 2D histogram
"""

def f_original(z, a0, a1, a2, a3, a4, n, p):
    zc = z.conjugate()
    za = abs(z)
    o = a0 + a1*z*zc + a2*(z**n).real + a3*1j
    o = o*z + a4*zc**(n-1)
    return o

def f_modified(z, a0, a1, a2, a3, a4, n, p):
    zc = z.conjugate()
    za = abs(z)
    o = a0 + a1*z*zc + a2*(z**n).real + a3*za*((z/za)**(n*p)).real
    o = o*z + a4*zc**(n-1)
    return o

def get_filename(a0, a1, a2, a3, a4, n, p, N, resolution_x):
    return f"symm-chaos_a0{a0:.3f}_a1{a1:.3f}_a2{a2:.3f}_a3{a3:.3f}_a4{a4:.3f}_n{n:d}_p{p:d}_N{N:d}_res{resolution_x:d}"

def get_succession(f, z0, N):
    xs = np.empty(N+1, dtype=np.float32)
    ys = np.empty(N+1, dtype=np.float32)
    z = z0
    xs[0] = z.real
    ys[0] = z.imag
    for i in range(1,N+1):
        z = f(z)
        xs[i] = z.real
        ys[i] = z.imag
    return xs, ys

def get_succession_boundaries(f, z0, N, equal=True):
    xmin, xmax = 99999, -99999
    ymin, ymax = 99999, -99999
    z = z0
    for _ in range(1,N+1):
        z = f(z)
        xmin = min(xmin, z.real)
        xmax = max(xmax, z.real)
        ymin = min(ymin, z.imag)
        ymax = max(ymax, z.imag)
    if equal:
        xmin = min(xmin,ymin)
        xmax = max(xmax,ymax)
        ymin = xmin
        ymax = xmax
    extent = (xmin, xmax, ymin, ymax)
    return extent, z

def get_succession_histogram(extent, pad, resolution,  f, z0, N):
    xmin, xmax, ymin, ymax = extent
    xpad, ypad = pad
    Nx, Ny = resolution
    x = np.linspace(xmin-xpad, xmax+xpad, Nx)
    y = np.linspace(ymin-ypad, ymax+ypad, Ny)
    x0,x1, Lx = x[0],x[-1], x[-1]-x[0]
    y0,y1, Ly = y[0],y[-1], y[-1]-y[0]
    counts = np.zeros((Nx,Ny), dtype=np.uint32)
    z = z0
    for i in range(1,N+1):
        if i%10000 == 0:
            print(f"\r [ {i/N*100:.1f}% ({i:d} / {N:d}) ... ]", end='', flush=True)
        z = f(z)
        if z.real>x0 and z.real<x1 and z.imag>y0 and z.imag<y1:
            ix = int((z.real - x0)/Lx * Nx)
            iy = int((z.imag - y0)/Ly * Ny)
            counts[ix,iy] += 1
    print(" completed", flush=True)
    return counts, z

def plot_histogram(ax, counts, cmap="gnuplot", log=True):
    img = counts
    if log:
        sel=(counts>0)
        img[sel] = np.log(img[sel])
    aximg = ax.imshow(img, aspect="equal", cmap=cmap) #extent=extent)
    ax.set(xticks=[], yticks=[])
    return aximg

"""
A rough guide to parameters.
        - The value of n determines the rotational symmetry of the image, it should be greater than or equal to 2.
        - a0 is usually between -3 and 3, values between -1 and 1 are generally less interesting.
        - a1 should have the opposite sign as a0, and be in the same range.
        - a2 perturbs the attractor, it can be 0.
        - a3 controls bilateral symmetry, 0 will result in mirror symmetry. Otherwise typical values are between -1 and 1.
        - a4 typically between -1 and 1 and not too close to zero.
    lambda -> a0
    alpha -> a1
    beta -> a2
    omega -> a3
    gamma -> a4
"""

def main(
    f = f_original,
    a0 = -1.86,
    a1 = 2.0,
    a2 = 0.0,
    a3 = 0.1,
    a4 = 1.0,
    n = 4,
    p = 1, #useless if f == f_original
    z0 = 0.1+0.3214j,
    xpad = 0.0,
    xres = 400,
    N0 = 1000,
    N = 100_000,
    batch_size = 20_000,
):
    pad = (xpad, xpad)
    resolution = (xres, xres)

    # Get data
    firstUpdate = True    
    params = (a0, a1, a2, a3, a4, n, p)
    func = lambda z: f(z,*params)
    fileroot = f"{get_filename(*params, N, xres)}"
    print(fileroot + " ... ", flush=True)
    extent, z_last = get_succession_boundaries(func, z0, N0)
    print(" extent of attractor is: %f %f %f %f"%extent)
    n_batch = N//batch_size
    print(f" computing batch 1/{n_batch}")
    counts, z_last = get_succession_histogram(extent, pad, resolution, func, z_last, batch_size)
    count_list = [counts] # for the animation
    
    # Main plot
    fig, ax = plt.subplots(figsize=(8,10), dpi=200)
    aximg = plot_histogram(ax, counts)
    #f(z) = z (a_0 + a_1 z z* + a_2 Re[z^n] + a_3 i ] ) + a_4 z*^(n-1)
    title="Symmetric chaotic attractor of the complex map:\n"
    title+=r"$f(z) = \left(a_0 + a_1 z \bar{z} + a_2 \mathrm{Re}[z^n] + i a_3 \right) z + a_4 z^{n-1}$"
    title+="\nhttps://paulbourke.net/fractals/symmetryinchaos/"
    ax.set_title(title)
    
    # Add bottom slider(s)
    fig.subplots_adjust(bottom=0.3)

    # $a_2$ perturbs the attractor if $\neq 0$
    # $a_3$ controls bilateral symmetry. Mirror symmetry if $0$, otherwise best $\in[-1,1]$
    # $a_4$ typically $\in[-1,1]$ and not too close to $0$.

    ax_a0 = fig.add_axes([0.55, 0.25, 0.25, 0.03])
    a0_slider = Slider(
        ax=ax_a0,
        label=r"$a_0$ usually $\in[-3,3]$; best values are outside $[ -1,1]$",
        valmin=-3,
        valmax=3,
        valinit=a0,
        valstep=0.01,
        valfmt="%.2f"
    )

    ax_a1 = fig.add_axes([0.55, 0.2, 0.25, 0.03])
    a1_slider = Slider(
        ax=ax_a1,
        label=r"$a_1$ should be $\sim -a_0$",
        valmin=-3,
        valmax=3,
        valinit=a1,
        valstep=0.01,
        valfmt="%.2f"
    )

    ax_n = fig.add_axes([0.55, 0.15, 0.25, 0.03])
    n_slider = Slider(
        ax=ax_n,
        label=r"$n$ controls the rotational symmetry",
        valmin=2,
        valmax=5,
        valinit=n,
        valstep=1,
        valfmt="%.0f"
    )

    ax_N = fig.add_axes([0.55, 0.1, 0.25, 0.03])
    N_slider = Slider(
        ax=ax_N,
        label=r"$N$ is the number of iterations of the map",
        valmin=100_000,
        valmax=10_000_000,
        valinit=N,
        valstep=1000,
        valfmt="%.0f"
    )

    sliders = [
        a0_slider, a1_slider, n_slider, N_slider
    ]

    
    def animate(val):
        nonlocal sliders, aximg, extent, pad, resolution, func, z0, z_last, a0, a1, a2, a3, a4, n, p, N0, N, batch_size, counts
        a0, a1, n, N = [slider.val for slider in sliders]
        params = (a0, a1, a2, a3, a4, n, p)
        func = lambda z: f(z,*params)
        fileroot = f"{get_filename(*params, N, xres)}"
        print(fileroot + " ... ", flush=True)
        extent, z_last = get_succession_boundaries(func, z0, N0)
        print(" extent of attractor is: %f %f %f %f"%extent)
        print(f" computing batch 1/{n_batch} ... ", flush=True)
        n_batch = N//batch_size
        counts, z_last = get_succession_histogram(extent, pad, resolution, func, z_last, batch_size)
        for batch in range(1,n_batch):
            print(f" computing batch {batch+1}/{n_batch}")
            new_counts, z_last = get_succession_histogram(extent, pad, resolution, func, z_last, batch_size)
            counts += new_counts
            aximg.set_array(counts)
            fig.canvas.draw_idle()        


    # register the update function with each slider
    #for slider in sliders:
    #    slider.on_changed(update)
    
    # Create a `matplotlib.widgets.Button` to reset the sliders to initial values.
    reset_ax = fig.add_axes([0.8, 0.025, 0.1, 0.04])
    reset_button = Button(reset_ax, "Reset", hovercolor="0.975")
    def reset(event, sliders=sliders):
        for slider in sliders:
            slider.reset()
        print("Reset to initial values!", flush=True)
    reset_button.on_clicked(reset)
    # ... one to run the calculations
    update_ax = fig.add_axes([0.5, 0.025, 0.1, 0.04])
    update_button = Button(update_ax, "Update", hovercolor="0.975")
    update_button.on_clicked(animate)
    # ... and one to save the output image
    save_ax = fig.add_axes([0.2, 0.025, 0.1, 0.04])
    save_button = Button(save_ax, "Save", hovercolor="0.975")
    def save(event, fig=fig, fileroot=fileroot, fmt="png"):
        fig.savefig(f"{fileroot}.{fmt}")
        print("Saved figure!", flush=True)
    save_button.on_clicked(save)

    def init_anim():
        ax.set_title(title)
        return [aximg]

    def update_anim(ct):
        nonlocal ax, aximg, count_list, extent, pad, resolution, func, z_last, batch_size
        if ct<n_batch: #compute stuff
            new_counts, z_last = get_succession_histogram(extent, pad, resolution, func, z_last, batch_size)
            count_list.append(count_list[-1]+new_counts)
            counts = count_list[-1]
        print(f"ct={ct} ; batch_size={batch_size}")
        #aximg.set_array(counts)
        aximg = plot_histogram(ax, count_list[ct%n_batch])
        return [aximg]

    frames_per_sec = 0.5  # Frames per second of the animation
    t_real = 10 #ts[-1]  # Actual total time of the integration (seconds)
    n_batch = N // batch_size
    ani = FuncAnimation(
        fig,
        update_anim,
        frames=np.arange(0, n_batch, n_batch // (frames_per_sec * t_real), dtype=np.int32),
        init_func=init_anim,
        blit=True,
        interval=1000 / frames_per_sec,
    )

    plt.show()


if __name__=='__main__':
    main()