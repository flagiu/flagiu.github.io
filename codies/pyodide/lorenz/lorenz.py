import numpy as np
#import matplotlib.pyplot as plt
import scipy.integrate as intg
#from matplotlib.animation import FuncAnimation

class Lorenz:
    def __init__(self, sigma = 10, b = 8 / 3, r = 28):
        ### Input parameters
        self.sigma = sigma
        self.b = b
        self.r = r
        return

    # Initial conditions, n cases with equally spaced initial positions
    def set_initial_condition(self,
        n,        # Number of replica
        diff = 1e-3,  # Maximum deviation of initial conditions
        x0 = 10,
        y0 = 10,
        z0 = 20
    ):
        self.n = n
        factors = np.linspace(1 - diff, 1 + diff, n)
        X0s = x0 * np.ones(n)
        Y0s = y0 * np.ones(n)
        Z0s = z0 * factors # variability only along z
        initial_cond = np.array([X0s, Y0s, Z0s]).reshape(-1) # shape 3*n
        # arrays of the trajectory (t,y(t)) with t0=0
        self.ys = initial_cond[:,None]
        self.ts = np.array([0])
        return

    def get_initial_condition(self):
        return self.y0

    def get_last_state(self):
        return self.ys[:,-1]

    def get_trajectory(self):
        return self.ys
    
    def get_trajectory_unfolded(self):
        x,y,z = self.ys.reshape(3,self.n,len(self.ts))
        # return (samples,times) arrays
        return x,y,z

    def integrate(self, dt_eval, T, rtol=1e-5):
        # yy must have shape 3 x n
        t_eval = self.ts[-1] + np.arange(dt_eval, T+dt_eval/2, dt_eval)
        #ys = np.zeros((3*n, N))
        y0 = self.get_last_state()
        ###
        def derivative(t, yy):
            """
            Derivative
            yy = [x,y,z] (or a (3,n) array flattened to 3 x n)
            dyy = [dx/dt,dy/dt,dz/dt]
            params = (sigma,r,beta)
            """
            sigma, b, r = self.sigma, self.b, self.r
            Y = yy.reshape(3,-1)
            dY = np.empty_like(Y)
            x,y,z = Y
            dY[0] = sigma * (y - x)
            dY[1] = x * (r - z) - y
            dY[2] = x * y - b * z
            return dY.reshape(-1)
        ###
        sol = intg.solve_ivp(derivative, (t_eval[0], t_eval[-1]),
                             y0, t_eval=t_eval, rtol=rtol)
        #for i in range(n):
        #    y0 = [X0s[i], Y0s[i], Z0s[i]]
        #    sol = intg.solve_ivp(lorenz_der, (t[0], t[-1]), y0, t_eval=t, rtol=rtol)
        #    ys[i, :, :] = sol.y
        self.ts = np.concatenate([self.ts,sol.t])
        self.ys = np.concatenate([self.ys,sol.y], axis=-1)
        return
    
    def run(self, n, dt_eval, T):
        self.set_initial_condition(n)
        self.integrate(dt_eval, T)
        return self.get_trajectory_unfolded()

lorenz = Lorenz()
#lorenz.set_initial_condition()
#lorenz.integrate()

"""
n = ys.shape[0]//3
ys = ys.reshape(3,n,-1)

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
"""