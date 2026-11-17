"""
Simulation of a 1D Klein-Kramers (KK) particle:

    dx_t = p_t/mass * dt
    dp_t = f(x_t) * dt - gamma/mass * p_t * dt + \\sqrt{2 * gamma * k_B * temp} * dw_t

"""

import argparse
import numpy as np
kB_JK = 1.380649e-23

def simulate_KK(force, mass, gamma, temp, x0, v0,
                dt, n_steps, n_paths, method, seed):
    """Return time array and paths x,v of shape (n_paths, n_steps + 1) each."""
    rng = np.random.default_rng(seed)
    t = np.arange(n_steps + 1) * dt
    x = np.empty((n_paths, n_steps + 1), dtype=float)
    p = np.empty((n_paths, n_steps + 1), dtype=float)
    f = np.empty((n_paths, n_steps + 1), dtype=float)
    x[:, 0] = x0 # m
    p[:, 0] = mass*v0 # kg * m/s
    f[:, 0] = force(x[:, 0]) # N
    noise = rng.standard_normal((n_paths, n_steps))  # adimensional
    kB = 1
    r_langevin = gamma / mass # langevin rate due to damping, s^-1

    if method == "euler":
        std_p = np.sqrt(2 * gamma * kB * temp * dt) # kg * m/s
        for i in range(n_steps):
            x[:, i + 1] = x[:, i] + p[:, i]/mass * dt
            p[:, i + 1] = p[:, i] + f[:, i] * dt - r_langevin * p[:, i] * dt + std_p * noise[:, i]
            f[:, i + 1] = force(x[:, i + 1])
    elif method == "trotter":
        langevin_decay = np.exp(-r_langevin * dt)
        langevin_std = np.sqrt(mass * kB * temp) * np.sqrt(1 - np.exp(-2 * r_langevin * dt))
        dt_half = dt * 0.5
        for i in range(n_steps):
            # iLp dt/2: momentum half step
            p_ = p[:, i] + f[:, i] * dt_half
            # iLq dt/2: position half step
            x_ = x[:, i] + p_ * dt_half
            # iLg dt: exact force-free Langevin step
            p_ = p_ * langevin_decay + langevin_std * noise[:, i]
            # iLq dt/2: position half step
            x[:, i + 1] = x_ + p_ * dt_half
            # iLp dt/2: momentum half step
            f[:, i + 1] = force(x[:, i + 1]) # store for convenience
            p[:, i + 1] = p_ + f[:, i + 1] * dt_half
    else:
        raise ValueError("method must be 'euler' or 'trotter'")
    return t, x, p, f


