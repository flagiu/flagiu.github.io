import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate as intg
from matplotlib.animation import FuncAnimation

class DynamicSystem:
    def __init__():
        return

    def f(self, t, yy):
        """
        Derivative dy/dt = f(t,y(t))
        Input:
            t  : a number or a 1d-array (T,)
            yy : a (d,) or (d*n,) or (d*n,T) array
        Output:
            dyy : same shape of yy
        """
        return np.zeros_like(yy)

    def J(self, t, yy):
        """
        Jacobian of f(t,y(t)): df_i/dy_j
        Input: same of f
        Output:
            J : a flattened (d,d) or flattened (d,d,n) or a (d*d*n,T) array
        """
        Jshape = (yy.shape[0]*self.d,)
        if len(yy.shape)==2:
            Jshape = (yy.shape[0]*self.d,yy.shape[1])
        return np.zeros(Jshape)

    # Initial conditions, n cases with equally spaced initial positions
    def set_initial_condition(self,
        y0,
        n = 5,        # Number of replica
        diff = 1e-3,  # Maximum deviation of initial conditions
        
    ):
        self.n = n
        factors = np.linspace(1 - diff, 1 + diff, n)
        try:
            self.d = len(y0)
            y0 = np.array(y0)
        except TypeError:
            self.d = 1
            y0 = np.array([y0])
        initial_cond = (y0[:,None] * factors[None,:]).reshape(-1) # shape d*n
        # arrays of the trajectory (t,y(t)) with t0=0
        self.ts = np.array([0])
        self.ys = initial_cond[:,None]
        self.fs = self.f(self.ts[0], initial_cond)[:,None]
        self.Js = self.J(self.ts[0], initial_cond)[:,None]
        return

    def get_initial_condition(self):
        return self.ts[0],self.ys[:,0],self.fs[:,0],self.Js[:,0]

    def get_last_state(self):
        return self.ts[-1],self.ys[:,-1],self.fs[:,-1],self.Js[:,-1]

    def get_trajectory(self):
        return self.ts,self.ys,self.fs,self.Js

    def integrate(self, dt_eval, T, rtol=1e-5):
        # yy must have shape d*n
        t0,y0,f0,J0 = self.get_last_state()
        t_eval = t0 + np.arange(dt_eval, T+dt_eval/2, dt_eval)
        sol = intg.solve_ivp(self.f, (t_eval[0], t_eval[-1]), y0,
                             t_eval=t_eval, rtol=rtol, jac=self.J)
        self.ts = np.concatenate([self.ts,sol.t])
        self.ys = np.concatenate([self.ys,sol.y], axis=-1)
        self.fs = np.concatenate([self.fs,self.f(sol.t,sol.y)], axis=-1)
        self.Js = np.concatenate([self.Js,self.J(sol.t,sol.y)], axis=-1)
        return


class Lorenz(DynamicSystem):
    """
    The famous Lorenz system having a strange attractor
    https://en.wikipedia.org/wiki/Lorenz_system
    """
    def set_params(self, sigma = 10, b = 8 / 3, r = 28):
        ### Input parameters
        self.sigma = sigma
        self.b = b
        self.r = r
        return

    def f(self, t, yy):
        """
        Derivative dy/dt = f(t,y(t))
        Input:
            t  : a number or a 1d-array (T,)
            yy : a (d,) or (d*n,) or (d*n,T) array
        Output:
            dyy : same shape of yy
        """
        sigma, b, r = self.sigma, self.b, self.r
        unfold_dimension_shape=(self.d,self.n)
        if len(yy.shape)==2:
            unfold_dimension_shape=(self.d,self.n,len(t))
        x,y,z = yy.reshape(*unfold_dimension_shape)
        fx = sigma * (y - x)
        fy = x * (r - z) - y
        fz = x * y - b * z
        return np.array([fx,fy,fz]).reshape(yy.shape)

    def J(self, t, yy):
        """
        Jacobian of f(t,y(t)): df_i/dy_j
        Input: same of f
        Output:
            J : a flattened (d,d) or flattened (d,d,n) or a (d*d*n,T) array
        """
        sigma, b, r = self.sigma, self.b, self.r
        unfold_dimension_shape=(self.d,self.n)
        Jshape = (yy.shape[0]*self.d,)
        if len(yy.shape)==2:
            unfold_dimension_shape=(self.d,self.n,len(t))
            Jshape = (yy.shape[0]*self.d,yy.shape[1])
        x,y,z = yy.reshape(*unfold_dimension_shape)
        ones = np.ones_like(x)
        Jxx = -sigma*ones
        Jxy = sigma*ones
        Jxz = 0*ones
        Jyx = r-z
        Jyy = -1*ones
        Jyz = -x
        Jzx = y
        Jzy = x
        Jzz = -b*ones
        return np.array([[Jxx,Jxy,Jxz],
                         [Jyx,Jyy,Jyz],
                         [Jzx,Jzy,Jzz]]).reshape(Jshape)
    
    def __init__(self, sigma = 10, b = 8 / 3, r = 28):
        ### Input parameters
        self.set_params(sigma=sigma, b=b, r=r)
        return

    def get_trajectory_unfolded(self):
        x,y,z = self.ys.reshape(3,self.n,len(self.ts))
        # return (samples,times) arrays
        return x,y,z


