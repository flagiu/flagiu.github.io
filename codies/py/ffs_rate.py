"""
Forward-Flux Sampling (FFS) of the A -> B transition rate for a 1D Brownian
particle in a double-well potential (left well A at x = -1, right well B at x = +1).

Algorithm (Allen, Valeriani, ten Wolde, J. Phys.: Condens. Matter 21, 463102 (2009)),
order parameter lambda = x:

  Stage 0 : run one long trajectory in A. Every time it crosses the first interface
            lambda_0 (coming from A) store the configuration. The flux is
            Phi_{A,0} = N_crossings / (Volume * T_simulated).
  Stage i : launch M trial runs from randomly chosen stored points on lambda_i.
            A trial succeeds if it reaches lambda_{i+1} before falling back to A
            (x <= lambda_A); successes are stored. P(i+1 | i) = successes / M.
  Rate    : k_AB = Phi_{A,0} * prod_i P(i+1 | i)

Because the dynamics are overdamped, the "configuration" is just x.
Independent repetitions of the whole procedure ("blocks") give the error bar.

----------------------------------------------------------------------------
HOOKING UP YOUR OWN MODULE
Edit ONLY make_integrator() below. It must return a function step(x) -> x_new
that advances the particle by one time step dt. Everything else is generic.
If no module is found, a built-in Euler-Maruyama integrator for
U(x) = Eb * (x^2 - 1)^2 is used.
----------------------------------------------------------------------------
"""

import argparse
import time

import numpy as np


# ---------------------------------------------------------------------------
# Adapter to the Brownian-dynamics module  (the only part you need to edit)
# ---------------------------------------------------------------------------
def make_integrator(seed, dt, mass, gamma, kT, Eb):
    """Return step(x) -> x_new and the potential U(x) (U used only for Kramers estimate)."""
    from KK_simulation import simulate_KK
    poteng = lambda x: Eb*(x**2 - 1)**2
    force = lambda x: -4*Eb*(x**3 - x)
    jacob = lambda x: 4*Eb*(3*x**2 - 1)
    def step(x, p):
        t,x,p,f = simulate_KK(
            force, mass, gamma, kT, x, p,
            dt, 1, 1, "trotter", seed
        )
        return x[:,-1], p[:,-1]
    return step, poteng, jacob

# ---------------------------------------------------------------------------
# One full FFS run
# ---------------------------------------------------------------------------
def run_ffs(step, interfaces, lam_A, n_crossings, n_trials, dt, rng,
            equil_steps, max_trial_steps, max_stage0_steps,
            x_start=-1.0, p_start=0.0,
            verbose=True):
    lam0 = interfaces[0]

    # ---- Stage 0: flux through lambda_0 ----
    # equilibrate
    x,p = x_start, p_start
    for _ in range(equil_steps):
        x,p = step(x,p)
    if x>=interfaces[0]:
        raise RuntimeError("Entered lambda_0 during first equilibration "
                            "decrease t_equil or increase lamA or decrease n_interfaces")

    # compute the equilibrium in-flux rate \dot{\Phi_0}
    points = []            # collect the crossings of lambda_0 coming from A
    in_A = (x <= lam_A)
    n_steps = 0
    lam_B = interfaces[-1]
    while len(points) < n_crossings and n_steps < max_stage0_steps:
        if n_steps%1000 == 0:
            print(f"\r  [ step {n_steps} ; {len(points)} points collected ... ]", end='')
        x,p = step(x,p)
        n_steps += 1
        if x >= lam_B:
            # Particle reached B: stage 0 must sample the A-basin only, so reinject
            # into A and relax (this relaxation time is NOT counted in the flux).
            x,p = x_start, p_start
            for _ in range(equil_steps):
                x,p = step(x,p)
            in_A = True
            continue
        if x <= lam_A:
            in_A = True
        elif x >= lam0 and in_A:        # crossing of lambda_0 coming from A
            points.append([x,p])
            in_A = False
    print(f"\r  [ completed ]                                            ")
    if len(points) == 0:
        raise RuntimeError("No crossings of lambda_0 observed in stage 0; "
                           "increase max_stage0_steps or lower lambda_0.")
    flux = len(points) / (n_steps * dt)
    if verbose:
        print(f"  stage 0: {len(points)} crossings in t = {n_steps * dt:.2f}  ->  flux = {flux:.4g}")

    # ---- Stages i -> i+1 ----
    probs = []
    for i in range(len(interfaces) - 1):
        lam_next = interfaces[i + 1]
        starts = rng.choice(points, size=n_trials, replace=True)
        new_points = []
        for start in starts:
            x,p = start
            for _ in range(max_trial_steps):
                x,p = step(x,p)
                if x >= lam_next:
                    new_points.append([x,p])
                    break
                if x <= lam_A:
                    break
        prob = len(new_points) / n_trials
        probs.append(prob)
        if verbose:
            print(f"  interface {i} -> {i + 1} (x = {interfaces[i]:+.2f} -> {lam_next:+.2f}): "
                  f"P = {prob:.4f}  ({len(new_points)}/{n_trials})")
        if not new_points:
            return flux, probs, 0.0
        points = new_points

    return flux, probs, flux * float(np.prod(probs))


def kramers_rate(U, ddU, kT, gamma, x_min=-1.0, x_max=0.0):
    """Kramers estimate k = sqrt(U''(xmin)|U''(xmax)|)/(2 pi gamma) exp(-dU/kT)."""
    dU = U(x_max) - U(x_min)
    return np.sqrt(ddU(x_min) * abs(ddU(x_max))) / (2 * np.pi * gamma) * np.exp(-dU / kT)

