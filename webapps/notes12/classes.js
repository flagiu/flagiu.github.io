class Notes {
	constructor(startingFrequency, ratio) {
		this.f0 = startingFrequency;
		this.r = ratio;
		
		

		this.generate_notes = function(N) {
			this.notes = createEmptyArray(1);
			this.notes[0] = this.f0;
			let L = this.L;
			let d = this.d;
			for (let i = 0; i < N-1; i++) {
				this.notes[i+1] = this.notes[i]*this.r;
			}
		}

		this.init_random = function () {
			// start with empty density and velocity
			this.zero_dens_vel();
			// fill randomly
			let L = this.L;
			let d = this.d;
			this.N = 0;
			for (let i = 0; i < L; i++) {
				for (let j = 0; j < L; j++) {
					for (let k = 0; k < d; k++) {
						if (Math.random() < this.rho) {
							this.vel[i * L + j][k] = 1;
							this.c[i * L + j] += 1;
							this.N += 1;
						}
					}
				}
			}
			console.log("N:", this.N, " Real Density:", this.N / (this.d*this.V));
		};
		this.init_random();
		//************************************ end of construction

		this.init_cube = function () {
			// start with empty density and velocity
			this.zero_dens_vel();
			// fill central cube
			let L = this.L;
			let d = this.d;
			let dL = int(L*Math.sqrt(this.rho)); //25;
			this.N=0;
			for (let i = int(L*0.5 - dL*0.5); i < int(L*0.5 + dL*0.5); i++) {
				for (let j = int(L*0.5 - dL*0.5); j < int(L*0.5 + dL*0.5); j++) {
					for (let k = 0; k < d; k++) {
						this.vel[i * L + j][k] = 1;
						this.c[i * L + j] += 1;
						this.N+=1;
					}
				}
			}
			console.log("N:", this.N, " Real Density:", this.N / (this.d*this.V));
		};

		this.init_sphere = function () {
			// start with empty density and velocity
			this.zero_dens_vel();
			// fill central sphere (circle)
			let L = this.L;
			let d = this.d;
			let L2 = L/2.0;
			let radius = int(L*Math.sqrt(this.rho / Math.PI)); //25;
			this.N=0;
			for (let i = 0; i < L; i++) {
				for (let j = 0; j < L; j++) {
					if( (i-L2)*(i-L2) + (j-L2)*(j-L2) > radius*radius ) continue;
					for (let k = 0; k < d; k++) {
						this.vel[i * L + j][k] = 1;
						this.c[i * L + j] += 1;
						this.N+=1;
					}
				}
			}
			console.log("N:", this.N, " Real Density:", this.N / (this.d*this.V));
		};

		this.detect_single_collision = function (i, j) {
			/*
			let cij=this.c[i*L+j];
			let vij=this.v[i*L+j];
			// nothing happens if density is 0,1,4
			if(cij==0||cij==1||cij==4) return;
			// one collision if density is 2
			else if(cij==2){
				if(vij[0]==1 && vij[2]==1) { // head-to-head collision along x
					vij[0]=0; vij[2]=0; // scatter along y
					vij[1]=1; vij[3]=1;
					console.log("x-Collision detected at i,j =",i,j);
				}
				else if(vij[1]==1 && vij[3]==1) { // head-to-head collision along y
					vij[0]=1; vij[2]=1; // scatter along x
					vij[1]=0; vij[3]=0;
					console.log("y-Collision detected at i,j =",i,j);
				}
				// in the orthogonal cases, they don't interact
			} else{
				console.log("Error! Density not defined:",this.c[i*L+j])
			}
			*/
		};

		this.detect_collisions = function () {
			let L = this.L;
			let d = this.d;
			let c = this.c;
			let v = this.vel;
			let v_new = createEmptyArray(this.V, this.d);
			let c_new = createEmptyArray(this.V);
			var ij, psi1, psi2, psi;
			for (let i = 0; i < L; i++) {
				for (let j = 0; j < L; j++) {
					ij = i * L + j;
					//this.detect_single_collision(i,j);
					psi1 = v[((i - 1 + L) % L) * L + j][0] * v[((i + 1) % L) * L + j][2] * (1 - v[i * L + (j - 1 + L) % L][1]) * (1 - v[i * L + (j + 1) % L][3]);
					psi2 = (1 - v[((i - 1 + L) % L) * L + j][0]) * (1 - v[((i + 1) % L) * L + j][2]) * v[i * L + (j - 1 + L) % L][1] * v[i * L + (j + 1) % L][3];
					psi = psi1 - psi2;
					v_new[ij][0] = v[((i - 1 + L) % L) * L + j][0] - psi;
					v_new[ij][1] = v[i * L + (j - 1 + L) % L][1] + psi;
					v_new[ij][2] = v[((i + 1) % L) * L + j][2] - psi;
					v_new[ij][3] = v[i * L + (j + 1) % L][3] + psi;
					c_new[ij] = v_new[ij][0] + v_new[ij][1] + v_new[ij][2] + v_new[ij][3];
				}
			}
			this.c = c_new;
			this.vel = v_new;
		};

		this.get_new_position = function (i, j, direction) {
			// must be 0,1,2,3
			let L = this.L;
			var inew,jnew;
			if (direction == 0) { // 1=(1,0) : move right
				inew = (i + 1) % L;
				jnew = j;
			} else if (direction == 1) { // 2=(0,1) : move up
				inew = i;
				jnew = (j + 1) % L;
			} else if (direction == 2) { // 3=(-1,0) : move left
				inew = (i - 1 + L) % L;
				jnew = j;
			} else if (direction == 3) { // 4=(0,-1) : move down
				inew = i;
				jnew = (j - 1 + L) % L;
			} else {
				console.log("Error! Direction not defined:", direction);
			}
			return inew * L + jnew;
		};

		this.evolve = function () {
			let L = this.L;
			let d = this.d;
			var ijnew;
			let vel_new = this.vel;
			let c_new = this.c;
			for (let i = 0; i < L; i++) {
				for (let j = 0; j < L; j++) {
					for (let k = 0; k < d; k++) {
						if (this.vel[i * L + j][k] > 0) {
							vel_new[i * L + j][k] -= 1;
							c_new[i * L + j] -= 1;
							ijnew = this.get_new_position(i, j, k);
							vel_new[ijnew][k] += 1;
							c_new[ijnew] += 1;
						}
					}
				}
			}
			this.vel = vel_new;
			this.c = c_new;
		};

		this.update = function () {
			this.detect_collisions();
			this.evolve();
		};

		this.show = function () {
			this.img.loadPixels();
			for (let i = 0; i < this.img.width; i++) {
				let i_ = Math.floor(i / this.factor) % this.L;
				for (let j = 0; j < this.img.height; j++) {
					let j_ = Math.floor(j / this.factor) % this.L;
					let col = int(this.c[i_ * L + j_] / this.d * 255);
					this.img.set(i, j, color(col));
				}
			}
			this.img.updatePixels();
			image(this.img, 0, 0); //w/2-this.L/2, h/2-this.L/2);
		};

	}
}
