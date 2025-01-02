/* must be included after plotly-setup.js and ../lib.js */

const R = 64;
const w = 2*R; //image width coincides with maximum R * 2
const h = w;
const startingFreq = 220; // Hertz
const ratio = 2./3.;
var sys;
var canvas;
var colors;

function setup() {
    //setAttributes('willReadFrequently', true);
    canvas = createCanvas(w,h)
    canvas.parent('sketch-holder');
    background(51);

    img = createImage(w,h);
    sys = new Notes(ratio, R, Nnotes);
    sys.show();
}

function draw() {
    background("white");
    sys.update();
    sys.show();
}

/* Interactive functions */

function changeN(value) {
    rho = parseFloat(value);
    document.getElementById("N_label").innerHTML = rho;
    sys = new LGCA(L, rho, img);
}

function changeL(value) {
    L = parseFloat(value);
    document.getElementById("L_label").innerHTML = L;
    sys = new LGCA(L, rho, img);
}
