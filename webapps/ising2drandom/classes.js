class Ising2D {
    constructor(L, m0=0.0, J0=0.0, h) {
		this.L = Math.floor(L);
		this.m = m0;
		this.e = 0.0;
		this.N = Math.floor(L*L);
		this.s = new Int32Array(this.N);
		this.J = new Float32Array(2*this.N);
	//	this.cup = colors[cup];
	//	this.cdown = colors[cdown];
	//	this.cerr = colors[cerr];
		this.init_random(m0,h,J0);
    }

	compute_magnetization() {
		this.m = 0.0;
		for (let i=0;i<this.N;i++)
			this.m += this.s[i];
		this.m /= this.N;
	}
    
    compute_energy(h) {
		var s, k0,k1,k2, E = 0;
		for (let i=0;i<L;i++) {
			for (let j=0;j<L;j++) {
				k0 = this.L*i + j; // center
				k1 = this.L*((i+1)%this.L) + j; // right
				k2 = this.L*i + (j+1)%this.L; //down
				s = this.s[k0];
				E -=   this.J[k0]*s*this.s[k1]; // center-right interaction
				E -= this.J[k0+1]*s*this.s[k2]; // center-down interaction
				E -= s*h; // field energy
			}
		}
		this.e = E/this.N;
    }

	overlap(other) {
		var q=0;
		if(this.N!=other.N){ console.log("ERROR: cannot compute overlap on different-size systems.")}
		for (let i=0; i<this.N; i++){
			q += this.s[i]*other.s[i];
		}
		q/=this.N;
		return q;
	}

	copy_couplings(other) {
		if(this.N!=other.N){ console.log("ERROR: cannot copy couplings from a different-size systems.")}
		for (let i=0; i<2*this.N; i++) this.J[i] = other.J[i];
	}

	init_random_couplings(J0) {
		let p1 = (1+J0)/2;
		var r;
		for (let i=0; i<2*this.N; i++) {
			this.J[i] = gaussianRandom(J0, 1.0);
			/*
			r = Math.random();
			if(r<p1) this.J[i] =  1;
			else     this.J[i] = -1;
			*/
		}
		this.compute_energy(h);
	}
    
    init_random_spins(m0,h) {
		let p1 = (1+m0)/2;
		var r;
		for (let i=0; i<this.N; i++) {
			r = Math.random();
			if(r<p1) this.s[i] =  1;
			else     this.s[i] = -1;
		}
		this.compute_energy(h);
    }

	init_random(m0, h, J0) {
		this.init_random_couplings(J0);
		this.init_random_spins(m0, h);
		this.compute_energy(h);
	}
    //---------- end of construction -------------------//
    
    update(T,h) {
		let L=this.L;
		var i,j,k0,k1,k2,k3,k4, J1,J2,J3,J4, dE;
		/*
		var lut = {}; // look up table
		for ( let dE=-8; dE<=8; dE+=2) {
			lut[dE.toString()] = {"1": Math.exp(-(dE+h)/T),
					"-1": Math.exp(-(dE-h)/T)};
		}*/

		for ( let a=0; a<this.N; a++) {
			k0 = randInt(0,this.N);
			i = Math.floor(k0/L);
			j = k0%L;
			k1=L*((i+1)%L)+j;   // right
			k2=L*i+(j+1)%L;     // down
			k3=L*((i-1+L)%L)+j; // left
			k4=L*i+(j-1+L)%L;   // up
			J1=this.J[k0];   // center-right interaction
			J2=this.J[k0+1]; // center-down interaction
			J3=this.J[k3];   // left-center interaction
			J4=this.J[k4+1]; // up-center interaction
			dE = 2*this.s[k0]*(
				J1*this.s[k1]+
				J2*this.s[k2]+
				J3*this.s[k3]+
				J4*this.s[k4]
			);
			//if (Math.random() < lut[dE.toString()][this.s[k0].toString()])
			if( this.s[k0]==1  && (Math.random() < Math.exp(-(dE+h)/T) ) ||
			    this.s[k0]==-1 && (Math.random() < Math.exp(-(dE-h)/T) )  )
			{
				this.s[k0]*=-1;
				this.e += dE/this.N; //constantly update energy (and magnetization)
				this.m += 2*this.s[k0]/this.N;
			}
		}

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
		let Jnew = new Float32Array(L*L);
		let factor = Math.floor(this.L/L); // >1
		let bulk_Nsamp = factor*factor;
		var spin, Jh, Jv;
		//BLOCK SPIN: sum subsquares and take the sign (cut out extra borders)
		for (let i=0; i<L; i++) {
			for (let j=0; j<L; j++) {
				spin = 0;
				Jh = Jv = 0.0;
				for(let fi=0; fi<factor; fi++) {
					for(let fj=0; fj<factor; fj++) {
						spin += this.s[L*(i+fi) + j+fj];
						Jh += this.J[L*(i+fi) + j+fj];
						Jv += this.J[L*(i+fi) + j+fj +1];
					}
				}
				if(spin==0) spin=randInt(2)*2-1;
				else spin = Math.sign(spin);
				snew[L*i+j] = spin;
				Jnew[L*i+j] = Jh;
				Jnew[L*i+j+1] = Jv;
			}
		}
		this.s = snew;
		this.J = Jnew;
    }
    
    expand(L) {
		let snew = new Int32Array(L*L);
		let Jnew = new Float32Array(2*L*L);
		let factor = Math.floor(L/this.L); // >1
		let i_,j_;
		for (let i=0; i<L; i++) {
			i_ = Math.floor(i/factor) % this.L;
			for (let j=0; j<L; j++) {
				j_ = Math.floor(j/factor) % this.L;
				snew[i*L+j] = this.s[this.L*i_+j_];
				Jnew[i*L+j] = this.J[this.L*i_+j_];
				Jnew[i*L+j+1] = this.J[this.L*i_+j_+1];
			}
		}
		this.s = snew;
		this.J = Jnew;
    }

    show(c, x0, y0, w, h) {
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
	c.putImageData(id, x0, y0);
    }
    
}