def print_problem(U, lam_A, lam_B, interfaces, x_start=-1.0, x_end=1.0):
    import matplotlib.pyplot as plt
    import sys
    Acol, Bcol = 'red', 'green'
    fig,ax = plt.subplots()
    dx=0.5
    xl = np.linspace(x_start-dx,x_end+dx,400)
    Ul=U(xl)
    dU=0.1
    ax.plot(xl,Ul)
    Umin,Umax = -0.5, Ul.max()
    n = len(interfaces)
    #
    ax.fill_between([xl[0],lam_A], Umin, Umax, color=Acol, alpha=0.2)
    ax.axvline(lam_A, ls='--', color=Acol)
    ax.text(lam_A, Umax+dU, r"$\lambda_\mathrm{A}$", ha="center", va="bottom")
    ax.scatter(x_start, U(x_start), marker='o', color=Acol, alpha=0.9)
    ax.text(x_start, U(x_start)+2*dU, "A", ha="center", va="bottom", fontsize="large")
    #
    ax.fill_between([lam_B,xl[-1]], Umin, Umax, color=Bcol, alpha=0.2)
    ax.axvline(lam_B, ls='--', color=Bcol)
    ax.text(lam_B, Umax+dU, r"$\lambda_n \equiv \lambda_\mathrm{B}$", ha="center", va="bottom")
    ax.scatter(x_end, U(x_end), marker='o', color=Bcol, alpha=0.9)
    ax.text(x_end, U(x_end)+2*dU, "B", ha="center", va="bottom", fontsize="large")
    #
    for i,lam in enumerate(interfaces[:-1]):
        ax.axvline(lam, ls='--', color='k')
        if i<n//2:
            ax.text(lam, Umax+dU, r"$\lambda_{%d}$"%i, ha="center", va="bottom")
    ax.set(xlim=(xl[0],xl[-1]), ylim=(Umin, Umax),
           xlabel=r"Order parameter $\lambda$", ylabel="Potential energy",
           xticks=[], yticks=[])
    fig.savefig("ffs_rate_problem.png")
    print("Saved ffs_rate_problem.png")
    sys.exit()


def main():
    p = argparse.ArgumentParser(description="FFS rate for a 1D double-well Brownian particle")
    p.add_argument("--mass", type=float, default=1.0)
    p.add_argument("--kT", type=float, default=1.0)
    p.add_argument("--gamma", type=float, default=1.0)
    p.add_argument("--Eb", type=float, default=10.0, help="barrier height (fallback potential only)")
    p.add_argument("--dt", type=float, default=1e-3)
    p.add_argument("--lam_A", type=float, default=-0.9, help="boundary of basin A: x <= lam_A")
    p.add_argument("--lam_B", type=float, default=0.8, help="boundary of basin B (last interface)")
    p.add_argument("--n_interfaces", type=int, default=5, help="interfaces from lambda_0 to lam_B")
    p.add_argument("--lam0", type=float, default=-0.7, help="first interface lambda_0")
    p.add_argument("--t_equil", type=float, default=0.1, help="stage-0 time for the equilibration step")
    p.add_argument("--n_crossings", type=int, default=500, help="stage-0 crossings to collect")
    p.add_argument("--n_trials", type=int, default=500, help="trial runs per interface")
    p.add_argument("--n_blocks", type=int, default=5, help="independent FFS repetitions")
    p.add_argument("--max_trial_steps", type=int, default=200_000)
    p.add_argument("--max_stage0_steps", type=int, default=20_000_000)
    p.add_argument("--seed", type=int, default=1)
    args = p.parse_args()

    interfaces = np.linspace(args.lam0, args.lam_B, args.n_interfaces)
    print(f"Rate k_AB with A: x <= {args.lam_A},  B: x >= {args.lam_B}")
    print(f"{len(interfaces)} interfaces: {np.round(interfaces, 3)}")

    step, U_b, ddU_b = make_integrator(args.seed - 1, args.dt, args.mass, args.gamma, args.kT, args.Eb)
    print_problem(U_b, args.lam_A, args.lam_B, interfaces)

    rates = []
    t0 = time.time()
    for b in range(args.n_blocks):
        print(f"Block {b + 1}/{args.n_blocks}")
        step, U_b, ddU_b = make_integrator(args.seed + 1000 * b, args.dt, args.mass, args.gamma, args.kT, args.Eb)
        U = U_b or U
        ddU = ddU_b or ddU
        rng = np.random.default_rng(args.seed + 1000 * b + 1)
        flux, probs, k = run_ffs(
            step, interfaces, args.lam_A, args.n_crossings, args.n_trials, args.dt, rng,
            equil_steps=int(args.t_equil / args.dt), max_trial_steps=args.max_trial_steps,
            max_stage0_steps=args.max_stage0_steps)
        print(f"  -> k_AB = {k:.4g}")
        rates.append(k)

    rates = np.array(rates)
    mean = rates.mean()
    sem = rates.std(ddof=1) / np.sqrt(len(rates)) if len(rates) > 1 else float("nan")
    print("\n================ FFS result ================")
    print(f"k_AB = {mean:.4g} +/- {sem:.2g}   (mean +/- s.e.m. over {len(rates)} blocks)")
    print(f"Wall time: {time.time() - t0:.1f} s")
    if U is not None and ddU is not None:
        print(f"Kramers estimate (high-barrier limit): {kramers_rate(U, ddU, args.kT, args.gamma):.4g}")


if __name__ == "__main__":
    main()
