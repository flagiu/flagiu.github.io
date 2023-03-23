/* must be included after plotly-setup.js and ../lib.js */

var system;
var T = 1.0;
var eta = 1.0;
var k = 1.0;
var mass = 1.0;
var x0 = 0.0;
var v0 = 1.0;

function setup() {
    document.getElementById("dt_slider").value = dt;
    document.getElementById("T_slider").value = T; //set correct slider position
    document.getElementById("eta_slider").value = eta;
    document.getElementById("k_slider").value = k;
    document.getElementById("m_slider").value = mass;
    document.getElementById("x0_slider").value = x0;
    document.getElementById("v0_slider").value = v0;
    system = new Particle1D(1.0, 1.0, mass, x0, v0);
    plotEnergy(T,k);
}

function draw() {
    if( Math.floor(t/dt)%ndt_refresh_plot == 0) {
        updateTimePlot( system.x, system.v );
        updateParametricPlot( system.x, system.v );
    }
    plotParticle(T,k,system.x);
    system.update(dt, T,eta,k);
    t+=dt;
    
    requestAnimationFrame(draw);
}

/* Interactive functions */

function change_dt(value) {
    dt = parseFloat(value);
    document.getElementById("dt_label").innerHTML = dt;
}
function changeT(value) {
    T = parseFloat(value);
    document.getElementById("T_label").innerHTML = T;
    plotEnergy(T,k);
}
function change_eta(value) {
    eta = parseFloat(value);
    document.getElementById("eta_label").innerHTML = eta;
}
function change_k(value) {
    k = parseFloat(value);
    document.getElementById("k_label").innerHTML = k;
    plotEnergy(T,k);
}
function change_m(value) {
    mass = parseFloat(value);
    document.getElementById("m_label").innerHTML = mass;
    system.m = mass;
}
function change_x0(value) {
    x0 = parseFloat(value);
    document.getElementById("x0_label").innerHTML = x0;
}
function change_v0(value) {
    v0 = parseFloat(value);
    document.getElementById("v0_label").innerHTML = v0;
}
function restart() {
    system.restart(x0,v0);
    trace1.x = [], trace1.y = [];
    trace2.x = [], trace2.y = [];
    trace3.x = [], trace3.y = [];
}


////////////////
setup();
draw();
