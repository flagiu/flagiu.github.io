class Notes {
	constructor(startingFrequency, ratio) {
		this.f0 = startingFrequency;
		this.q = ratio;
		
		this.generate_notes = function(N) {
			this.freq = createEmptyArray(N);
			this.freq[0] = this.f0;
			var logf;
			for (let i = 1; i < N; i++) {
				this.freq[i] = this.q * this.freq[i-1];
				logf = Math.log2(this.freq[i]/this.f0);
				this.freq[i] = this.f0*Math.pow(2, logf%1);
			}
			this.freq.sort();
			return this.freq;
		}

		this.generate_notes(1);

		this.show = function(c, w, h, R, r) {
			// arguments: context, img_width, img_height, large_circle_radius, small_circles_radius
			let xcenter = w/2;
			let ycenter = h/2;
			c.clearRect(0, 0, w, h);
			c.fillStyle = 'white'; // white background (works?)
			c.fill();
			drawCircle(c, xcenter, ycenter, R, 'white', 'black', 1);
			var logf, angle, x,y;
			for(let i=0; i<this.freq.length; i++) {
				logf = Math.log2(this.freq[i]/this.f0);
				angle = -Math.PI/2 + 2*Math.PI * (logf%1); // start from the top
				x = xcenter + R*Math.cos(angle);
				y = ycenter + R*Math.sin(angle);
				drawCircle(c, x, y, r, 'black', 'black', 1);
			}
		}

		this.play = async function(audioCtx) {
			const duration = 0.5; // seconds
			for(let i=0; i<this.freq.length; i++) {
				await playSineWave(audioCtx, this.freq[i], duration);
			}
		}

	}
}
