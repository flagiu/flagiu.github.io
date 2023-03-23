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
