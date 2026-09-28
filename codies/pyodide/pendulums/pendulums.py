import numpy as np
import scipy.integrate as intg


def simulate_double_pendulum(m1=1, m2=1, l1=1, l2=1, phi0=np.pi, T=10):
    g = 10  # Gravitational acceleration
    n = 50  # Number of pendulums

    def der(t, y):
        return np.array(
            [
                (l2 * y[2] - l1 * y[3] * np.cos(y[0] - y[1]))
                / (l1**2 * l2 * (m1 + m2 * np.sin(y[0] - y[1]) ** 2)),
                (l1 * (m1 + m2) * y[3] - l2 * m2 * y[2] * np.cos(y[0] - y[1]))
                / (l1 * l2**2 * (m1 + m2 * np.sin(y[0] - y[1]) ** 2)),
                -(m1 + m2) * g * l1 * np.sin(y[0])
                - (y[2] * y[3] * np.sin(y[0] - y[1]))
                / (l1 * l2 * (m1 + m2 * np.sin(y[0] - y[1]) ** 2))
                + (
                    l2**2 * m2 * y[2] ** 2
                    + l1**2 * (m1 + m2) * y[3] ** 2
                    - l1 * l2 * m2 * y[2] * y[3] * np.cos(y[0] - y[1])
                )
                / (2 * l1**2 * l2**2 * (m1 + m2 * np.sin(y[0] - y[1]) ** 2) ** 2)
                * np.sin(2 * (y[0] - y[1])),
                -m2 * g * l2 * np.sin(y[1])
                + (y[2] * y[3] * np.sin(y[0] - y[1]))
                / (l1 * l2 * (m1 + m2 * np.sin(y[1] - y[2]) ** 2))
                - (
                    l2**2 * m2 * y[2] ** 2
                    + l1**2 * (m1 + m2) * y[3] ** 2
                    - l1 * l2 * m2 * y[2] * y[3] * np.cos(y[0] - y[1])
                )
                / (2 * l1**2 * l2**2 * (m1 + m2 * np.sin(y[0] - y[1]) ** 2) ** 2)
                * np.sin(2 * (y[0] - y[1])),
            ]
        )

    # Initial conditions, n pendulums with equally spaced initial positions
    diff = 1e-3  # Maximum deviation of initial conditions
    factors = np.linspace(1 - diff, 1 + diff, n)
    phi0s = phi0 / 2 * factors
    phi1s = phi0 / 2 * factors
    dphi0s = [0] * n
    dphi1s = [0] * n

    #T = 10  # Integration time
    dt = 0.01 # Integration time step
    N = int(T/dt) #1000  # Number of discretization points
    rtol = 1e-5  # Relative tolerance of the integrator

    t = np.linspace(0, T, N)

    ys = np.zeros((n, 4, N))
    for i in range(n):
        y0 = [
            phi0s[i],
            phi1s[i],
            (m1 + m2) * l1**2 * dphi0s[i]
            + m2 * l1 * l2 * dphi1s[i] * np.cos(phi0s[i] - phi1s[i]),
            m2 * l2**2 * dphi1s[i]
            + m2 * l1 * l2 * dphi0s[i] * np.cos(phi0s[i] - phi1s[i]),
        ]
        sol = intg.solve_ivp(der, (t[0], t[-1]), y0, t_eval=t, rtol=rtol)
        ys[i, :, :] = sol.y

    x1 = l1 * np.sin(ys[:, 0, :]).T
    y1 = -l1 * np.cos(ys[:, 0, :]).T
    x2 = l1 * np.sin(ys[:, 0, :]).T + l2 * np.sin(ys[:, 1, :]).T
    y2 = -l1 * np.cos(ys[:, 0, :]).T - l2 * np.cos(ys[:, 1, :]).T

    return x1, y1, x2, y2


# TODO: if running in python
### Input parameters
# m1 = 1  # Masses of the weights
# m2 = 1
# l1 = 1  # Length of the rods
# l2 = 1
# g = 10  # Gravitational acceleration

# n = 50  # Number of pendulums

# # Initial conditions, n pendulums with equally spaced initial positions
# diff = 1e-3  # Maximum deviation of initial conditions
# factors = np.linspace(1 - diff, 1 + diff, n)
# phi0s = np.pi / 2 * factors
# phi1s = np.pi / 2 * factors
# dphi0s = [0] * n
# dphi1s = [0] * n

# T = 10  # Integration time
# N = 1000  # Number of discretization points
# rtol = 1e-5  # Relative tolerance of the integrator

# t = np.linspace(0, T, N)

# ys = np.zeros((n, 4, N))
# for i in range(n):
#     y0 = [
#         phi0s[i],
#         phi1s[i],
#         (m1 + m2) * l1**2 * dphi0s[i]
#         + m2 * l1 * l2 * dphi1s[i] * np.cos(phi0s[i] - phi1s[i]),
#         m2 * l2**2 * dphi1s[i] + m2 * l1 * l2 * dphi0s[i] * np.cos(phi0s[i] - phi1s[i]),
#     ]
#     sol = intg.solve_ivp(der, (t[0], t[-1]), y0, t_eval=t, rtol=rtol)
#     ys[i, :, :] = sol.y

# x1 = l1 * np.sin(ys[:, 0, :]).T
# y1 = -l1 * np.cos(ys[:, 0, :]).T
# x2 = l1 * np.sin(ys[:, 0, :]).T + l2 * np.sin(ys[:, 1, :]).T
# y2 = -l1 * np.cos(ys[:, 0, :]).T - l2 * np.cos(ys[:, 1, :]).T
