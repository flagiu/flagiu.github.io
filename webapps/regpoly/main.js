/* must be included after plotly-setup.js and ../lib.js */

const a0 = 0; // starting angle (rad)
const R = 128;
const r = 5;
const w = 2.5*R; //image width coincides with maximum R * 2
const h = w;
var N = 3;
var sys;
var canvas;
var c;

function setup() {
    document.getElementById("N_slider").value = N; //set correct slider position
    canvas = document.getElementById("sketch-holder");
    c = canvas.getContext("2d");
    //delete document.getElementById("defaultCanvas0");
    canvas.width = w;
    canvas.height = h;
    canvas.focus();
    background(51);
    //window = = browser.windows.getCurrent();

    sys = new Points(N);
    sys.generate_points(N);
    sys.show(c, canvas.width, canvas.height, R, r, a0);
}

function draw() {
    //background("white");
}

/* Interactive functions */

function changeN(value) {
    N = parseFloat(value);
    document.getElementById("N_label").innerHTML = N;
    sys.generate_points(N);
    sys.show(c, canvas.width, canvas.height, R, r, a0);
}
