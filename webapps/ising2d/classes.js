class Ising2D {
    constructor(L, m0=0.0, h) {
	this.L = Math.floor(L);
	this.m = m0;
	this.e = 0.0;
	this.N = Math.floor(L*L);
	this.s = new Int32Array(this.N);
//	this.cup = colors[cup];
//	this.cdown = colors[cdown];
//	this.cerr = colors[cerr];
	this.init_random(m0,h);
    }
    
    energy(h) {
	var s, idx, E = 0;
	for (let i=0;i<L;i++)
	    for (let j=0;j<L;j++) {
		s = this.s[i][j];
		idx = this.L*((i+1)%this.L) + j; // right
		E -= s*this.s[idx];
		idx = this.L*i + (j+1)%this.L; //down
		E -= s*this.s[idx];
		E -= s*h;
	    }
	return E/this.N;
    }
    
    init_random(m0,h) {
	let p1 = (1+m0)/2;
	var r;
	for (let i=0; i<this.N; i++)
	{
	    r = Math.random();
	    if(r<p1) this.s[i] =  1;
	    else     this.s[i] = -1;
	}
	this.e = this.energy(h);
    }
    //---------- end of construction -------------------//
    
    update(T,h) {
	let L=this.L;
	var i,j,lut = {} // look up table
	for ( let dE=-8; dE<=8; dE+=2) {
	    lut[dE.toString()] = {"1": Math.exp(-(dE+h)/T),
				  "-1": Math.exp(-(dE-h)/T)};
	}
	for ( let a=0; a<this.N; a++) {
	    let k = randInt(0,this.N);
	    i = Math.floor(k/L);
	    j = k%L;
	    let dE = 2*this.s[k]*(
		this.s[L*((i+1)%L)+j]+
		    this.s[L*((i-1+L)%L)+j]+
		    this.s[L*i+(j+1)%L]+
		    this.s[L*i+(j-1+L)%L]
	    );
	    if (Math.random() < lut[dE.toString()][this.s[k].toString()])
	    {
		this.s[k]*=-1;
		this.e += dE/this.N; //constantly update energy
	    }
	}
	this.m = 0.0;
	for (let i=0;i<this.N;i++)
		this.m += this.s[i];
	this.m /= this.N;
    }
    
    resize(L) {
	if(L==this.L) return;
	else if (L<this.L) this.reduce(L);
	else this.expand(L);
	this.L = L;
	this.N = Math.floor(L*L);
	//this.img = createImage(L,L);
    }
    
    reduce(L) {
	let snew = new Int32Array(L*L);
	let factor = Math.floor(this.L/L); // >1
	let bulk_Nsamp = factor*factor;
	var spin;
	//BLOCK SPIN: sum subsquares and take the sign (cut out extra borders)
	for (let i=0; i<L; i++) {
	    for (let j=0; j<L; j++) {
		spin = 0;
		for(let fi=0; fi<factor; fi++) {
		    for(let fj=0; fj<factor; fj++) {
			spin += this.s[L*(i+fi) + j+fj];
		    }
		}
		if(spin==0) spin=randInt(2)*2-1;
		else spin = Math.sign(spin);
		snew[L*i+j] = spin;
	    }
	}
	this.s = snew;
    }
    
    expand(L) {
	let snew = new Int32Array(L*L);
	let factor = Math.floor(L/this.L); // >1
	let i_,j_;
	for (let i=0; i<L; i++) {
	    i_ = Math.floor(i/factor) % this.L;
	    for (let j=0; j<L; j++) {
		j_ = Math.floor(j/factor) % this.L;
		snew[i*L+j] = this.s[this.L*i_+j_];
	    }
	}
	this.s = snew;
    }

    show(c, w, h) {
	let xfactor = Math.floor(w/this.L);
	let yfactor = Math.floor(h/this.L);
	c.clearRect(0, 0, w, h);
	c.fillStyle = "#00FF00"; // green background (for debugging)
	let r,g,b, id = c.getImageData(0,0, w,h)
	/*
	img.loadPixels();
	for (let i = 0; i < img.width; i++) {
	    let i_ = Math.floor(i/xfactor) % this.L;
	    for (let j = 0; j < img.height; j++) {
		let j_ = Math.floor(j/yfactor) % this.L;
		if( this.s[this.L*i_+j_]==1)
		    img.set(i,j, this.cup);
		else if (this.s[this.L*i_+j_]==-1)
		    img.set(i,j, this.cdown);
		else
		    img.set(i,j, this.cerr); //wrong value (for debugging)
	    }
	}
	img.updatePixels();
	image(img, 0,0);//w/2-this.L/2, h/2-this.L/2);
	*/
	for( var i=0; i<this.L; i++) {
	    var x = Math.floor(xfactor * i);
	    for( var j=0; j<this.L; j++) {
		var y = Math.floor(yfactor*j);
		var cx = Math.floor(xfactor * 1.1) + 1;
		var cy = Math.floor(yfactor * 1.1) + 1;
		if( this.s[this.L*i+j]==1) {
		    r = 255;
		    g = 255;
		    b = 255;
		}else if( this.s[this.L*i+j]==-1) {
		    r = 0;
		    g = 0;
		    b = 0;
		}else {
		    r = 255;
		    g = 0;
		    b = 0;
		}

		for (var yi = y; yi < y + cy; yi++) {
		    var p = 4 * (w*yi + x)

		    for (var xi = 0; xi < cx; xi++) {
			id.data[p++] = r;
			id.data[p++] = g;
			id.data[p++] = b;
			id.data[p++] = 255;
		    }
		}
	    }
	}
	c.putImageData(id, 0, 0);
    }
    
}
