"""
https://en.wikipedia.org/wiki/Lyapunov_fractal
"""
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

class DiscreteMap:
    def __init__(self):
        return

    def set_params(self, params):
        self.params = params

    # Initial conditions, n cases with equally spaced initial positions
    def set_initial_condition(self,
        params,   # parameters
        x0,       # Initial condition (number or d-dimensional array)
        n,        # Number of replica in each dimension (integer)
        diff,     # Maximum deviation of initial conditions (% in each dimension)
    ):
        self.set_params(params)
        self.n = int(n)
        if not hasattr(x0,"len"):
            x0 = np.array([x0])
        self.d = len(x0)
        factors = np.linspace(1 - diff/100, 1 + diff/100, n)
        initial_cond = (x0[:,None] * factors[None,:]).reshape(-1) # (d dimension X n replica)
        # arrays of the trajectory (t,y(t)) with t0=0
        self.ts = np.array([0]) # 1d array
        initial_f = self.f(self.ts[0], initial_cond)
        initial_J = self.J(self.ts[0], initial_cond)
        self.ys = initial_cond[:,None] # (d dimension X n replica, time)
        self.fs = initial_f[:,None]    # (d dimension X n replica, time)
        self.Js = initial_J[:,None]    # (d dimension X d dimension X n replica, time)
        return

    # Foo identity map
    """
     t : a number or a (times,) array
    yy : a (dimension X samples,) or (dimension X samples, times)
    Output:
    y_t+1 = f(t, y_t) , with same dimension of yy
    """
    def f(self, t, yy):
        return yy
    
    # its Jacobian
    def J(self, t, yy):
        if not hasattr(t,"len"):
            if self.d == 1 and self.n == 1:
                return 1
            else:
                return np.ones((self.d*self.n, self.d*self.n))
        else:
            if self.d == 1 and self.n == 1:
                return np.ones(1,len(t))
            else:
                return np.ones((self.d*self.n, self.d*self.n, len(t)))
               

    def get_initial_condition(self): # (dimension X samples,) each
        return self.ys[:,0], self.fs[:,0]

    def get_last_state(self): # (dimension X samples,) each
        return self.ys[:,-1], self.fs[:,-1]

    def get_trajectory(self): # (dimension X samples, time) each
        return self.ys, self.fs
    
    def get_trajectory_unfolded(self): #unfold (dimension, samples, time)
        return self.ys.reshape(self.d, self.n, len(self.ts)), self.fs.reshape(self.d, self.n, len(self.ts))

    def integrate(self, dt_eval, T):
        # dt_eval and T must be integer: this is a discrete-time system
        numt = int(T/dt_eval)
        t_eval = np.empty(numt)
        y_eval = np.empty((self.d*self.n,numt))
        f_eval = np.empty((self.d*self.n,numt))
        J_eval = np.empty((self.d*self.d*self.n,numt))
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
                J_eval[:,i] = self.J(t,y)
        self.ts = np.concatenate([self.ts,t_eval])
        self.ys = np.concatenate([self.ys,y_eval], axis=-1)
        self.fs = np.concatenate([self.fs,f_eval], axis=-1)
        self.Js = np.concatenate([self.Js,J_eval], axis=-1)
        return

    def isolate_orbits_amongsamples(self, epsilon=0.01, t_window=10):
        # flatten the trajectory and take the last t_window points:
        #   (we treat all samples as independent points)
        stationary_data = self.ys[:,-t_window:].reshape(self.d, self.n, t_window).reshape(self.d, self.n * t_window)
        orbits = [stationary_data.T[-1]]
        def distance(y1,y2): # L2 distance between d-dimensional arrays
            return np.sqrt(np.sum((y1-y2)*(y1-y2), axis=0))
        # run all stationary data in reverse, starting from 2nd-to-last
        for y in stationary_data.T[:-1]: #(samples * t_window, dimension)
            recurred = False
            for y_ in orbits:
                if distance(y,y_)<epsilon:
                    recurred = True
                    break
            if not recurred:
                orbits.append(y)
        # output shape: (num_recurred_points,)
        self.orbits = np.array(orbits)

    def compute_lyapunov_exponents(self, t_window=10):
        """
        lim_{t\to\infty} \frac{1}{t} \Sum_{i=0}^{t-1} ln|J(x_i)|
        """
        J = self.Js[:,-t_window:] #shape (d*d*n,times) ; take the last t_window point
        d = self.d
        if d==1:
            det = J
        else:
            J = J.reshape(d,d,self.n,-1)    #shape (d,d,n,times)
            J = np.transpose(J, (2,3,0,1))  #shape (n,times,d,d)
            det = np.linalg.det(J)          #det() acts on the last 2 dimensions (d,d) --> shape (n,times)
        # average over time axis (-1): output shape is (n samples,)
        self.lyexp = np.mean(np.log(np.abs(det)), axis=-1)
    
    def run(self, lam, x0, n, diff, dt_eval, T):
        self.set_initial_condition(lam, x0, n, diff)
        self.integrate(dt_eval, T)
        self.isolate_orbits_amongsamples()
        self.compute_lyapunov_exponents()

    def plot_1d_vs_time(self, ax, dim=0, plot_args=dict(marker='.',ls='-')):
        ys,fs = self.get_trajectory_unfolded() #unfold (dimension, samples, time)
        for k in range(self.n):
            col='C%d'%k
            ax.plot(self.ts, ys[dim,k,:], color=col, **plot_args)
    
    def plot_Cobweb(self, ax, dim=0, plot_args=dict(marker='.',ls='-')):
        ys,fs = self.get_trajectory_unfolded() #unfold (dimension, samples, time)
        for k in range(self.n):
            col='C%d'%k
            x = ys[dim,k,:]
            y = fs[dim,k,:]
            ax.axvline(x[0], ymax=y[0], color=col, **plot_args)
            x = np.insert(x, np.arange(1,len(x)+1, dtype=np.int32), y)
            y = np.repeat(y,2)
            ax.plot(x, y, color=col, **plot_args)

    def plot_2d_parametric(self, ax, dimX=0, dimY=1, plot_args=dict(marker='.',ls='-')):
        ys,fs = self.get_trajectory_unfolded() #unfold (dimension, samples, time)
        for k in range(self.n):
            col='C%d'%k
            ax.plot(ys[dimX,k,:], ys[dimY,k,:], color=col, **plot_args)

