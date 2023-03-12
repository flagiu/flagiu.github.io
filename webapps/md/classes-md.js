class Particle {
    constructor(type, sigma, x, y, vx, vy) {
	this.type = type;
	this.sigma = sigma;
	this.pos = new Vector(x,y);
	this.vel = new Vector(vx,vy);
	this.color = 'red';
    }
    
    overlaps( p, sigmaFrac, L ) {
        let thresh = sigmaFrac*0.5*(this.sigma + p.sigma);
        let d2 = ( this.pos.sub(p.pos).mic(L) ).sq();
        return ( d2 < thresh*thresh );
    }
}

/*****************************************************************/

class PairInteraction {
    constructor(pair_energy_fun, pair_force_fun) {
        this.energy = pair_energy_fun; // arguments: (vec1,vec2)   output: float
        this.force = pair_force_fun;   // arguments: (vec1,vec2)   output: vec
    }
}

function LJenergy(posA, posB) {
    let x2 = 1.0/(posA.sub(posB)).sq(); // (sigma/r)^2
    let x6 = x2*x2*x2;
    return ( x6*x6 - x6 );
}
function LJforce(posA, posB) {
    let rAB = posA.sub(posB);
    let x2 = 1.0/(rAB).sq(); // (sigma/r)^2
    let x8 = x2*x2*x2*x2;
    let x14 = x8*x2*x2*x2;
    let f = 6*( 2*x14 - x8 );
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
	
	this.initRanFrac = 0.9; // allows putting two particles within 0.9 of their hard sphere distance, when initializing random
    }
    
    init_random(maxcount = 10000) {
	var x,y, i,j, overlap, count;
	for (i=0; i<this.N; i++)
	{
            count = 0;
	    do
	    {
                x = Math.random() * this.L.x;
                y = Math.random() * this.L.y;
                this.ps[i] = new Particle(1, 1.0, x,y, 0.0, 0.0);
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
    
    init_xtal(n, ax,ay, bx,by) {
	var x,y;
	for (let i=0; i<n; i++)
	{
	    for (let j=0; j<n; j++)
	    {
	         x = (i+0.5)*ax + (j+0.5)*bx;
	         y = (j+0.5)*ay + (j+0.5)*by;
	         this.ps[i*n + j] = new Particle(1, 1.0, x,y, 0.0, 0.0);
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
        let sqrtT = Math.sqrt(T);
        for( let i=0; i<this.N; i++ )
        {
            this.ps[i].vel = Gaussian2D( 0.0, sqrtT );
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
        this.ene_kin = 0.0;
        for( let i=0; i<this.N; i++ )
        {
            this.ene_kin += 0.5 * this.ps[i].vel.sq() / this.N;
        }
        return this.ene_kin;
    }
    EnergyPotential() {
        this.ene_pot = 0.0;
        for( let i=0; i<this.N; i++ )
        {
            for( let j=i+1; j<this.N; j++ )
            {
                this.ene_pot += this.pi.energy( this.ps[i].pos, this.ps[j].pos ) / this.N;
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
                this.tot_force.add_inplace( this.pi.force( this.ps[i].pos, this.ps[j].pos ) / this.N );
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
                fij = this.pi.force( this.ps[i].pos, this.ps[j].pos );
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
    
    update(T,P) {
	let L=this.L;
	var i,j;
    }
    
    show(c, w, h) {
	let xfactor = w/this.L.x;
	let yfactor = h/this.L.y;
	let factor = Math.sqrt(xfactor*yfactor);
	var x,y,radius;
	c.clearRect(0, 0, w, h);
	c.fillStyle = "#000000"; // black background (not working...)
	var x,y;
	for(let i=0; i<this.N; i++) {
	    x = Math.floor(xfactor * this.ps[i].pos.x);
            y = Math.floor(yfactor * this.ps[i].pos.y);
            radius = 0.5*this.ps[i].sigma*factor;
            //console.log(i,x,y,radius);
            drawCircle(c, x, y, radius, this.ps[i].color, 'black', 2);
	}
    }
    
}

//export class System
