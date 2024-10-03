/* must be included after plotly-setup.js and ../lib.js */
const w = 512; //image width coincides with maximum L
const h = w;
var L = 128;
var rho = 0.4;
var sys;
var canvas;
var colors;

function setup() {
    document.getElementById("N_slider").value = rho; //set correct slider position
    document.getElementById("L_slider").value = L;
    setAttributes('willReadFrequently', true);
    canvas = createCanvas(w,h)
    //console.log(this.canvas.drawingContext.getContextAttributes()); // https://stackoverflow.com/questions/75489567/how-to-set-canvas-attributes-from-p5-js
    canvas.parent('sketch-holder');
    background(51);

    img = createImage(w,h);
    sys = new LGCA(L, rho, img);
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
