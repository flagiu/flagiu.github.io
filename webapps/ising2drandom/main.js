/* must be included after plotly-setup.js and ../lib.js */
const w = 256; //image width coincides with maximum L
const h = w;
const dh = 5; // spacing between the two systems
var L = 128;
var T = 2.269;
var H = 0.0;
var m0 = 0.0; //initial magnetization
var J0 = 0.0; //average coupling +-1
var q; // overlap
var system1, system2;
var colors;
var canvas1, canvas2;
var c1, c2;

function setup() {
    document.getElementById("T_slider").value = T; //set correct slider position
    document.getElementById("H_slider").value = H;
    document.getElementById("L_slider").value = L;
    canvas1 = document.getElementById("sketch-holder1");
    c1 = canvas1.getContext("2d");
    c1.willReadFrequently=true;
    canvas1.width = w;
    canvas1.height = h;
    canvas1.focus();

    canvas2 = document.getElementById("sketch-holder2");
    c2 = canvas2.getContext("2d");
    c2.willReadFrequently=true;
    canvas2.width = w;
    canvas2.height = h;
    canvas2.focus();
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
    system1 = new Ising2D(L,m0,H);
    system2 = new Ising2D(L,m0,H);
    system2.copy_couplings(system1);
    //system.show();
}

function draw() {
    system1.update(T,H);
    system2.update(T,H);
    q = system1.overlap(system2);
    system1.show(c1, 0, 0, w, h);
    system2.show(c2, 0, 0, w, h);
    t+=dt;
    Plotly.extendTraces("time-plot1", {x: [[t], [t], [t], [t], [t]], y: [[H],[system1.m],[system2.m],[system1.e],[system2.e]]}, [0, 1, 2, 3, 4], nt);
    Plotly.extendTraces("time-plot2", {x: [[t]], y: [[q]]}, [0], nt);
    if( (t/dt)%ndt_refresh_hist == 0) {
      plotOverlap(system1.N);
    }
    requestAnimationFrame(draw);
}

/* Interactive functions */

function changeT(value) {
    T = parseFloat(value);
    document.getElementById("T_label").innerHTML = T;
}

function changeH(value) {
    H = parseFloat(value);
    document.getElementById("H_label").innerHTML = H;
}

function changeL(value) {
    L = parseFloat(value);
    document.getElementById("L_label").innerHTML = L;
    system1.resize(L);
    system2.resize(L);
}

////////////////
setup();
draw();
