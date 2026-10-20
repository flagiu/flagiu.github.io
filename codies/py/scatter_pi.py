"""
From 3b1b 's video on computing Pi with colliding blocks
https://www.youtube.com/watch?v=6dTyOl1fmDo
"""
import argparse
import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate as intg
from matplotlib.patches import Circle
from matplotlib.animation import FuncAnimation
import sys
import copy

class Vec():
    def __init__(self, r):
        if hasattr(r, "len"):
            self.d = len(r)
        else:
            self.d = 1
        self.r = np.array(r)

    def diff(self, other):
        return Vec(self.r.copy() - other.r.copy())
    
    def diff_inplace(self, other):
        self.r = self.r - other.r.copy()

    def sum(self, other):
        return Vec(self.r.copy() + other.r.copy())
    
    def sum_inplace(self, other):
        self.r = self.r + other.r.copy()

    def mult(self, factor):
        return Vec(self.r.copy() * factor)

    def mult_inplace(self, factor):
        self.r = self.r * factor.copy()

    def mean(self):
        return self.r.mean()

    def dot(self, other):
        return np.sum(self.r * other.r)

    def sqNorm(self):
        return np.sum(self.r * self.r)

    def norm(self):
        return np.sqrt(self.sqNorm())

    def normalize(self):
        n = self.norm()
        if n>0:
            return Vec(self.r / self.norm())
        else:
            print("Error: cannot normalize a vector with zero norm")
        return
    
    def normalize_inplace(self):
        n = self.norm()
        if n>0:
            self.r /= self.norm()
        else:
            print("Error: cannot normalize a vector with zero norm")
        return

    def print(self):
        print(self.r)

###
class Particle():
    def __init__(self, mass, position, velocity, pbc=None, color=None):
        self.m = mass
        self.r = Vec(position)
        self.v = Vec(velocity)
        self.pbc = pbc
        self.color = color

    def apply_pbc(self):
        if self.pbc is None:
            return

    def print(self):
        print(f"Mass: {self.m}")
        print(f"Position: ", end='')
        self.r.print()
        print(f"Velocity: ", end='')
        self.v.print()
        

###
class HardSphere(Particle):
    def __init__(self, mass, position, velocity, diameter):
        super().__init__(mass, position, velocity)
        self.sigma = diameter

    def print(self):
        super().print()
        print(f"Diameter: {self.sigma}")

