/* must be included after plotly-setup.js and ../lib.js */
const w = 512; //image width, in pixels
const h = w;
var system;
var canvas;
var c;

var N = 64; // max 324 with initRanFrac=0.9
var L = 20; // box side (internal units)
var T = 2.0; // temperature (internal units)
var P = 0.0; // pressure (internal units)
var pi = new PairInteraction( LJenergy, LJforce );
let nbins_rdf = 100;
let npoints_sq = 100;

function setup() {
    document.getElementById("T_slider").value = T; //set correct slider position
    document.getElementById("P_slider").value = P;
    document.getElementById("L_slider").value = L;
    document.getElementById("rdf_slider").value = nbins_rdf;
    document.getElementById("sq_slider").value = npoints_sq;
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
    if( Math.floor(t/dt)%ndt_refresh_thermo == 0) {
        updateTimePlot( system.Virial(), system.MolarVolume(),system.EnergyKinetic(),system.EnergyPotential() );
        updateParametricPlot( system.MolarVolume(), system.Virial() );
    }
    if( Math.floor(t/dt)%ndt_refresh_free_energy == 0) {
      plotFreeEnergy();
    }
    /*
    if( Math.floor(t/dt)%ndt_refresh_rdf == 0) {
      system.computeRDF(nbins_rdf);
      plotRDF(system.rdf, system.L);
      system.computeSq(npoints_sq);
      plotSq(system.sq, system.L);
    }
    */
    system.update(T,P);
    system.show(c, canvas.width, canvas.height);
    t+=dt;
    
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

function changeRDF(value) {
    nbins_rdf = parseFloat(value);
    document.getElementById("rdf_label").innerHTML = nbins_rdf;
}
function changeSq(value) {
    npoints_sq = parseFloat(value);
    document.getElementById("sq_label").innerHTML = npoints_sq;
}
////////////////
setup();
draw();
