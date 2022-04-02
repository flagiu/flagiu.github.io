// "Rock-Paper-Scissors" system evolving according to Belousov–Zhabotinsky equations
function RPS(L, img, colornames) {
    this.L = int(L);
    this.N = int(L*L);
    this.Nch = colornames.length; //number of chemicals
    this.c = createEmptyArray(this.L, this.L, this.Nch); //concentration
    this.cnew = this.c;
    this.clrs = []; //colors
    for (let i=0; i<this.Nch; i++)
	this.clrs.push(colors[colornames[i]]);
    this.img = img;
    this.factor = Math.floor(this.img.width/this.L);
    
    this.init_random = function() {
	for (let i=0; i<this.L; i++)
	    for (let j=0; j<this.L; j++)
		for (let ch=0; ch<this.Nch; ch++)
		    this.c[i][j][ch] = Math.random();
    }
    this.init_random();
    //************************************ end of construction
    
    this.update = function(D,A, dt) {
	let L=this.L;
	for (let i=0; i<L; i++) {
	    for (let j=0; j<L; j++) {
		let rho = 0.0; //total concentration of chemicals
		for(let ch=0; ch<this.Nch; ch++)
		    rho += this.c[i][j][ch];
		for(let ch=0; ch<this.Nch; ch++) {
		    let lap = this.c[(i+1)%L][j][ch] +
			this.c[(i-1+L)%L][j][ch] +
			this.c[i][(j+1)%L][ch] +
			this.c[i][(j-1+L)%L][ch] -
			2*2*this.c[i][j][ch]; // local laplacian
		    
		    this.cnew[i][j][ch] = this.c[i][j][ch] + dt * (
			D*lap + this.c[i][j][ch]*(1-rho-A*this.c[i][j][(ch+1)%this.Nch])
		    ); //integration step
		}
	    }
	}
	this.c = this.cnew;
    }

    this.resize = function(L) {
	if(L==this.L) return;
	else if (L<this.L) this.reduce(L);
	else this.expand(L);
	this.L = L;
	this.N = int(L*L);
	this.factor = Math.floor(this.img.width/this.L);
	//this.img = createImage(L,L);
    }

    this.reduce = function(L) {
	let factor = Math.floor(this.L/L);
	let bulk_Nsamp = factor*factor;
	this.cnew = createConstArray(0, L,L,this.Nch);
	// average subsquares
	for (let i=0; i<L; i++) {
	    for (let j=0; j<L; j++) {
		for(let ch=0; ch<this.Nch; ch++) {
		    for(let fi=0; fi<factor; fi++) {
			for(let fj=0; fj<factor; fj++) {
			    this.cnew[i][j][ch] += this.c[i+fi][j+fj];
			}
		    }
		    this.cnew[i][j][ch] /= bulk_Nsamp;
		}
	    }
	}
	this.c = this.cnew;
    }
    
    this.expand = function(L) {
	let factor = Math.floor(L/this.L);
	this.cnew = createEmptyArray(L,L, this.Nch);
	let jc,ic=0;
	for (let i=0; i<L; i++) {
	    i_ = Math.floor(i/factor) % this.L;
	    for (let j=0; j<L; j++) {
		j_ = Math.floor(j/factor) % this.L;
		for(let ch=0; ch<this.Nch; ch++)
		    this.cnew[i][j][ch] = this.c[i_][j_][ch];
	    }
	}
	this.c = this.cnew;
    }

    this.show = function() {
	this.img.loadPixels();
	for (let i = 0; i < this.img.width; i++) {
	    let i_ = Math.floor(i/this.factor) % this.L;
	    for (let j = 0; j < this.img.height; j++) {
		let j_ = Math.floor(j/this.factor) % this.L;
		let r = int( this.c[i_][j_][0] *255);
		let g = int( this.c[i_][j_][1] *255);
		let b = int( this.c[i_][j_][2] *255);
		this.img.set(i,j,color(r,g,b));
			     //avgP5Colors( this.clrs, this.c[i_][j_])
			    //);
	    }
	}
	this.img.updatePixels();
	image(this.img, 0,0);//w/2-this.L/2, h/2-this.L/2);
    }
    
}