class Thomas(DynamicSystem):
    """
    A system proposed by René Thomas, having a strange attractor
    https://en.wikipedia.org/wiki/Thomas'_cyclically_symmetric_attractor
    see also: "LABYRINTH CHAOS", by J. C. SPROTT and KONSTANTINOS E. CHLOUVERAKIS
    https://doi.org/10.1142/S0218127407018245
    """
    def set_params(self, b = 1):
        ### Input parameters
        self.b = b
        return

    def f(self, t, yy):
        """
        Derivative dy/dt = f(t,y(t))
        Input:
            t  : a number or a 1d-array (T,)
            yy : a (d,) or (d*n,) or (d*n,T) array
        Output:
            dyy : same shape of yy
        """
        b = self.b
        unfold_dimension_shape=(self.d,self.n)
        if len(yy.shape)==2:
            unfold_dimension_shape=(self.d,self.n,len(t))
        x,y,z = yy.reshape(*unfold_dimension_shape)
        fx = np.sin(y) - b*x
        fy = np.sin(z) - b*y
        fz = np.sin(x) - b*z
        return np.array([fx,fy,fz]).reshape(yy.shape)

    def J(self, t, yy):
        """
        Jacobian of f(t,y(t)): df_i/dy_j
        Input: same of f
        Output:
            J : a flattened (d,d) or flattened (d,d,n) or a (d*d*n,T) array
        """
        b = self.b
        unfold_dimension_shape=(self.d,self.n)
        Jshape = (yy.shape[0]*self.d,)
        if len(yy.shape)==2:
            unfold_dimension_shape=(self.d,self.n,len(t))
            Jshape = (yy.shape[0]*self.d,yy.shape[1])
        x,y,z = yy.reshape(*unfold_dimension_shape)
        ones = np.ones_like(x)
        Jxx,Jxy,Jxz = -b*ones, np.cos(y), 0*ones
        Jyx,Jyy,Jyz = 0*ones, -b*ones, np.cos(z)
        Jzx,Jzy,Jzz = np.cos(x), 0*ones, -b*ones
        return np.array([[Jxx,Jxy,Jxz],
                         [Jyx,Jyy,Jyz],
                         [Jzx,Jzy,Jzz]]).reshape(Jshape)
    
    def __init__(self, b = 8):
        ### Input parameters
        self.set_params(b=b)
        return

    def get_trajectory_unfolded(self):
        x,y,z = self.ys.reshape(3,self.n,len(self.ts))
        # return (samples,times) arrays
        return x,y,z


#system = Lorenz()
#system.set_initial_condition([10,10,20])
#system.integrate(0.01, 100)

system = Thomas(b=0.05)
system.set_initial_condition([1,0,-1])
system.integrate(0.01, 500)

n = system.n
ts,ys,fs,Js = system.get_trajectory()
N = len(ts)
ys = ys.reshape(3,n,N)
fs = fs.reshape(3,n,N)
Js = Js.reshape(3,3,n,N)

#plot the 3d trajectory as animation
fps = 20  # Frames per second of the animation
t_real = 10 #ts[-1]  # Actual total time of the integration (seconds)

fig = plt.figure()
ax = plt.axes(projection="3d")
lns = []
cols = plt.cm.jet(np.linspace(0, 1, n))
for i in range(n):
    lns.append(ax.plot3D([], [], [], "-", color=cols[i])[0])

def init():
    xlim=(ys[0].reshape(-1).min(),ys[0].reshape(-1).max())
    ylim=(ys[1].reshape(-1).min(),ys[1].reshape(-1).max())
    zlim=(ys[2].reshape(-1).min(),ys[2].reshape(-1).max())
    ax.set(xlim=xlim, ylim=ylim, zlim=zlim)
    ax.set(xlabel=r"$x$", ylabel=r"$y$", zlabel=r"$z$")
    return lns

def update(ct):
    for i in range(n):
        lns[i].set_data(ys[0, i, :ct], ys[1, i, :ct])
        lns[i].set_3d_properties(ys[2, i, :ct])
    return lns

ani = FuncAnimation(
    fig,
    update,
    frames=np.arange(0, N, N // (fps * t_real), dtype=np.int32),
    init_func=init,
    blit=True,
    interval=1000 / fps,
)

plt.show()
# ani.save(f"images/thomas_b{system.b:.5f}.gif")
