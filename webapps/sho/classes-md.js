class Particle1D {
    constructor(type, sigma, mass, x, v) {
	this.type = type;
	this.sigma = sigma;
	this.m = mass;
	this.x = x;
	this.v = v;
	this.color = 'red';
    }
    
    restart(x0, v0) {
        this.x = x0;
        this.v = v0;
    }
    
    //--------------- INTEGRATION with Euler-Maruyama method -------------------------//
    
    update(dt, T,eta,k) {
        let ran = Gaussian2D( 0.0, Math.sqrt(2*T*eta*dt) );
        let vnew = this.v + ( -eta*this.v*dt -k*this.x*dt +ran.x )/this.m;
        let xnew = this.x + this.v*dt;
        this.x = xnew;
        this.v = vnew;
    }
    
}

class System1D {
    constructor() {
        this.particles = new Array();
        this.x = 0.0;
        this.v = 0.0;
        this.x2 = 0.0;
        this.v2 = 0.0;
        this.dx2 = 0.0;
        this.dv2 = 0.0;
        this.N=0
    }

    add_particle(particle) {
        this.N = this.N+1;
        this.particles.push(particle);
        // update average x,v,x^2,v^2
        this.x = (this.x * (this.N-1) + particle.x) / this.N;
        this.v = (this.v * (this.N-1) + particle.v) / this.N;
        this.x2 = (this.x2 * (this.N-1) + particle.x*particle.x) / this.N;
        this.v2 = (this.v2 * (this.N-1) + particle.v*particle.v) / this.N;
        this.dx2 = this.x2 - this.x*this.x;
        this.dv2 = this.v2 - this.v*this.v;
    }
    
    restart(x0, v0) {
        this.particles.forEach( (el) => el.restart(x0,v0) );
        this.x = x0;
        this.v = v0;
        this.x2 = x0*x0;
        this.v2 = v0*v0;
        this.dx2 = this.x2 - this.x*this.x;
        this.dv2 = this.v2 - this.v*this.v;
    }
    
    update(dt, T,eta,k) {
        this.x = 0.0;
        this.v = 0.0;
        this.x2 = 0.0;
        this.v2 = 0.0;
        for(var i=0;i<N;i++) {
            this.particles[i].update(dt,T,eta,k);
            this.x += this.particles[i].x / this.N;
            this.v += this.particles[i].v / this.N;
            this.x2 += this.particles[i].x*this.particles[i].x / this.N;
            this.v2 += this.particles[i].v*this.particles[i].v / this.N;
        }
        this.dx2 = this.x2 - this.x*this.x;
        this.dv2 = this.v2 - this.v*this.v;
    }
    
}