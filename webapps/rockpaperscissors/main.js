/* must be included after plotly-setup.js and ../lib.js */
const w = 256; //image width coincides with maximum L
const h = w;
var dt0 = 0.01;
var dtfactor = 1;
var dt=dtfactor*dt0;
var L = 128;
var D = 0.25;
var A = 0.75;
var sys;
var canvas;
var colors;

function setup() {
    document.getElementById("D_slider").value = D; //set correct slider position
    document.getElementById("A_slider").value = A;
    document.getElementById("L_slider").value = L;
    document.getElementById("dt_slider").value = dtfactor;
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
    sys = new RPS(L, img, ["red","green","blue"]);
    sys.show();
}

function draw() {
    background("white");
    sys.update(D,A, dt);
    sys.show();
    //t+=dt;
    //Plotly.extendTraces("time-plot", {x: [[t], [t], [t]], y: [[H],[spins.m],[spins.e]]}, [0, 1, 2], nt)
    //Plotly.extendTraces("parametric-plot", {x: [[H]], y: [[spins.m]]}, [0], nt)
}

/* Interactive functions */

function changeD(value) {
    D = parseFloat(value);
    document.getElementById("D_label").innerHTML = D;
}

function changeA(value) {
    A = parseFloat(value);
    document.getElementById("A_label").innerHTML = A;
}

function changeL(value) {
    L = parseFloat(value);
    document.getElementById("L_label").innerHTML = L;
    sys.resize(L);
}

function changeDt(value) {
    dtfactor = parseFloat(value);
    document.getElementById("dt_label").innerHTML = dtfactor;
    dt = dtfactor*dt0;
}
