/* must be included after plotly-setup.js and ../lib.js */
const w = 256; //image width coincides with maximum L
const h = w;
var L = 128;
var q = 3;
var T = 1;
var H = 0.0;
var spins;
var canvas;
var colors;

function setup() {
    document.getElementById("q_slider").value = q;
    document.getElementById("T_slider").value = T; //set correct slider position
    document.getElementById("H_slider").value = H;
    document.getElementById("L_slider").value = L;
    canvas = createCanvas(w,h);
    canvas.parent('sketch-holder');
    background(51);
    colordict = {
	"red": color(255,0,0),
	"blue": color(0,0,255),
	"green": color(0,255,0),
	"yellow": color(225,255,0),
	"indigo": color(37,0,130),
	"black": color(0),
	"white": color(255),
	key: function(n) {
            return Object.keys(this)[n];
	},
	value: function(n) {
            return this[Object.keys(this)[n]];
	}
    };
    img = createImage(w,h);
    spins = new Potts2D(L,q,H, img);
    spins.show();
    //plotMH(T);
}

function draw() {
    background("green");
    spins.update(T,H);
    spins.show();
    t+=dt;
    Plotly.extendTraces("time-plot", {x: [[t], [t], [t]], y: [[H],[spins.m],[spins.e]]}, [0, 1, 2], nt)
    Plotly.extendTraces("parametric-plot", {x: [[H]], y: [[spins.m]]}, [0], nt)
}

/* Interactive functions */
function changeq(value) {
    q = parseFloat(value);
    document.getElementById("q_label").innerHTML = q;
    spins = new Potts2D(L,q,H, img);
}

function changeT(value) {
    T = parseFloat(value);
    document.getElementById("T_label").innerHTML = T;
    //plotMH(T);
}

function changeH(value) {
    H = parseFloat(value);
    document.getElementById("H_label").innerHTML = H;
}

function changeL(value) {
    L = parseFloat(value)
    document.getElementById("L_label").innerHTML = L
    spins.resize(L);
}
