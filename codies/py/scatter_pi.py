"""
From 3b1b 's video on computing Pi with colliding blocks
https://www.youtube.com/watch?v=6dTyOl1fmDo
"""
import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate as intg
from matplotlib.patches import Circle
from matplotlib.animation import FuncAnimation
import sys

class Vec():
    def __init__(self, r):
        if hasattr(r, "len"):
            self.d = len(r)
        else:
            self.d = 1
        self.r = np.array(r)

    def diff(self, other):
        return Vec(self.r - other.r)
    
    def diff_inplace(self, other):
        self.r = self.r - other.r

    def sum(self, other):
        return Vec(self.r + other.r)
    
    def sum_inplace(self, other):
        self.r = self.r + other.r

    def mult(self, factor):
        return Vec(self.r * factor)

    def mult_inplace(self, factor):
        self.r = self.r * factor

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
    def __init__(self, mass, position, velocity, pbc=None):
        self.m = mass
        self.r = Vec(position)
        self.v = Vec(velocity)
        self.pbc = pbc

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
    def __init__(self, particles, walls, debug=False):
        self.ps = particles
        self.N = len(self.ps)
        self.walls = walls
        self.coll_times = None
        self.coll_partner = None
        self.BIG_T = 1e10  # a large default collision time
        self.debug=debug
        self.time = 0

    def dbprint(self, *args, **kwargs):
        if self.debug:
            print(*args, **kwargs)

    def print(self):
        if self.time==0:
            print("# Time, x_1, v_1, x_2, v_2, Qtot, Ekin")
        Qtot = (self.ps[0].m*self.ps[0].v.r + self.ps[1].m*self.ps[1].v.r)/2
        Ekin = (self.ps[0].m*self.ps[0].v.r**2 + self.ps[1].m*self.ps[1].v.r**2)/2
        print(f"{self.time:.2f}"+
              f" {self.walls[0].r.r:.6f} {self.walls[0].v.r:.6f}"+
              f" {self.ps[0].r.r:.6f} {self.ps[0].v.r:.6f}"+
              f" {self.ps[1].r.r:.6f} {self.ps[1].v.r:.6f}"+
              f" {Qtot:.6f} {Ekin:.6f}")

    def plot1d(self, axReal, axPhaseSpace, radius_plot = 0.05, normalize_v=True, v_plot=0.2):
        for wall in self.walls:
            axReal.axvline(wall.r.r, ymin=0, color='k')
        
        for i,p in enumerate(self.ps):
            col="C%d"%i
            xy = (p.r.r,self.time)
            radius = radius_plot #radius_plot_factor * p.sigma/2
            #patch = Circle(xy, radius)
            #axReal.add_patch(patch)
            axReal.scatter(*xy, fc=col, ec='none', alpha=0.7)
            if p.v.norm()>1e-6:
                axReal.annotate("", xy=xy, xytext=(xy[0]+p.v.normalize().r*v_plot, xy[1]),
                                arrowprops=dict(arrowstyle="<-", color=col))

        r = np.sqrt(self.ps[0].m / self.ps[1].m)
        u = r*self.ps[0].v.r
        v = self.ps[1].v.r
        axPhaseSpace.scatter(u,v, fc='r', ec='none', alpha=0.9, s=1)

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
                #check also against walls:
                # walls are encoded as extra particles j' = N + j     
                for j in range(len(self.walls)):
                    pj = self.walls[j]
                    self.dbprint(f"collide:   checking (particle {i}, wall {j})")
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
                    #check also against walls: encoded as extra particles j' = N + j     
                    for j in range(len(self.walls)):
                        pj = self.walls[j]
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
                     (f"particle {self.coll_j})" if self.coll_j<self.N else f"wall {self.coll_j-self.N})"))
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
        pj = self.ps[self.coll_j] if self.coll_j<self.N else self.walls[self.coll_j-self.N]
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
max_collisions = 1e8
debug = False

if len(sys.argv)!=2:
    print("Usage: <r: sqrt(mass ratio)>")
    sys.exit(1)
r = float(sys.argv[1]) # square root of mass ratio
assert r>=1

#Create the system
particles = [
    HardSphere(r*r, 2*x0, v0, sigma),
    HardSphere(  1,   x0,  0, sigma)
]
walls = [ #walls in 1d are modelles as particles with infinite mass
    HardSphere(np.inf, 0, 0, 0)
]

system = System(particles, walls, debug=debug)

###
plot=False
if plot:
    fig,axes = plt.subplots(1,2, figsize=(6,2), dpi=300, tight_layout=True)
    axReal,axPhaseSpace = axes
    u_radius = np.abs(v0*r)
    axPhaseSpace.add_patch(Circle((0,0), u_radius, fc='none', ec='black'))

    system.plot1d(axReal,axPhaseSpace)
    system.print()
    n_collisions = 0
    collided = True
    while collided and n_collisions < max_collisions:
        collided = system.collide()
        if collided:
            n_collisions += 1
        system.print()
        system.plot1d(axReal,axPhaseSpace)

    if not collided:
        print(f"Completed after {n_collisions} collisions")
    else:
        print("Interrupted")

    axReal.set(xlabel=r"Position $x$", xlim=(x_wall,4),
            ylabel="Time", ylim=(-1,system.time+1))
    axPhaseSpace.set(xlabel=r"$u$", xlim=(-u_radius*1.2,u_radius*1.2),
                    ylabel=r"$v$", ylim=(-u_radius*1.2,u_radius*1.2), aspect="equal")
    plt.show()
else:
    system.print()
    n_collisions = 0
    collided = True
    while collided and n_collisions < max_collisions:
        collided = system.collide()
        if collided:
            n_collisions += 1
        system.print()

    if not collided:
        print(f"Completed after {n_collisions} collisions", file=sys.stderr)
    else:
        print(f"Interrupted after max collisions {max_collisions}", file=sys.stderr)
