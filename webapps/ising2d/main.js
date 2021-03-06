/* must be included after plotly-setup.js and ../lib.js */
const w = 256; //image width coincides with maximum L
const h = w;
var L = 128;
var T = 2.269;
var H = 0.0;
var m0 = 0.0; //initial magnetization
var spins;
var canvas;
var colors;

function setup() {
    document.getElementById("T_slider").value = T; //set correct slider position
    document.getElementById("H_slider").value = H;
    document.getElementById("L_slider").value = L;
    canvas = createCanvas(w,h);
    canvas.parent('sketch-holder');
    background(51);
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
    spins = new Ising2D(L,m0,H, img, "yellow","indigo","black");
    spins.show();
    plotMH(T);
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

function changeT(value) {
    T = parseFloat(value);
    document.getElementById("T_label").innerHTML = T;
    plotMH(T);
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
