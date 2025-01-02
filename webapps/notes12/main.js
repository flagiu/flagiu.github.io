/* must be included after plotly-setup.js and ../lib.js */

const R = 128;
const r = 5;
const w = 2.5*R; //image width coincides with maximum R * 2
const h = w;
const f0 = 440; // Hertz
const q = 3.; //Math.pow(2,1./12.);
var sys;
var canvas;
var c;
// create web audio api context
var audioCtx;

function setup() {
    canvas = document.getElementById("sketch-holder");
    c = canvas.getContext("2d");
    canvas.width = w;
    canvas.height = h;
    canvas.focus();
    background(51);
    //window = = browser.windows.getCurrent();

    sys = new Notes(f0, q);
    sys.show(c, canvas.width, canvas.height, R, r);
}

function draw() {
    //background("white");
}

/* Interactive functions */

function changeN(value) {
    let N = parseFloat(value);
    document.getElementById("N_label").innerHTML = N;
    sys.generate_notes(N);
    sys.show(c, canvas.width, canvas.height, R, r);
}

function playNotes() {
    audioCtx = new(window.AudioContext || window.webkitAudioContext)();
    sys.play(audioCtx);
}