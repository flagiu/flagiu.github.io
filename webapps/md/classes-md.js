class Particle {
    constructor(type, sigma, mass, x, y, vx, vy) {
        this.type = type;
        this.sigma = sigma;
        this.mass = mass;
        this.pos = new Vector(x,y);
        this.vel = new Vector(vx,vy);
        this.color = 'red';
        this.force = new Vector(0.0,0.0);
    }

    set_force(fx,fy) {
        this.force = new Vector(fx,fy);
    }
    
    overlaps( p, sigmaFrac, L ) {
        let thresh = sigmaFrac*0.5*(this.sigma + p.sigma);
        let d2 = ( this.pos.sub(p.pos).mic(L) ).sq();
        return ( d2 < thresh*thresh );
    }

    update(T,P,L,integrator) {
        if(integrator=="Euler") {
            this.vel.add_inplace( this.force.mult_scalar( dt/this.mass ) );
            this.pos.add_inplace( this.vel.mult_scalar( dt ) );
            this.pos.mic_inplace(L); // periodic boundary condition
        } else if(integrator=="Verlet part 1") {
            // force(t)
            this.vel.add_inplace( this.force.mult_scalar( 0.5*dt/this.mass ) );
            this.pos.add_inplace( this.vel.mult_scalar( dt ) );
            this.pos.mic_inplace(L); // periodic boundary condition
        } else if(integrator=="Verlet part 2") {
            // force(t+dt)
            this.vel.add_inplace( this.force.mult_scalar( 0.5*dt/this.mass ) );
        }
    }
}

/*****************************************************************/

class PairInteraction {
    constructor(pair_energy_fun, pair_force_fun) {
        this.energy = pair_energy_fun; // arguments: (vec1,vec2)   output: float
        this.force = pair_force_fun;   // arguments: (vec1,vec2)   output: vec
    }
}

function LJenergy(posA, posB, L) {
    let x2 = 1.0/(posA.sub(posB).mic(L)).sq(); // (sigma/r)^2
    let x6 = x2*x2*x2;
    return 4.0*( x6*x6 - x6 );
}
function LJforce(posA, posB, L) { // from B to A
    let rAB = posA.sub(posB).mic(L);
    let x2 = 1.0/rAB.sq(); // (sigma/r)^2
    let x8 = x2*x2*x2*x2;
    let x14 = x8*x2*x2*x2;
    let f = 4.0*6.0*( 2.0*x14 - x8 );
    return new Vector( f*rAB.x, f*rAB.y );
}

/*****************************************************************/

class System {
    constructor(N, L, pair_interaction) {
        this.N = N;
        this.L = new Vector(L,L); // 0 <= x <= Lx, 0 <= y <= Ly
        this.pi = pair_interaction;
        
        this.ps = new Array(this.N);
        this.V = 0.0;
        this.v = 0.0;
        this.rho = 0.0;
        this.ene_kin = 0.0; // per particle
        this.ene_pot = 0.0; // per particle
        this.virial = 0.0;
        this.integrator = "None";
        
        this.initRanFrac = 0.9; // allows putting two particles within 0.9 of their hard sphere distance, when initializing random
        this.startedRDF = false;
        this.startedSq = false;
    }
    
    init_random(maxcount = 10000) {
        var x,y, i,j, overlap, count;
        for (i=0; i<this.N; i++)
        {
                count = 0;
            do
            {
                x = (Math.random()-0.5) * this.L.x;
                y = (Math.random()-0.5) * this.L.y;
                this.ps[i] = new Particle(1, 1.0, 1.0, x,y, 0.0, 0.0);
                overlap = false;
                for( j=0; j<i; j++)
                {
                    if( this.ps[i].overlaps( this.ps[j], this.initRanFrac, this.L ) )
                    {
                        overlap=true;
                        break;
                    }
                }
                count++;
            } while( overlap && count<maxcount );
            if(count>=maxcount) {
                console.log('WARNING: random initialization falied for particle',i);
                this.ps[i].color = 'blue';
            }
        }
    }
    
    init_xtal(n, ax,ay, bx,by) { // positions in [-L/2, L/2)
        var x,y;
        let nh=Math.floor(n/2);
        for (let i=0; i<n; i++)
        {
            for (let j=0; j<n; j++)
            {
                x = (i-nh+0.5)*ax + (j-nh+0.5)*bx;
                y = (j-nh+0.5)*ay + (j-nh+0.5)*by;
                this.ps[i*n + j] = new Particle(1, 1.0, 1.0, x,y, 0.0, 0.0);
            }
        }
    }
    init_square() {
        let n = Math.floor(Math.sqrt(N));
        if( n*n != N ) console.log("Error: N not adeguate for square lattice");
        let ax = this.L.x / n;
        let ay = 0.0;
        let bx = 0.0;
        let by = this.L.y / n;
        this.init_xtal(n, ax,ay, bx,by);
    }
    init_hex() {
    }
    
