function Potts2D(L=16,q=2, h=0, img) {
    this.L = int(L);
    this.q = q; // n. of spin values s={0,1,...,q-1}
    this.e = 0.0;
    this.N = int(L*L);
    this.cs = []
    for (let i=0; i<this.q; i++)
	this.cs.push(colordict.value(i));
    this.img = img;
    this.factor = Math.floor(this.img.width/this.L);
    
    this.energy = function(h) {
	var E = 0;
	for (let i=0;i<L;i++)
	    for (let j=0;j<L;j++) {
		let s = this.s[i][j];
		E -= ( deltaKron(s, this.s[(i+1)%this.L][j]) +
		       deltaKron(s, this.s[i][(j+1)%this.L])
		     );
	    }
	return E/this.N;
    }
    this.init_random = function(h) {
	var s = createConstArray(-1,L,L); // 2d array of spins -1
	this.m = 0.0;
	for (let i=0; i<L; i++)
	    for (let j=0; j<L; j++) {
		s[i][j] = randInt(0,this.q); // uniform in {1,...,q-1}
		this.m += deltaKron(0, s[i][j]);
	    }
	this.s = s;
	this.m /= this.N;
	this.e = this.energy(h);
    }
    this.init_random(h);
    //************************ end of constructor
    
    this.update = function(T,h) {
	let L=this.L;
	/*
	var lut = {} // look up table
	for ( let dE=-8; dE<=8; dE+=2) {
	    lut[dE.toString()] = [];
	    for( let s=0; s<q; s++) {
		lut[de.toString()][s.toString()] = Math.exp(-(dE+h)/T),
	     "-1": Math.exp(-(dE-h)/T)};
	    }
	}*/
	for ( let a=0; a<this.N; a++) {
	    let i = randInt(0,L);
	    let j = randInt(0,L);
	    let s = this.s[i][j];
	    let snew = (s + 1+randInt(0,this.q-1) )%this.q; //random different from s
	    let dE = ( h * (s-snew) +
		deltaKron( s, this.s[(i+1)%L][j] ) + deltaKron( s, this.s[(i-1+L)%L][j] ) + deltaKron( s, this.s[i][(j+1)%L] ) + deltaKron( s, this.s[i][(j-1+L)%L] ) - ( deltaKron( snew, this.s[(i+1)%L][j] ) + deltaKron( snew, this.s[(i-1+L)%L][j] ) + deltaKron( snew, this.s[i][(j+1)%L] ) + deltaKron( snew, this.s[i][(j-1+L)%L] ) )
		     );
	    let prob = Math.exp(-dE/T);//lut[dE.toString()][s.toString()]
	    if (prob>=1 || Math.random() < prob)
	    {
		this.s[i][j] = snew;
		this.e += dE/this.N;//constantly update energy
	    }
	}
	this.m = 0.0;
	for (let i=0;i<this.L;i++)
	    for (let j=0;j<this.L;j++)
		this.m += deltaKron(0,this.s[i][j]);
	this.m /= this.N;
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
	factor = Math.floor(this.L/L);
	bulk_Nsamp = factor*factor;
	s = createConstArray(0, L,L);
	//BLOCK SPIN: sum subsquares and take the sign (cut out extra borders)
	for (let i=0; i<L; i++) {
	    for (let j=0; j<L; j++) {
		for(let fi=0; fi<factor; fi++) {
		    for(let fj=0; fj<factor; fj++) {
			s[i][j] += this.s[i+fi][j+fj];
		    }
		}
		if(s[i][j]==0) s[i][j]=randInt(2)*2-1;
		else s[i][j] = Math.sign(s[i][j]);
	    }
	}
	this.s = s;
    }
    
    this.expand = function(L) {
	factor = Math.floor(L/this.L);
	let s = createEmptyArray(L,L); // 2d array of spins +1,-1
	let jc,ic=0;
	for (let i=0; i<L; i++) {
	    i_ = Math.floor(i/factor) % this.L;
	    for (let j=0; j<L; j++) {
		j_ = Math.floor(j/factor) % this.L;
		s[i][j] = this.s[i_][j_];
	    }
	}
	this.s = s;
    }

    this.show = function() {
	this.img.loadPixels();
	for (let i = 0; i < this.img.width; i++) {
	    let i_ = Math.floor(i/this.factor) % this.L;
	    for (let j = 0; j < this.img.height; j++) {
		let j_ = Math.floor(j/this.factor) % this.L;
		let c = this.cs[this.s[i_][j_]]; //color is indexed by spin
		this.img.set(i,j, c);
	    }
	}
	this.img.updatePixels();
	image(this.img, 0,0);//w/2-this.L/2, h/2-this.L/2);
    }
    
}