class System():
    def __init__(self, particles, obstacles, time=0, debug=False):
        self.ps = copy.deepcopy(particles)
        self.obstacles = copy.deepcopy(obstacles)
        self.time = time
        self.N = len(self.ps)
        # debugging variables
        self.debug = debug
        # collision variables
        self.BIG_T = 1e10  # a large default collision time
        self.coll_times = None
        self.coll_partner = None
        self.coll_i = None
        self.coll_j = None

    def copy(self, coll_variables=False):
        other = System(self.ps, self.obstacles, time=self.time, debug=self.debug)
        if coll_variables:
            other.coll_times = self.coll_times.copy()
            other.coll_partner = self.coll_partner.copy()
            other.coll_i = self.coll_i.copy()
            other.coll_j = self.coll_j.copy()
        return other

    def dbprint(self, *args, **kwargs):
        if self.debug:
            print(*args, **kwargs)

    def print(self):
        if self.time==0:
            print("# Time, x_1, v_1, x_2, v_2, Qtot, Ekin")
        Qtot = (self.ps[0].m*self.ps[0].v.r + self.ps[1].m*self.ps[1].v.r)/2
        Ekin = (self.ps[0].m*self.ps[0].v.r**2 + self.ps[1].m*self.ps[1].v.r**2)/2
        print(f"{self.time:.2f}"+
              f" {self.obstacles[0].r.r:.6f} {self.obstacles[0].v.r:.6f}"+
              f" {self.ps[0].r.r:.6f} {self.ps[0].v.r:.6f}"+
              f" {self.ps[1].r.r:.6f} {self.ps[1].v.r:.6f}"+
              f" {Qtot:.6f} {Ekin:.6f}")

    def plot_phaseSpace_v1_v2(self, ax):
        lns = ax.get_lines() #[]
        r = np.sqrt(self.ps[0].m / self.ps[1].m)
        u = r*self.ps[0].v.r
        v = self.ps[1].v.r
        lns.append(
            ax.plot(u,v, '.', markersize=4, mfc='r', mec='none', alpha=0.9)[0]
        )
        return lns
    
    def plot1d(self, axReal, axPhaseSpace, radius_plot = 0.05,
               v_plot = lambda v: 0.2):
        lns = self.plot_phaseSpace_v1_v2(axPhaseSpace)
        for obstacle in self.obstacles:
            col='black' if obstacle.color is None else obstacle.color
            axReal.axvline(obstacle.r.r, ymin=0, color=col)
        
        for i,p in enumerate(self.ps):
            col="C%d"%i if p.color is None else p.color
            xy = (p.r.r,self.time)
            radius = radius_plot #radius_plot_factor * p.sigma/2
            #patch = Circle(xy, radius)
            #axReal.add_patch(patch)
            lns.append(
                axReal.scatter(*xy, fc=col, ec='none', alpha=0.7)
            )
            if p.v.norm()>1e-6:
                xy_end = (xy[0]+p.v.normalize().r*v_plot(p.v.norm()), xy[1])
                lns.append(
                    axReal.annotate("", xy=xy, xytext=xy_end,
                                    arrowprops=dict(arrowstyle="<-", color=col))
                )
        return lns


    def plot2d(self, axReal, axPhaseSpace, dt_ballistic = 0.0,
               radius_plot = lambda sigma: 0.05,
               v_plot = lambda v: 0.2):
        lns = self.plot_phaseSpace_v1_v2(axPhaseSpace)
        for obstacle in self.obstacles:
            col='black' if obstacle.color is None else obstacle.color
            axReal.axvline(obstacle.r.r, ymin=0, color=col)
        
        for i,p in enumerate(self.ps):
            col="C%d"%i if p.color is None else p.color
            pos = p.r.sum( p.v.mult(dt_ballistic) ) #project to ballistic evolution
            xy = (pos.r,0) if pos.d==1 else (pos.r[0],pos.r[1]) #if 1d embedded in 2d, else pure 2d
            #axReal.add_patch(Circle(xy, radius_plot(p.sigma)))
            lns.append(
                axReal.scatter(*xy, fc=col, ec='none', alpha=0.7)
            )
            if p.v.norm()>1e-6:
                v_plot_vec = p.v.normalize().r*v_plot(p.v.norm())
                xy_end = (xy[0]+v_plot_vec, xy[1]) if p.v.d==1 else (xy[0]+v_plot_vec[0], xy[1]+v_plot_vec[1]) #1d embedded in 2d, or pure 2d
                lns.append(
                    axReal.annotate("", xy=xy, xytext=xy_end,
                                    arrowprops=dict(arrowstyle="<-", color=col))
                )
        xy=(1,0.5)
        lns.append(
            axReal.annotate(f"t={self.time+dt_ballistic :.5g}", xy=xy, xytext=xy, fontsize="small")
        )
        return lns

    def pair_collision_time(self, pi, pj):
        tij = self.BIG_T
        rij = pi.r.diff(pj.r)
        vij = pi.v.diff(pj.v)
        bij = rij.dot(vij)
        if bij < 0: #collision can take place
            sij = (pi.sigma + pj.sigma)/2
            v2 = vij.sqNorm()
            discr = bij*bij - v2*(rij.sqNorm() - sij*sij)
            self.dbprint(f"pair_collision_time: bij<0 ==> collision is possible; discr={discr}")
            if discr >= 0: #collision takes place
                tij = (-bij - np.sqrt(discr))/v2
                self.dbprint(f"pair_collision_time:  discr>=0 ==> collision will place at tij={tij:.6f}")
        return tij

    def collide(self):
        if self.coll_times is None: #first time checking
            self.dbprint("collide: first collision...")
            self.coll_times = self.BIG_T * np.ones(self.N)
            self.coll_partner = np.empty(self.N, dtype=np.int32)
            for i in range(self.N-1):
                pi = self.ps[i]
                for j in range(i+1,self.N):
                    pj = self.ps[j]
                    self.dbprint(f"collide:   checking (particle {i}, particle {j})")
                    tij = self.pair_collision_time(pi, pj)    
                    if tij < self.coll_times[i]:
                        self.coll_times[i] = tij
                        self.coll_partner[i] = j
                    if tij < self.coll_times[j]: #update also particle j's
                        self.coll_times[j] = tij
                        self.coll_partner[j] = i
                #check also against obstacles:
                # obstacles are encoded as extra particles j' = N + j     
                for j in range(len(self.obstacles)):
                    pj = self.obstacles[j]
                    self.dbprint(f"collide:   checking (particle {i}, obstacle {j})")
                    tij = self.pair_collision_time(pi, pj)    
                    if tij < self.coll_times[i]:
                        self.coll_times[i] = tij
                        self.coll_partner[i] = self.N + j
        else: #already checked once
            self.dbprint("collide: non-first collision...")
            for i in range(self.N):
                pi = self.ps[i]
                if (i==self.coll_i or self.coll_partner[i]==self.coll_i or
                    i==self.coll_j or self.coll_partner[i]==self.coll_j): 
                    self.coll_times[i] = self.BIG_T
                    for j in range(self.N):
                        if j!=i:
                            pj = self.ps[j]
                            tij = self.pair_collision_time(pi, pj)    
                            if tij < self.coll_times[i]:
                                self.coll_times[i] = tij
                                self.coll_partner[i] = j
                            if tij < self.coll_times[j]:
                                self.coll_times[j] = tij
                                self.coll_partner[j] = i
                    #check also against obstacles: encoded as extra particles j' = N + j     
                    for j in range(len(self.obstacles)):
                        pj = self.obstacles[j]
                        tij = self.pair_collision_time(pi, pj)    
                        if tij < self.coll_times[i]:
                            self.coll_times[i] = tij
                            self.coll_partner[i] = self.N + j
        self.dbprint("collide: collision times are:",*self.coll_times)
        # check if any collision will take place, otherwise return False
        if (self.coll_times == self.BIG_T).all():
            return False
        #find the shortest collision time
        self.coll_i = self.coll_times.argmin()
        tij = self.coll_times[self.coll_i]
        self.coll_j = self.coll_partner[self.coll_i]
        self.dbprint(f"collide: identified next collision: (particle {self.coll_i}, "+
                     (f"particle {self.coll_j})" if self.coll_j<self.N else f"obstacle {self.coll_j-self.N})"))
        # move all particles, update collision times and global time
        for i in range(self.N):
            self.coll_times[i] -= tij
            pi = self.ps[i]
            pi.r.sum_inplace( pi.v.mult(tij) )
        self.time += tij
        self.dbprint("collide: ballistics updated")
        # collide particles i and j
        if self.debug:
            self.print()
        pi = self.ps[self.coll_i]
        pj = self.ps[self.coll_j] if self.coll_j<self.N else self.obstacles[self.coll_j-self.N]
        rij = pi.r.diff(pj.r)
        self.dbprint(f"collide:  ri={pi.r.r} rj={pj.r.r} ==> rij={rij.r}")
        vij = pi.v.diff(pj.v)
        bij = rij.dot(vij)
        sij = (pi.sigma + pj.sigma)/2
        self.dbprint(f"collide:  r_ij={rij.r:.5f}, s_ij={sij:.5f}, b_ij={bij:.5f}")
        dvi_kinetic = rij.mult(-bij/(sij*sij)) #momentum exchange on particle i
        dvi = dvi_kinetic.mult( 2/(1+pi.m/pj.m))
        dvj = dvi_kinetic.mult(-2/(1+pj.m/pi.m))
        self.dbprint(f"collide:  exchanging dvi_kinetic={dvi_kinetic.r:.5f} dv_i={dvi.r:.5f}, dv_j={dvj.r:.5f}")
        pi.v.sum_inplace(dvi) #velocity update for i
        pj.v.sum_inplace(dvj) #velocity update for j
        self.dbprint("collide: collision updated")
        return True