    init_maxboltz(T) {
        // remember to divide by the mass!
        let sqrtT = Math.sqrt(T);
        let velCM = new Vector(0.0,0.0);
        for( let i=0; i<this.N; i++ )
        {
            this.ps[i].vel = Gaussian2D( 0.0, sqrtT/this.ps[i].mass );
            velCM.add_inplace(this.ps[i].vel.mult_scalar(1/this.N));
        }
        // remove the average
        for( let i=0; i<this.N; i++ )
        {
            this.ps[i].vel.sub(velCM);
        }
    }
    //---------- end of construction -------------------//
    
    Volume() {
        this.V = this.L.x*this.L.y;
    	return this.V;
    }
    MolarVolume() {
        this.v = this.Volume()/this.N;
    	return this.v;
    }
    NumDensity() {
        this.rho = this.N/this.Volume();
        return this.rho;
    }
    EnergyKinetic() {
        this.ene_kin = 0.0; // per particle
        for( let i=0; i<this.N; i++ )
        {
            this.ene_kin += 0.5 * this.ps[i].mass * this.ps[i].vel.sq() / this.N;
        }
        return this.ene_kin;
    }
    EnergyPotential() {
        this.ene_pot = 0.0; // per particle
        for( let i=0; i<this.N; i++ )
        {
            for( let j=i+1; j<this.N; j++ )
            {
                this.ene_pot += this.pi.energy( this.ps[i].pos, this.ps[j].pos, this.L ) / this.N;
            }
        }
        return this.ene_pot;
    }
    TotalForce() {
        this.tot_force = new Vector(0.0,0.0);
        for( let i=0; i<this.N; i++ )
        {
            for( let j=i+1; j<this.N; j++ )
            {
                this.tot_force.add_inplace( this.pi.force( this.ps[i].pos, this.ps[j].pos, this.L ));
            }
        }
        return this.tot_force;
    }
    Virial() {
        this.virial = 0.0;
        var fij, rij;
        for( let i=0; i<this.N; i++ )
        {
            for( let j=i+1; j<this.N; j++ )
            {
                fij = this.pi.force( this.ps[i].pos, this.ps[j].pos, this.L );
                rij = this.ps[i].pos.sub( this.ps[j].pos );
                this.virial += 2* rij.dot( fij ) / this.N;
            }
        }
        return this.virial;
    }
    
    expand(L) {
    	this.L.x = L;
    	this.L.y = L;
    }

    //--------------- INTEGRATION -------------------------//
    
    set_integrator(value) {
        this.integrator = value;
    }

    calc_all_forces() {
        let N=this.N;
        var i,j, f_ij;
        for(i=0;i<N;i++) { this.ps[i].set_force(0.0, 0.0); }
        for(i=0;i<N;i++) {
            for(j=i+1;j<N;j++) {
                f_ij = this.pi.force( this.ps[i].pos, this.ps[j].pos, this.L );
                this.ps[i].force.add_inplace( f_ij.mult_scalar( 1.0/N) );
                this.ps[j].force.add_inplace( f_ij.mult_scalar(-1.0/N) );
            }
        }
    }

    update(T,P) {
        let N=this.N;
	    let L=this.L;
	    var i;
        if(this.integrator=="NVE - Euler") {
            this.calc_all_forces();
            for(i=0;i<N;i++) { this.ps[i].update(T,P,L, "Euler"); }
        }
        if(this.integrator=="NVE - Verlet") {
            // To start the algorithm, I assume at t=0 all forces are zero !
            for(i=0;i<N;i++) { this.ps[i].update(T,P,L, "Verlet part 1"); }
            this.calc_all_forces();
            for(i=0;i<N;i++) { this.ps[i].update(T,P,L, "Verlet part 2"); }
        }
    }
    
    show(c, w, h) {
        let xfactor = w/this.L.x;
        let yfactor = h/this.L.y;
        let factor = Math.sqrt(xfactor*yfactor);
        var x,y,radius;
        c.clearRect(0, 0, w, h);
        c.fillStyle = "#000000"; // black background (not working...)
        c.fill();
        var x,y;
        for(let i=0; i<this.N; i++) {
            let x_off = this.ps[i].pos.x + 0.5*this.L.x;
            let y_off = this.ps[i].pos.y + 0.5*this.L.y;
            x = Math.floor(xfactor * x_off);
            y = Math.floor(yfactor * y_off);
            radius = 0.5*this.ps[i].sigma*factor;
            //console.log(i,x,y,radius);
            drawCircle(c, x, y, radius, this.ps[i].color, 'black', 2);
        }
    }
    
}

//export class System