#####
class LogisticMap(DiscreteMap):
    def f(self, t, yy):
        """
        y_t+1 = f(t, y_t)
        yy = [x_1,...,x_d] (or a (d,n) array flattened to d x n)
        """
        return self.params * yy * (1-yy)
    
    def J(self, t, yy):
        """
        Jacobian df/dy
        """
        return self.params * (1 - 2*yy)

    def get_domain_boundary(self):
        return [0,1]

##############################################

Nt=4600
Nw=4000
if len(sys.argv)<5 or len(sys.argv)>7:
    print("Usage: <AB-sequence> <parameter min> <parameter max>"+
          f"<parameter resolution> [sequence length={Nt:d}] [stationary length={Nw:d}]")
    sys.exit(1)
sequenceAB=sys.argv[1]
lam0=float(sys.argv[2])
lam1=float(sys.argv[3])
Np=int(sys.argv[4])
if len(sys.argv)>5:
    Nt=int(sys.argv[5])
if len(sys.argv)>6:
    Nw=int(sys.argv[6])
print("Input:",sequenceAB,lam0,lam1,Np,Nt,Nw)
outname=f"lyapunov_fractal_logisticMap_{sequenceAB}_param{lam0}_{lam1}_Np{Np:d}_Nt{Nt:d}_Nw{Nw:d}"

assert (Nt>0 and Np>0 and lam1>lam0 and sequenceAB[0]=='A' and
        sum([el in ['A','B'] for el in sequenceAB])==len(sequenceAB))

system = LogisticMap()
init_cond=(lam0,0.501,1,0) #params, x0, n, diff
lambdas = np.linspace(lam0,lam1,Np, dtype=np.float32)

try:
    Z = np.load(f"{outname}.npy")