### Input parameters
sigma = 0.0002 #diameter
x0 = 1
v0 = -1

parser = argparse.ArgumentParser(
    prog = sys.argv[0],
    description = 'Scattering between two particles and a wall at the origin.\n'+
                  '  for mass ratio multiple of 100, the number of scatterings computes pi!',
    epilog=''
)
parser.add_argument('sqrt_mass_ratio',  type=float, help="Square root of the particles' mass ratio.")
parser.add_argument('--max_coll',  type=int, required=False, default=1e8,
                    help="Maximum number of collisions in the simulation. [default: %(default)s]")
parser.add_argument('--show',  type=bool, required=False, default=False,
                    help="Show the plot? [default: %(default)s]")
parser.add_argument('--anim',  type=bool, required=False, default=False,
                    help="Show the animation? [default: %(default)s]")
parser.add_argument('--anim_secs',  type=float, required=False, default=5,
                    help="Real duration of the animation (seconds). [default: %(default)s]")
parser.add_argument('--debug',  type=bool, required=False, default=False,
                    help="Show debugging? [default: %(default)s]")
args = parser.parse_args()

#if len(sys.argv)!=2:
#    print("Usage: <r: sqrt(mass ratio)>")
#    sys.exit(1)
#r = float(sys.argv[1]) # square root of mass ratio
r = args.sqrt_mass_ratio
assert r>=1
assert args.anim_secs>0

#Create the system
particles = [
    HardSphere(r*r, 2*x0, v0, sigma),
    HardSphere(  1,   x0,  0, sigma)
]
obstacles = [ #obstacles in 1d are modelles as particles with infinite mass
    HardSphere(np.inf, 0, 0, 0)
]

