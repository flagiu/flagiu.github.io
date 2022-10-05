/* must be included after plotly-setup.js and ../lib.js */
const w = 512; //image width coincides with maximum L
const h = w;
var maxmod=2; //max z modullus
var maxiter=100; //max iterations
var n=2; //exponent of the recursion law
var L=128; // resolution per side
const xmin = -2.; // questi si potrebbero mettere come sliders...
const xmax =  1.;
const ymin = -1.;
const ymax =  1.;
var dx,dy;
var canvas;
var colors;
var img;

function mandelbrot() {
    img.loadPixels();
    let scale = int(w/L);
    var x,y;
    dx = (xmax-xmin)/L;
    dy = (ymax-ymin)/L;
    for (let i = 0; i < img.width; i++) {
	for (let j = 0; j < img.height; j++) {
	    if ( i%scale==0 && j%scale==0 )
	    {
		x = xmin + (i/scale)*dx;
		y = ymin + ((img.width - j)/scale)*dy;
		if( check_rule(x,y) )
		    img.set(i, j, colors['black']);
		else
		    img.set(i, j, colors['white']);
	    } else
		    img.set(i, j, colors['white']); //extra points
	}
    }
    img.updatePixels();
    image(img, 0,0);//w/2-this.L/2, h/2-this.L/2);
}

function check_rule(x,y) {
    const c = math.complex(x,y);
    let z = math.complex(0.,0.);
    let iter=0;
    let zmod=math.abs(z);
    while(zmod<maxmod && iter<maxiter){
	z = rule(z,c,n);
	zmod = math.abs(z);
	iter++;
    }
    if(zmod<maxmod && iter>=maxiter) return true;
    else return false;
}

function rule(z,c,n) { // z^n + c
    let znew = math.complex(1.,0.);
    for(let i=0;i<n;i++){
	znew = math.multiply(znew,z);
    }
    znew = math.add(znew,c);
    return znew;
}

function setup() {
    document.getElementById("maxmod_slider").value = maxmod; //set correct slider position
    document.getElementById("maxiter_slider").value = maxiter;
    document.getElementById("n_slider").value = n;
    document.getElementById("L_slider").value = L;
    canvas = createCanvas(w,h);
    canvas.parent('sketch-holder');
    colors = {
	"yellow": color(225,255,0),
	"purple": color(127,0,255),
	"indigo":color(75,0,130),
	"red": color(255,0,0),
	"blue": color(0,0,255),
	"black": color(0),
	"white": color(255),
	"green": color(0,255,0)
    };
    img = createImage(w,h);
    mandelbrot();
}

/* Interactive functions */

function change_maxmod(value) {
    maxmod = parseFloat(value);
    document.getElementById("maxmod_label").innerHTML = maxmod;
    mandelbrot();
}

function change_maxiter(value) {
    maxiter = parseFloat(value);
    document.getElementById("maxiter_label").innerHTML = maxiter;
    mandelbrot();
}

function change_n(value) {
    n = parseFloat(value);
    document.getElementById("n_label").innerHTML = n;
    mandelbrot();
}

function changeL(value) {
    L = parseFloat(value)
    document.getElementById("L_label").innerHTML = L;
    mandelbrot();
}