def analyze_KK(poteng, force, jacob, mass, gamma, temp, x0, v0,
               t, x, p, f,
               burn_factor,
               no_plot, max_path_shown):
    """Analyze the simulated trajectories"""
    n_steps = len(t) # -1 ... but it's the same
    n_paths = x.shape[0]
    kB = 1
    r_langevin = gamma / mass # langevin rate due to damping, s^-1
    sigma_p = np.sqrt(2 * gamma * kB * temp)

    def theoretical_OU_moments(t, rate, mu, sigma, x0):
        mean = mu + (x0 - mu) * np.exp(-rate * t)
        var = sigma**2 / (2.0 * rate) * (1.0 - np.exp(-2.0 * rate * t))
        return mean, var

    def empirical_autocorrelation(X, max_lag):
        """Autocorrelation of one stationary trajectory, lags 0..max_lag."""
        assert len(X.shape)==1 # one trajectory
        X = X - X.mean()
        n = len(X)
        return np.array([np.dot(X[: n - k], X[k:]) / (n - k) for k in range(max_lag + 1)])

    def empirical_crosscorrelation(X, Y, max_lag):
        """Covariance of one stationary trajectory, lags 0..max_lag."""
        assert len(X.shape)==1 and len(Y.shape)==1 and len(X)==len(Y) # one trajectory
        X = X - X.mean()
        Y = Y - Y.mean()
        n = len(X)
        return np.array([np.dot(X[: n - k], Y[k:]) / (n - k) for k in range(max_lag + 1)])

    def gaussian(X, mu, var):
        return np.exp(-(X - mu) ** 2 / (2 * var)) / np.sqrt(2 * np.pi * var)


    # discard ~5 relaxation times
    dt = t[1]-t[0]
    burn = int(burn_factor / (r_langevin * dt))
    #t_transient = t[:burn]
    #x_transient = x[:, :burn]
    #p_transient = p[:, :burn]
    #f_transient = f[:, :burn]
    t = t[burn:]
    x = x[:, burn:]
    p = p[:, burn:]
    f = f[:, burn:]

    x_mean_emp, x_var_emp = x.mean(axis=0), x.var(axis=0)
    x3_mom_emp = ((x - x_mean_emp)**3).mean(axis=0)
    x4_mom_emp = ((x - x_mean_emp)**4).mean(axis=0)
    x_skew_emp = x3_mom_emp / x_var_emp**(3/2)
    x_kurt_emp = x4_mom_emp / x_var_emp**2 - 3.0

    p_mean_emp, p_var_emp = p.mean(axis=0), p.var(axis=0)
    p_mean_th, p_var_th = theoretical_OU_moments(t, r_langevin, 0, sigma_p, mass*v0)
    p3_mom_emp = ((p - p_mean_emp)**3).mean(axis=0)
    p4_mom_emp = ((p - p_mean_emp)**4).mean(axis=0)
    p_skew_emp = p3_mom_emp / p_var_emp**(3/2)
    p_kurt_emp = p4_mom_emp / p_var_emp**2 - 3.0

    f_mean_emp, f_var_emp = f.mean(axis=0), f.var(axis=0)
    f3_mom_emp = ((f - f_mean_emp)**3).mean(axis=0)
    f4_mom_emp = ((f - f_mean_emp)**4).mean(axis=0)
    f_skew_emp = f3_mom_emp / f_var_emp**(3/2)
    f_kurt_emp = f4_mom_emp / f_var_emp**2 - 3.0

    print()
    print(f"Final x mean:     simulated = {x_mean_emp[-1]: .4f}")
    print(f"Final x variance: simulated = {x_var_emp[-1]: .4f}")
    print()
    print(f"Final p mean:     simulated = {p_mean_emp[-1]: .4f}   free theory = {p_mean_th[-1]: .4f}")
    print(f"Final p variance: simulated = {p_var_emp[-1]: .4f}   free theory = {p_var_th[-1]: .4f}")
    print(f"  Stationary p variance (free theory) = {sigma_p**2 / (2 * r_langevin):.4f}")

    if no_plot:
        return

    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed; skipping plots.")
        return

    fig, axes = plt.subplots(3, 4, figsize=(20, 12))
    
    # 1) Sample trajectories + mean +/- 2 std
    n_paths_shown = min(max_path_shown, n_paths)

    ax = axes[0, 0]    
    for i in range(n_paths_shown):
        ax.plot(t, x[i], lw=0.7, alpha=0.7)
    ax.set(xlabel=r"$t$", ylabel=r"$x(t)$", title="Sample trajectories")
    ax.plot(t, x_mean_emp, "b", lw=2, label="mean (sim.)")
    ax.fill_between(t,
                    x_mean_emp - 2 * np.sqrt(x_var_emp),
                    x_mean_emp + 2 * np.sqrt(x_var_emp),
                    color="lightblue", alpha=0.2, label=r"mean $\pm 2\sigma_t$ (sim.)")
    ax.legend()

    ax = axes[1, 0]
    for i in range(n_paths_shown):
        ax.plot(t, p[i], lw=0.7, alpha=0.7)
    ax.plot(t, p_mean_th, "k", lw=2, label="free theory mean")
    ax.fill_between(t,
                    p_mean_th - 2 * np.sqrt(p_var_th),
                    p_mean_th + 2 * np.sqrt(p_var_th),
                    color="gray", alpha=0.2, label=r"free theory $\pm 2\sigma_t$")
    ax.set(xlabel=r"$t$", ylabel=r"$p(t)$")
    ax.legend()

    ax = axes[2, 0]    
    for i in range(n_paths_shown):
        ax.plot(t, f[i], lw=0.7, alpha=0.7)
    ax.set(xlabel=r"$t$", ylabel=r"$f(t)$")
    ax.plot(t, f_mean_emp, "b", lw=2, label="mean (sim.)")
    ax.fill_between(t,
                    f_mean_emp - 2 * np.sqrt(f_var_emp),
                    f_mean_emp + 2 * np.sqrt(f_var_emp),
                    color="lightblue", alpha=0.2, label=r"mean $\pm 2\sigma_t$ (sim.)")
    ax.legend()

    # 2) Momentum mean and variance, vs theory
    ax = axes[0, 1]
    ax.plot(t, x_mean_emp, label="mean (sim)")
    ax.fill_between(t,
                    x_mean_emp - 2 * np.sqrt(x_var_emp/(n_paths-1)),
                    x_mean_emp + 2 * np.sqrt(x_var_emp/(n_paths-1)),
                    color="C0", alpha=0.2, label=r"$\pm 2$ st.d of mean (sim)")
    #ax.plot(t, x_mean_th, "--", label="mean (theory)")
    ax.plot(t, x_var_emp, label="variance (sim)")
    #ax.plot(t, x_var_th, "--", label="variance (theory)")
    ax.plot(t, x_skew_emp, label="skew (sim)")
    ax.plot(t, x_kurt_emp, label="Fisher's kurtosis (sim)")
    ax.set(xlabel=r"$t$", title=r"Moments of $x$") #, xscale="log", yscale="log")
    ax.legend()

    ax = axes[1, 1]
    ax.plot(t, p_mean_emp, label="mean (sim)")
    ax.fill_between(t,
                    p_mean_emp - 2 * np.sqrt(p_var_emp/(n_paths-1)),
                    p_mean_emp + 2 * np.sqrt(p_var_emp/(n_paths-1)),
                    color="C0", alpha=0.2, label=r"$\pm 2$ st.d of mean (sim)")
    ax.plot(t, p_mean_th, "--", label="mean (free theory)")
    ax.fill_between(t,
                    p_mean_th - 2 * np.sqrt(p_var_th/(n_paths-1)),
                    p_mean_th + 2 * np.sqrt(p_var_th/(n_paths-1)),
                    color="C1", alpha=0.2, label=r"$\pm 2$ st.d of mean (free th.)")
    ax.plot(t, p_var_emp, label="var. (sim)")
    ax.plot(t, p_var_th, "--", label="var. (free theory)")
    ax.plot(t, p_skew_emp, label="skew (sim)")
    ax.plot(t, p_kurt_emp, label="Fisher's kurtosis (sim)")
    ax.set(xlabel=r"$t$", title=r"Moments of $p$")
    ax.legend()

    ax = axes[2, 1]
    ax.plot(t, f_mean_emp, label="mean (sim)")
    ax.fill_between(t,
                    f_mean_emp - 2 * np.sqrt(f_var_emp/(n_paths-1)),
                    f_mean_emp + 2 * np.sqrt(f_var_emp/(n_paths-1)),
                    color="C0", alpha=0.2, label=r"$\pm 2$ st.d of mean (sim)")
    #ax.plot(t, x_mean_th, "--", label="mean (theory)")
    ax.plot(t, f_var_emp, label="variance (sim)")
    #ax.plot(t, x_var_th, "--", label="variance (theory)")
    ax.plot(t, f_skew_emp, label="skew (sim)")
    ax.plot(t, f_kurt_emp, label="Fisher's kurtosis (sim)")
    ax.set(xlabel=r"$t$", title=r"Moments of $f$") #, xscale="log", yscale="log")
    ax.legend()

    # 3) Final-time distribution vs Gaussian
    ax = axes[0, 2]
    ax.hist(x[:, -1], bins=50, density=True, alpha=0.6, label="sim.")
    xs = np.linspace(x[:, -1].min(), x[:, -1].max(), 400)
    Px = np.exp(-poteng(xs)/(kB*temp)) # Boltzmann distribution
    Px /= np.diff(xs)[0] * Px.sum() # normalize to area and histogram
    ax.plot(xs, Px, "k", label="Theory")
    ax.set(xlabel=r"$x(t_f)$", ylabel="density", title="Distribution at final time", yscale="log")
    ax.legend()

    ax = axes[1, 2]
    ax.hist(p[:, -1], bins=50, density=True, alpha=0.6, label="sim.")
    ps = np.linspace(p[:, -1].min(), p[:, -1].max(), 400)
    ax.plot(ps, gaussian(ps, p_mean_th[-1], p_var_th[-1]), "k", label="Free theory")
    ax.set(xlabel=r"$p(t_f)$", ylabel="density", title="Distribution at final time", yscale="log")
    ax.legend()

    ax = axes[2, 2]
    ax.hist(f[:, -1], bins=50, density=True, alpha=0.6, label="sim.")
    fs = force(xs)
    Pf = Px / np.abs(jacob(xs))
    ax.plot(fs, Pf, "k", label="Theory")
    ax.set(xlabel=r"$f(t_f)$", ylabel="density", title="Distribution at final time", yscale="log")
    ax.legend()

    # 4) Autocorrelation of a long stationary trajectory
    max_lag = int(20.0 / (r_langevin * dt))
    lags = np.arange(max_lag + 1) * dt
    Cxx = empirical_autocorrelation(x[0], max_lag)
    Cpp = empirical_autocorrelation(p[0], max_lag)
    Cff = empirical_autocorrelation(f[0], max_lag)
    Cxp = empirical_crosscorrelation(x[0], p[0], max_lag)
    Cxf = empirical_crosscorrelation(x[0], f[0], max_lag)
    Cpf = empirical_crosscorrelation(p[0], f[0], max_lag)
    
    ax = axes[0, 3]
    ax.plot(lags, Cxx, label=r"$C_{xx}(\tau)$ (sim.)")
    ax.plot(lags, Cxp, label=r"$C_{xp}(\tau)$ (sim.)")
    ax.plot(lags, Cxf, label=r"$C_{xf}(\tau)$ (sim.)")
    ax.set(xlabel=r"$\tau$", title="Stationary autocorrelation")
    ax.legend()

    ax = axes[1, 3]
    ax.plot(lags, Cpp, label="simulation")
    ax.plot(lags, sigma_p**2 / (2 * r_langevin) * np.exp(-r_langevin * lags),
            "k--", label=r"$\frac{\sigma_p^2}{2 \gamma / m}e^{-\gamma/m \tau}$")
    ax.set(xlabel=r"$\tau$", ylabel=r"$C_{pp}(\tau)$")
    ax.legend()

    ax = axes[2, 3]
    ax.plot(lags, Cff, label=r"$C_{ff}(\tau)$ (sim.)")
    ax.plot(lags, Cpf, label=r"$C_{pf}(\tau)$ (sim.)")
    ax.set(xlabel=r"$\tau$", title="Stationary autocorrelation")
    ax.legend()

    plt.tight_layout()
    plt.savefig("KK_simulation.png", dpi=150)
    print("Saved plot to KK_simulation.png")
    #plt.show()


