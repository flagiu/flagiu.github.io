/* must be included after plotly-setup.js and ../lib.js */

const R = 128;
const r = 5;
const w = 2.5*R; //image width coincides with maximum R * 2
const h = w;
var f0 = 440; // Hertz
var q = 3.; //Math.pow(2,1./12.);
var N = 1;
var sys;
var canvas;
var c;
// create web audio api context
var audioCtx;

function setup() {
    document.getElementById("q_number").value = q; //set correct slider position
    document.getElementById("N_slider").value = N; //set correct slider position
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
function change_q(value) {
    q = parseFloat(value);
    sys.q = q;
    sys.generate_notes(N);
    sys.show(c, canvas.width, canvas.height, R, r);
}

function changeN(value) {
    N = parseFloat(value);
    document.getElementById("N_label").innerHTML = N;
    sys.generate_notes(N);
    sys.show(c, canvas.width, canvas.height, R, r);
}

function playNotes() {
    audioCtx = new AudioContext();//new(window.AudioContext || window.webkitAudioContext)();
    sys.play(audioCtx);
}