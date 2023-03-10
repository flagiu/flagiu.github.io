/* must be included after plotly-setup.js and ../lib.js */
const w = 512; //image width, in pixels
const h = w;
var system;
var canvas;
var c;

var N = 64;
var L = 20; // box side (internal units)
var T = 2.0; // temperature (internal units)
var P = 0.0; // pressure (internal units)
var pi = new PairInteraction( LJenergy, LJforce );

function setup() {
    document.getElementById("T_slider").value = T; //set correct slider position
    document.getElementById("P_slider").value = P;
    document.getElementById("L_slider").value = L;
    canvas = document.getElementById("sketch-holder");
    c = canvas.getContext("2d");
    c.willReadFrequently=true;
    canvas.width = w;
    canvas.height = h;
    canvas.focus();
    system = new System(N,L,pi);
    system.init_square();
    //console.log(system);
    //system.show(c, canvas.width, canvas.height);
}

function draw() {
    system.update(T,P);
    system.show(c, canvas.width, canvas.height);
    t+=dt;
    if( Math.floor(t/dt)%ndt_refresh_thermo == 0) {
        Plotly.extendTraces("time-plot", {x: [[t], [t], [t], [t]], y: [[system.Virial()], [system.MolarVolume()],[system.EnergyKinetic()],[system.EnergyPotential()]]}, [0, 1, 2, 3], nt);
        Plotly.extendTraces("parametric-plot", {x: [[system.MolarVolume()]], y: [[system.Virial()]]}, [0], nt);
    }
    if( (t/dt)%ndt_refresh_free_energy == 0) {
      plotFreeEnergy();
    }
    requestAnimationFrame(draw);
}

/* Interactive functions */

function changeT(value) {
    T = parseFloat(value);
    document.getElementById("T_label").innerHTML = T;
}

function changeP(value) {
    P = parseFloat(value);
    document.getElementById("P_label").innerHTML = P;
}

function changeL(value) {
    L = parseFloat(value);
    document.getElementById("L_label").innerHTML = L;
    if(L>system.L.x)
    {
        system.expand(L);
    }
}

////////////////
setup();
draw();