except:
    sequence = tuple([0 if el=='A' else 1 for el in sequenceAB])
    Z = np.empty((len(lambdas),len(lambdas)))
    for ia,a in enumerate(lambdas):
        print(f"\r[{(ia+1)/len(lambdas)*100:.1f}%]", end='', flush=(ia%10==0))
        for ib,b in enumerate(lambdas):
            system.set_initial_condition(*init_cond)
            params=(a,b)
            while system.ts[-1]<Nt:
                for s in sequence:
                    system.set_params(params[s])
                    system.integrate(dt_eval=1, T=1)
            system.compute_lyapunov_exponents(t_window=Nw)
            Z[ia,ib] = system.lyexp[0]
    print()
    np.save(f"{outname}", Z)

fig,ax = plt.subplots(figsize=(5,4), dpi=200)
zmin = np.unique(Z.reshape(-1))[0]
if zmin==-np.inf: #replace -np.inf with the minimum finite value
    zmin = np.unique(Z.reshape(-1))[1]    
    Z[Z==-np.inf] = zmin
zmax=Z.reshape(-1).max()
mid = (0 - zmin)/(zmax - zmin)
# black to green for Z<0 (0 to mid)
# white to red for Z>0 (mid to 1)
segmentdata = { # x, y0, y1
    'red':   [(0.0, 0.0, 0.0),
              (mid, 0.0, 1.0),
              (1.0, 1.0, 1.0)],
    'green': [(0.0, 0.0, 0.0),
              (mid, 1.0, 1.0),
              (1.0, 0.0, 0.0)],
    'blue':  [(0.0, 0.0, 0.0),
              (mid, 0.0, 1.0),
              (1.0, 0.0, 0.0)],
}
img = ax.imshow(Z.T, origin="lower",
                cmap=LinearSegmentedColormap("aaa", segmentdata), #cmap="bwr",vmin=-zmax, vmax=zmax,
                extent=(lambdas[0],lambdas[-1],lambdas[0],lambdas[-1]))
fig.colorbar(img, label=r"$\Lambda$", shrink=0.8)
ax.set(xlabel=r"$\lambda_a$", ylabel=r"$\lambda_b$", aspect="equal")
fig.tight_layout()
fig.savefig(f"{outname}.png")
#plt.show()

sys.exit()

lambdas = np.linspace(0,4,1000)
system.run(lambdas[0], 0.5, 10, 1, 1, 100) #a foo run
x0,x1 = system.get_domain_boundary()

fig,axes = plt.subplots(2,1, sharex=True, figsize=(4,8), dpi=200)
axBif, axLyap = axes
axBif.set(ylabel=r"$x^*$", ylim=(x0,x1), xlim=(lambdas[0],lambdas[-1]))
axLyap.set(xlabel=r"$\lambda$", ylabel=r"$\Lambda$")
axLyap.axhline(0, color='k', ls='-')

lyexp = np.empty((system.n, len(lambdas)))
orbits = []
xorbits = []
for il,lam in enumerate(lambdas):
    system.run(lam, 0.5, 10, 1, 1, 100)
    lyexp[:,il] = system.lyexp.copy()
    orbits.append( system.orbits.copy() )
    xorbits.append( lam*np.ones(len(system.orbits)) )
xorbits = np.concatenate(xorbits)
orbits = np.concatenate(orbits)

axBif.scatter(xorbits, orbits, s=1, marker='.', ec='none', fc='k')
for k in range(system.n):
    axLyap.scatter(lambdas, lyexp[k], s=1, marker='.', ec='none', fc='C%d'%k)

fig.savefig("logistic_map.png")
plt.show()

sys.exit()

fig,axes = plt.subplots(1,2, figsize=(8,4), dpi=200)
ax1d, axCobweb = axes
ax1d.set(xlabel=r"$t$", ylabel=r"$x_t$", ylim=(x0,x1))
axCobweb.set(xlabel=r"$x_{t}$",   xlim=(x0,x1),
             ylabel=r"$x_{t+1}$", ylim=(x0,x1), aspect="equal")
system.plot_1d_vs_time(ax1d)
system.plot_Cobweb(axCobweb)
# plot bisetrix
axCobweb.plot([x0,x1],[x0,x1],'k-',zorder=-1)
# plot f(x_t)
xl = np.linspace(x0,x1,100)
yl = system.f(0,xl)
axCobweb.plot(xl, yl,'k-',zorder=-1)

plt.show()