system = System(particles, obstacles, debug=args.debug)
u_radius = np.abs(v0*r)

###
if args.show:
    fig,axes = plt.subplots(1,2, figsize=(6,2), dpi=300, tight_layout=True)
    axReal,axPhaseSpace = axes
    axPhaseSpace.add_patch(Circle((0,0), u_radius, fc='none', ec='black'))

    system.plot1d(axReal,axPhaseSpace)
    system.print()
    n_coll = 0 #count collisions
    collided = True #start True in order to enter the while loop
    while collided and n_coll < args.max_coll:
        collided = system.collide()
        if collided:
            n_coll += 1
        system.print()
        system.plot1d(axReal,axPhaseSpace)

    if not collided:
        print(f"Completed after {n_coll} collisions")
    else:
        print(f"Interrupted after max collisions {args.max_coll}", file=sys.stderr)

    axReal.set(xlabel=r"Position $x$", xlim=(system.obstacles[0].r.r,4),
            ylabel="Time", ylim=(-1,system.time+1))
    axPhaseSpace.set(xlabel=r"$u$", xlim=(-u_radius*1.2,u_radius*1.2),
                    ylabel=r"$v$", ylim=(-u_radius*1.2,u_radius*1.2), aspect="equal")
    plt.show()
elif args.anim:
    fig,axes = plt.subplots(1,2, figsize=(6,2), dpi=300, tight_layout=True)
    axReal,axPhaseSpace = axes

    t_coll = [system.time] #list of collision times
    snapshots = [system.copy()]
    n_coll = 0 #count collisions
    collided = True #start True in order to enter the while loop
    while collided and n_coll < args.max_coll:
        collided = system.collide()
        if collided:
            n_coll += 1
            t_coll.append(system.time)
            snapshots.append(system.copy())
    t_coll = np.array(t_coll)

    if not collided:
        print(f"Completed after {n_coll} collisions")
    else:
        print(f"Interrupted after max collisions {args.max_coll}", file=sys.stderr)

    fps = 24 # frames per second of the animation
    t_real = args.anim_secs  # real duration of the animation (seconds)

    maxFrames = int(fps*t_real)
    dt_coll = np.diff(t_coll)
    dt_min = dt_coll.min() #maximum time resolution of the simulation
    dt = dt_min/10 # desired time resolution of the animation
    N = 1+int(t_coll[-1]/dt) # number of simulation snapshots at constant dt
    # adapt N,dt to the constraints: fps,t_real
    N = min(N, maxFrames)
    dt = t_coll[-1]/(N-1)
    
    def init():
        global r, v0, snapshots, axReal, axPhaseSpace, snapshots
        axReal.clear()
        axPhaseSpace.clear()
        axPhaseSpace.add_patch(Circle((0,0), u_radius, fc='none', ec='black'))
        axReal.set(xlabel=r"Position $x$", xlim=(snapshots[0].obstacles[0].r.r,4),
                    ylabel=r"Position $y$", ylim=(-1,+1))
        axPhaseSpace.set(xlabel=r"$u$", xlim=(-u_radius*1.2,u_radius*1.2),
                        ylabel=r"$v$", ylim=(-u_radius*1.2,u_radius*1.2), aspect="equal")
        lns = snapshots[0].plot2d(axReal,axPhaseSpace, dt_ballistic=0)
        return lns

    def update(count):
        global lns, t_coll, dt
        #current animation time
        t_anim = t_coll[0] + dt*count
        #find the saved snapshot at or just before t_anim
        i1 = np.where(t_anim>=t_coll)[0][-1]
        #find the ones you missed due to dt>dt_min
        i0 = 0 if count==0 else np.where(t_anim-dt>=t_coll)[0][-1]
        for i in range(i0,i1+1):
            #project ballistic evolution before the next collision
            dt_mismatch = t_anim - t_coll[i]
            lns = snapshots[i].plot2d(axReal,axPhaseSpace, dt_ballistic=dt_mismatch)
            #print(f"update: count = {count:.0f} ; t_anim = {t_anim:.2g};"+
            #      f" i = {i:d} ; last_sys.time = {snapshots[i].time:.2g}")
        return lns


    ani = FuncAnimation(
        fig,
        update,
        frames=np.arange(0, N),
        init_func=init,
        blit=True,
        interval=1000 / fps,
        repeat_delay=1000,
    )
    plt.show()
else:
    system.print()
    n_coll = 0
    collided = True
    while collided and n_coll < args.max_coll:
        collided = system.collide()
        if collided:
            n_coll += 1
        system.print()

    if not collided:
        print(f"Completed after {n_coll} collisions", file=sys.stderr)
    else:
        print(f"Interrupted after max collisions {args.max_coll}", file=sys.stderr)