def main():
    p = argparse.ArgumentParser(description="1D Klein-Kramers simulation")
    p.add_argument("--mass", type=float, default=1.0, help="kg")
    p.add_argument("--gamma", type=float, default=1.0, help="friction coefficient, kg/s")
    p.add_argument("--temp", type=float, default=0.1, help="temperature, Joule")
    p.add_argument("--force", choices=["zero", "harmonic", "double-well"], default="double-well", help="force option")
    p.add_argument("--k2", type=float, default=-3.0, help="coefficient of x^2/2 [N/m] for polynomial forces")
    p.add_argument("--k4", type=float, default=1.0, help="coefficient of x^4/4 [N/m^3] for polynomial forces")
    p.add_argument("--x0", type=float, default=-1.7, help="initial position, m")
    p.add_argument("--v0", type=float, default=0.0, help="initial velocity, m/s")
    p.add_argument("--dt", type=float, default=0.01, help="integration time step")
    p.add_argument("--tsim", type=float, default=100.0, help="total simulation time")
    p.add_argument("--paths", type=int, default=2000, help="number of independent paths")
    p.add_argument("--method", choices=["euler", "trotter"], default="trotter", help="integration method option")
    p.add_argument("--seed", type=int, default=42, help="random number generator seed")
    p.add_argument("--burn_factor", type=float, default=10.0, help="transient time to burn for stationary measures, in units of mass/gamma")
    p.add_argument("--no-plot", action="store_true")
    p.add_argument("--save-paths", action="store_true")
    p.add_argument("--max_path_shown", type=int, default=8, help="show only a subset of simulated paths")
    args = p.parse_args()

    force, poteng, jacob = None, None, None
    if args.force == "zero":
        poteng = lambda x: 0.0*x
        force = lambda x: 0.0*x
        jacob = lambda x: 0.0*x
    elif args.force == "harmonic":
        k = args.k2
        poteng = lambda x: k*x**2/2
        force = lambda x: -k*x
        jacob = lambda x: k*np.ones_like(x)
    elif args.force == "double-well":
        k2 = args.k2
        k4 = args.k4
        poteng = lambda x: k2*x**2/2 + k4*x**4/4
        force = lambda x: - k2*x - k4*x**3
        jacob = lambda x: k2 + 3*k4*x**2
    else:
        raise ValueError("force must be 'zero' or 'harmonic'")

    n_steps = int(round(args.tsim / args.dt))
    print(f"Method: {args.method}, paths: {args.paths}, steps: {n_steps}, dt: {args.dt}")

    t, x, p, f = simulate_KK(force, args.mass, args.gamma, args.temp, args.x0, args.v0,
                             args.dt, n_steps, args.paths, args.method, args.seed)

    if args.save_paths:
        np.savetxt("KK_x.dat", np.array([t,*x]).T, fmt="%f")
        np.savetxt("KK_p.dat", np.array([t,*p]).T, fmt="%f")
        np.savetxt("KK_f.dat", np.array([t,*f]).T, fmt="%f")
        print("Saved trajectories into KK_{x,p,f}.dat")

    analyze_KK(poteng, force, jacob, args.mass, args.gamma, args.temp,
               args.x0, args.v0,
               t, x, p, f,
               args.burn_factor, args.no_plot, args.max_path_shown)
    return


if __name__ == "__main__":
    main()
