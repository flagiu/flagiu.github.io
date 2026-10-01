import numpy as np
#import matplotlib.pyplot as plt
import scipy.integrate as intg
#from matplotlib.animation import FuncAnimation

class LogisticMap:
    def __init__(self):
        return

    # Initial conditions, n cases with equally spaced initial positions
    def set_initial_condition(self,
        lam,      # parameter
        n,        # Number of replica
        x0,       # Initial condition
        diff,     # Maximum deviation of initial conditions (%)
    ):
        self.lam = lam
        self.n = n
        factors = np.linspace(1 - diff/100, 1 + diff/100, n)
        initial_cond = x0 * factors
        # arrays of the trajectory (t,y(t)) with t0=0
        self.ts = np.array([0])
        initial_f = self.f(self.ts[0],initial_cond)
        self.ys = initial_cond[:,None]
        self.fs = initial_f[:,None]
        return

    def f(self, t, yy):
        """
        y_t+1 = f(t, y_t)
        yy = [x_1,...,x_d] (or a (d,n) array flattened to d x n)
        """
        return self.lam * yy * (1-yy)
    
    def J(self, t, yy):
            """
            Jacobian df/dy
            """
            return self.lam * (1 - 2*yy)

    def get_initial_condition(self):
        return self.ys[:,0], self.fs[:,0]

    def get_last_state(self):
        return self.ys[:,-1], self.fs[:,-1]

    def get_trajectory(self):
        return self.ys, self.fs
    
    def get_trajectory_unfolded(self):
        # 1D: already in the shape (samples,time)
        return self.get_trajectory()

    def integrate(self, dt_eval, T):
        # dt_eval and T must be integer: this is a discrete-time system
        numt = int(T/dt_eval)
        t_eval = np.empty(numt)
        y_eval = np.empty((self.n,numt))
        f_eval = np.empty((self.n,numt))
        # starting t, y, f(t,y(t))
        t = self.ts[-1]
        y, f = self.get_last_state()
        for i in range(T):
            # next t, y, f(t,y(t))
            t = t+1
            y = f
            f = self.f(t, y)
            if (i+1)%dt_eval == 0:
                t_eval[i] = t
                y_eval[:,i] = y
                f_eval[:,i] = f
        self.ts = np.concatenate([self.ts,t_eval])
        self.ys = np.concatenate([self.ys,y_eval], axis=-1)
        self.fs = np.concatenate([self.fs,f_eval], axis=-1)
        return

    def isolate_orbits_1sample(self, epsilon=0.01, t_window=10):
        orbits = [self.ys[:,-1]]
        def distance(y1,y2): # L2 distance
            return np.sqrt(np.sum((y1-y2)*(y1-y2)))
        i = 2
        while i < t_window:
            y = self.ys[:,-i]
            recurred = False
            for y_ in orbits:
                if distance(y,y_)<epsilon:
                    recurred = True
            if recurred:
                orbits.append(y)
            i = i + 1
        # output shape: (num_recurred_points, dimension*samples)
        return np.array(orbits)

    def isolate_orbits_amongsamples(self, epsilon=0.01, t_window=10):
        # flatten the trajectory and take the last t_window points:
        #   (we treat all samples as independent points)
        stationary_data = self.ys[:,-t_window:].reshape(-1)
        orbits = [stationary_data[-1]]
        def distance(y1,y2): # L2 distance
            return np.sqrt(np.sum((y1-y2)*(y1-y2)))
        # run all stationary data in reverse, starting from 2nd-to-last
        for y in stationary_data[:-1]:
            recurred = False
            for y_ in orbits:
                if distance(y,y_)<epsilon:
                    recurred = True
                    break
            if not recurred:
                orbits.append(y)
        # output shape: (num_recurred_points,)
        return np.array(orbits)

    def get_lyapunov_exponents(self):
        ts = self.ts
        ys = self.ys
        """
        lim_{t\to\infty} \frac{1}{t} \Sum_{i=0}^{t-1} ln|J(x_i)|
        """
        lyexp = np.mean(np.log(np.abs(self.J(ts,ys))), axis=-1)
        return lyexp # shape: (samples,)
    
    def run(self, lam, n, x0, diff, dt_eval, T):
        self.set_initial_condition(lam, n, x0, diff)
        self.integrate(dt_eval, T)
        ys, ymaps = self.get_trajectory_unfolded()
        orbits = self.isolate_orbits_amongsamples()
        lyexp = self.get_lyapunov_exponents()
        return self.ts, ys, ymaps, orbits, lyexp

system = LogisticMap()
