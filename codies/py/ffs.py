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
            J : a (d*n,d*n) or (d*n,d*n,T) array
        """
        Jshape = (self.d*self.n, self.d*self.n)
        if len(yy.shape)==2:
            Jshape = (self.d*self.n, self.d*self.n, len(t))
        return np.zeros(Jshape, dtype=yy.dtype)

    def J_flattened(self, t, yy):
        """
        Output:
            J : a flattened (d*d*n) or (d*d*n,T) array
        """
        Jshape = (self.d*self.d*self.n,)
        if len(yy.shape)==2:
            Jshape = (self.d*self.d*self.n,len(t))
        return np.zeros(Jshape, dtype=yy.dtype)

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
        self.Js = self.J_flattened(self.ts[0], initial_cond)[:,None]
        return

    def get_initial_condition(self):
        return self.ts[0],self.ys[:,0],self.fs[:,0],self.Js[:,0]

    def get_last_state(self):
        return self.ts[-1],self.ys[:,-1],self.fs[:,-1],self.Js[:,-1]

    def get_trajectory(self):
        return self.ts,self.ys,self.fs,self.Js

    def integrate(self, dt_eval, integration_time, rtol=1e-5, method='RK45'):
        # yy must have shape d*n
        t0,y0,f0,J0 = self.get_last_state()
        t_eval = t0 + np.arange(dt_eval, integration_time+dt_eval/2, dt_eval)
        sol = intg.solve_ivp(self.f, (t_eval[0], t_eval[-1]), y0,
                             t_eval=t_eval, rtol=rtol, method=method,
                             jac=self.J)
        self.ts = np.concatenate([self.ts,sol.t])
        self.ys = np.concatenate([self.ys,sol.y], axis=-1)
        self.fs = np.concatenate([self.fs,self.f(sol.t,sol.y)], axis=-1)
        self.Js = np.concatenate([self.Js,self.J_flattened(sol.t,sol.y)], axis=-1)
        return


class DoubleWell(DynamicSystem):
    # x,v : position and velocity variables
    # U: potential energy
    # gamma, T: friction and temperature
    def set_params(self, mass = 1, a = 1, b = 1, c = 1, gamma=0, T=1):
        ### Input parameters
        self.params = (mass, a, b, c, gamma, T)
        return

    def __init__(self, mass = 1, a = 1, b = 1, c = 1, gamma=0, T=1):
        ### Input parameters
        params = (mass, a, b, c, gamma, T)
        self.set_params(*params)
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
        m, a, b, c, gamma, T = self.params
        unfold_dimension_shape=(self.d,self.n)
        if len(yy.shape)==2:
            unfold_dimension_shape=(self.d,self.n,len(t))
        q,p = yy.reshape(*unfold_dimension_shape)
        dwdt = np.random.randn(*p.shape) # Wiener noise divided by dt?
        f_ran = np.sqrt(2*gamma*T)/m * dwdt
        fq = p/m
        fp = -(a*q + b*q**2 + c*q**3) - gamma*p/m + f_ran
        return np.array([fq,fp]).reshape(yy.shape)

    
    def J_single(self, q, p):
        m, a, b, c, gamma, T = self.params
        ones = np.ones_like(q)
        Jqq,Jqp = 0*ones, -(a + 2*b*q + 3*c*q**2)
        Jpq,Jpp =   ones, -gamma/m*ones
        return Jqq,Jqp,Jpq,Jpp

    def J(self, t, yy):
        """
        Jacobian of f(t,y(t)): df_i/dy_j
        Input: same of f
        Output:
            J : a (d*n,d*n) or (d*n,d*n,t) array
        """
        unfold_dimension_shape=(self.d,self.n)
        Jshape = (self.d*self.n,self.d*self.n)
        if len(yy.shape)==2:
            unfold_dimension_shape=(self.d,self.n,len(t))
            Jshape = (self.d*self.n,self.d*self.n,yy.shape[1])
        qp = yy.reshape(*unfold_dimension_shape)
        outJ = np.empty(Jshape, dtype=qp.dtype)
        for i in range(self.n):
            q = qp[0,i]
            for j in range(self.n):
                p = qp[1,j]
                Jqq,Jqp,Jpq,Jpp = self.J_single(q,p)
                outJ[self.d*i+0, self.d*i+0] = Jqq
                outJ[self.d*i+0, self.d*j+1] = Jqp
                outJ[self.d*j+1, self.d*i+0] = Jpq
                outJ[self.d*j+1, self.d*i+1] = Jpp
        return outJ
    
    def J_flattened(self, t, yy):
        """
        Output:
            J : a flattened (d,d,n) or (d*d*n,t) array
        """
        unfold_dimension_shape=(self.d,self.n)
        Jshape = (self.d*self.d*self.n,)
        if len(yy.shape)==2:
            unfold_dimension_shape=(self.d,self.n,len(t))
            Jshape = (self.d*self.d*self.n,yy.shape[1])
        q,p = yy.reshape(*unfold_dimension_shape)
        Jqq,Jqp,Jpq,Jpp = self.J_single(q,p) # each (n,) or (n,t)
        outJ = np.array([[Jqq,Jqp],
                         [Jpq,Jpp]]) # (d,d,n,) or (d,d,n,t)
        return outJ.reshape(Jshape) # (d*d*n,) or (d*d*n,t)

    def PotEng_fun(self, q):
        m, a, b, c, gamma, T = self.params
        return a/2*q**2 + b/3*q**3 + c/4*q**4
    
    def PotEng(self, t, yy):
        """
        Scalar Potential Energy such that fp = -dU/dq
        Input:
            t  : a number or a 1d-array (T,)
            yy : a (d,) or (d*n,) or (d*n,T) array
        Output:
            dyy : same shape of yy
        """
        unfold_dimension_shape=(self.d,self.n)
        if len(yy.shape)==2:
            unfold_dimension_shape=(self.d,self.n,len(t))
        q,p = yy.reshape(*unfold_dimension_shape)
        U = self.PotEng_fun(q)
        return np.array(U).reshape(unfold_dimension_shape[1:])

    def KinEng_fun(self, p):
        m, a, b, c, gamma, T = self.params
        return p**2/(2*m)
    
    def KinEng(self, t, yy):
        """
        Scalar Kinetic Energy such that fq = dK/dp
        Input:
            t  : a number or a 1d-array (T,)
            yy : a (d,) or (d*n,) or (d*n,T) array
        Output:
            dyy : same shape of yy
        """
        unfold_dimension_shape=(self.d,self.n)
        if len(yy.shape)==2:
            unfold_dimension_shape=(self.d,self.n,len(t))
        q,p = yy.reshape(*unfold_dimension_shape)
        K = self.KinEng_fun(p)
        return np.array(K).reshape(unfold_dimension_shape[1:])

    def Hamiltonian(self, t, yy):
        return self.KinEng(t,yy) + self.PotEng(t,yy)
    
    def get_trajectory_unfolded(self):
        x,v = self.ys.reshape(self.d,self.n,len(self.ts))
        # return (samples,times) arrays
        return x,v

    def integrate(self, dt_eval, integration_time, rtol=1e-5, method='RK45'):
        # normalize temperature to dt
        # (a dirty fix for Wiener noise integration)
        other_params = self.params[:-1]
        T = self.params[-1]
        self.params = (*other_params, T/dt_eval)
        super().integrate(dt_eval, integration_time, rtol, method)
        # reset back the temperature, after integration
        self.params = (*other_params, T)

#######################################################
#######################################################

system = DoubleWell(
    mass = 1,
    a = -1, b = 0, c = 1,
    #a = 1, b = 0, c = 0,
    gamma = 0, # friction coeff
    T = 0.1      # temperature
)
system.set_initial_condition(
    [-1.5,0],
    n=5, diff=1e-3
)
system.integrate(
    0.01, 10,
    rtol=1e-4,
    method='RK45' # 'RK45', 'Radau'
)

#plot the trajectory as animation
frames_per_second = 20  # Frames per second of the animation
t_real = 10 #ts[-1]  # Actual total time of the integration (seconds)

#######################################################
#######################################################

n = system.n
ts,ys,fs,Js = system.get_trajectory()
N = len(ts)

Ks = system.KinEng(ts, ys)
Us = system.PotEng(ts, ys)
Hs = Ks + Us

qs,ps = ys.reshape(2,n,N)
fqs,fps = fs.reshape(2,n,N)
Js = Js.reshape(2,2,n,N)

fig,axes = plt.subplots(2,4, figsize=(16,8))
ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8 = axes.ravel()
lns = []
cols = plt.cm.jet(np.linspace(0, 1, n))
for i in range(n):
    for ax in axes.ravel():
        lns.append(ax.plot([], [], "-", color=cols[i])[0])

def init():
    global system, ts,qs,ps,Ks,Us,Hs, ax1,ax2,ax3,ax4,ax5,ax6,ax7,ax8, lns
    tlim=(ts.reshape(-1).min(),ts.reshape(-1).max())
    qlim=(qs.reshape(-1).min(),qs.reshape(-1).max())
    plim=(ps.reshape(-1).min(),ps.reshape(-1).max())
    Ulim = (Us.reshape(-1).min(),Us.reshape(-1).max())
    Klim = (Ks.reshape(-1).min(),Ks.reshape(-1).max())
    Hlim = (Hs.reshape(-1).min(),Hs.reshape(-1).max())
    T=system.params[-1]
    ql = np.linspace(*qlim, 100)
    Ul = system.PotEng_fun(ql)
    ax1.set(xlim=qlim, ylim=Ulim)
    ax1.set(xlabel=r"Position $q$", ylabel=r"Potential energy $U(q)$")
    ax1.plot(ql, Ul, 'k--', zorder=-1, lw=2)
    #
    ax2.set(xlim=tlim, ylim=qlim)
    ax2.set(xlabel=r"Time $t$", ylabel=r"Position $q$")
    #
    ax3.set(xlim=tlim, ylim=Ulim)
    ax3.set(xlabel=r"Time $t$", ylabel=r"Potential energy $U(q)$")
    ax3.axhline(T/2, color='k', ls='--', label='equipartition')
    #
    ax4.set(xlim=qlim, ylim=plim)
    ax4.set(xlabel=r"Position $q$", ylabel=r"Momentum $p$")
    #
    pl = np.linspace(*plim, 100)
    Kl = system.KinEng_fun(pl)
    ax5.set(xlim=plim, ylim=Klim)
    ax5.set(xlabel=r"Momentum $p$", ylabel=r"Kinetic energy $K(p)$")
    ax5.plot(pl, Kl, 'k--', zorder=-1, lw=2)
    #
    ax6.set(xlim=tlim, ylim=plim)
    ax6.set(xlabel=r"Time $t$", ylabel=r"Momentum $p$")
    #
    ax7.set(xlim=tlim, ylim=Klim)
    ax7.set(xlabel=r"Time $t$", ylabel=r"Kinetic energy $K(p)$")
    ax7.axhline(T/2, color='k', ls='--', label='equipartition')
    #
    ax8.set(xlim=tlim, ylim=Hlim)
    ax8.set(xlabel=r"Time $t$", ylabel=r"Hamilton function $H(q,p)$")
    ax8.axhline(T, color='k', ls='--', label='equipartition')
    return lns

def update(ct):
    global axes, ts,qs,ps,Us,Ks
    nplots=len(axes.ravel())
    for i in range(n):
        lns[i*nplots+0].set_data(qs[i, :ct], Us[i, :ct])
        lns[i*nplots+1].set_data(ts[:ct], qs[i, :ct])
        lns[i*nplots+2].set_data(ts[:ct], Us[i, :ct])
        lns[i*nplots+3].set_data(qs[i, :ct], ps[i, :ct])
        lns[i*nplots+4].set_data(ps[i, :ct], Ks[i, :ct])
        lns[i*nplots+5].set_data(ts[:ct], ps[i, :ct])
        lns[i*nplots+6].set_data(ts[:ct], Ks[i, :ct])
        lns[i*nplots+7].set_data(ts[:ct], Hs[i, :ct])
    return lns

ani = FuncAnimation(
    fig,
    update,
    frames=np.arange(0, N, N // (frames_per_second * t_real), dtype=np.int32),
    init_func=init,
    blit=True,
    interval=1000 / frames_per_second,
)

plt.show()
# ani.save(f"images/thomas_b{system.b:.5f}.gif")
