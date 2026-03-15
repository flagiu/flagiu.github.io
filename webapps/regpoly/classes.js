class Points {
	constructor(N) {
		this.fracs = null;
		this.nk = 0;
		this.N = N;
		this.kmax=10000;
		this.tol = 1e-10;
		
		this.generate_points = function(N) {
			this.N = N;
			let repeated = false;
			let k=0;
			this.fracs = createEmptyArray(this.kmax);
			var frac;
			while(!repeated && k<this.kmax){
				frac = (k/N)%1;
				if(k>=1){
					for(let i=0; i<k; i++){
						if(Math.abs(frac-this.fracs[i])<this.tol){
							repeated = true;
						}
					}
				}
				if(!repeated){
					this.fracs[k] = frac;
					k = k+1;
				}
			}
			this.nk = k;
			console.log("N="+this.N+" --> nk="+this.nk+" points");
			return;
		}

		//this.generate_points(this.N);

		this.show = function(c, w, h, R, r, a0) {
			// arguments: context, img_width, img_height, large_circle_radius, small_circles_radius
			let xcenter = w/2;
			let ycenter = h/2;
			c.clearRect(0, 0, w, h);
			c.fillStyle = 'white'; // white background (works?)
			c.fill();
			drawCircle(c, xcenter, ycenter, R, 'white', 'black', 1);
			var a, x, y, ao, xo, yo, ko, f, fo, col, colo, xm, ym;
			for(let k=0; k<this.nk; k++) {
				// current point
				f = k/this.nk;
				a = a0 + 2*Math.PI*this.fracs[k];
				x = xcenter + R*Math.cos(a);
				y = ycenter + R*Math.sin(a);
				col = color(hsvToRgb(f,1,1));
				// old point
				ko = (k-1+this.nk)%this.nk;
				fo = ko/this.nk;
				ao = a0 + 2*Math.PI*this.fracs[ko];
				xo = xcenter + R*Math.cos(ao);
				yo = ycenter + R*Math.sin(ao);
				colo = color(hsvToRgb(fo,1,1));
				// draw
				drawCircle(c, x, y, r, col, 'black', 1);
				xm = (xo+x)*0.5;
				ym = (yo+y)*0.5;
				drawLine(c, xo, yo, xm, ym, colo, 1);
				drawLine(c, xm, ym, x , y , col , 1);
			}
		}

	}
}
