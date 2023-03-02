/* must be included after plotly-setup.js and ../lib.js */
const w = 512; //image width coincides with maximum L
const h = w;
var L = 128;
var T = 2.269;
var H = 0.0;
var m0 = 0.0; //initial magnetization
var system;
var colors;
var canvas;
var c;

function setup() {
    document.getElementById("T_slider").value = T; //set correct slider position
    document.getElementById("H_slider").value = H;
    document.getElementById("L_slider").value = L;
    canvas = document.getElementById("sketch-holder");
    c = canvas.getContext("2d");
    c.willReadFrequently=true;
    canvas.width = w;
    canvas.height = h;
    canvas.focus();
    /*
    colors = {
	"yellow": color(225,255,0),
	"purple": color(127,0,255),
	"indigo":color(75,0,130),
	"red": color(255,0,0),
	"blue": color(0,0,255),
	"black": color(0),
	"white": color(255),
	"green": color(0,255,0)
    };*/
//    img = createImage(w,h);
    system = new Ising2D(L,m0,H);
    //system.show();
    plotMH(T);
}

function draw() {
    system.update(T,H);
    system.show(c, canvas.width, canvas.height);
    t+=dt;
    Plotly.extendTraces("time-plot", {x: [[t], [t], [t]], y: [[H],[system.m],[system.e]]}, [0, 1, 2], nt);
    Plotly.extendTraces("parametric-plot", {x: [[H]], y: [[system.m]]}, [0], nt);
    if( (t/dt)%ndt_refresh_gibbs == 0) {
      plotGibbs(T,system.N);
    }
    requestAnimationFrame(draw);
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
    L = parseFloat(value);
    document.getElementById("L_label").innerHTML = L;
    system.resize(L);
}

////////////////
setup();
draw();
