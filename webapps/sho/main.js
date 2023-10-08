/* must be included after plotly-setup.js and ../lib.js */

var system;
var N = 100;
var T = 1.0;
var eta = 1.0;
var k = 1.0;
var mass = 1.0;
var x0 = 0.0;
var v0 = 1.0;

// Plotly.newPlot("time-plot", [trace1, trace2], layout1, {responsive: true, displayModeBar: false});
// Plotly.newPlot("parametric-plot", [trace3], layout2, {responsive: true, displayModeBar: false});
Plotly.newPlot("average-plot", [trace4, trace5], layout3, {responsive: true, displayModeBar: false});
Plotly.newPlot("average2-plot", [trace6, trace7], layout4, {responsive: true, displayModeBar: false});

function setup() {
    document.getElementById("dt_slider").value = dt;
    document.getElementById("T_slider").value = T; //set correct slider position
    document.getElementById("m_slider").value = mass;
    document.getElementById("eta_slider").value = eta;
    document.getElementById("k_slider").value = k;
    document.getElementById("N_slider").value = N;
    document.getElementById("x0_slider").value = x0;
    document.getElementById("v0_slider").value = v0;
    start_system();
    plotEnergy(T,k);
}

function draw() {
    if( Math.floor(t/dt)%ndt_refresh_plot == 0) {
        /*
        for(var i=0;i<N;i++) {
            let x = system.particles[i].x;
            let v = system.particles[i].v;
            updateTimePlot( x, v );
            updateParametricPlot( x, v );
        }
        */
        updateTimePlot( "average-plot", system.x, system.v );
        updateTimePlot( "average2-plot", system.dx2, system.dv2 );
    }
    plotSystem(T,k,system);
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
    start_system();
}
function change_N(value) {
    N = parseInt(value);
    document.getElementById("N_label").innerHTML = N;
    start_system();
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
    trace4.x = [], trace4.y = [];
    trace5.x = [], trace5.y = [];
    trace6.x = [], trace6.y = [];
    trace7.x = [], trace7.y = [];
}
function start_system() {
    system = new System1D();
    for(var i=0;i<N;i++) {
        system.add_particle( new Particle1D(1.0, 1.0, mass, x0, v0) );
    }
}


////////////////
setup();
draw();
