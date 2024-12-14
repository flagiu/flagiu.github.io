/* must be included after plotly-setup.js and ../lib.js */
const w = 512; //image width, in pixels
const h = w;
var system;
var canvas;
var c;

var N = 42; //36; // max 324 with initRanFrac=0.9
var L = 7.0; // box side (units of sigma)
var T = 0.5; // temperature (units of eps/kB)
var P = 0.0; // pressure (units of eps/sigma^3)
var pi = new PairInteraction( LJenergy, LJforce );
let nbins_rdf = 100;
let npoints_sq = 50;
let ndt_analyze = 1000;
let ndt_every_frame = 100;
let num_pinnedRDF = 0;
let num_pinnedSq = 0;

function setup() {
    document.getElementById("T_number").value = T; //set correct slider position
    document.getElementById("P_number").value = P;
    document.getElementById("L_number").value = L;
    document.getElementById("rdf_bins_number").value = nbins_rdf;
    document.getElementById("sq_npoints_number").value = npoints_sq;
    canvas = document.getElementById("sketch-holder");
    c = canvas.getContext("2d");
    c.willReadFrequently=true;
    canvas.width = w;
    canvas.height = h;
    canvas.focus();
    system = new System(N,L,pi);
    //system.init_square();
    system.init_hex();
    system.CenterOfMass(false,false);
    //console.log(system);
    //system.show(c, canvas.width, canvas.height);
}

function draw() {
    if( Math.floor(t_idx)%ndt_refresh_thermo == 0) {
        let ekin = system.EnergyKinetic();
        let epot = system.EnergyPotential();
        let etot = ekin+epot;
        updateTimePlot( system.Virial(), system.NumDensity(),ekin,epot,etot );
        updateParametricPlot( system.NumDensity(), system.Virial() );
    }
    if( Math.floor(t_idx)%ndt_refresh_free_energy == 0) {
      plotFreeEnergy();
    }
    /*
    if( Math.floor(t_idx)%ndt_refresh_rdf == 0) {
      system.computeRDF(nbins_rdf);
      plotRDF(system.rdf, system.L);
      system.computeSq(npoints_sq);
      plotSq(system.sq, system.L);
    }
    */
    if(system.integrator != "None") {
        for(var i=0;i<ndt_every_frame;i++) {
            system.update(T,P);
            t_idx+=1;
            t=dt*t_idx;
        }
    }
    system.show(c, canvas.width, canvas.height);

    if( system.startedRDF && Math.floor(t_idx)%ndt_analyze == 0) {
        system.computeRDF(nbins_rdf);
        plotRDF(system.rdf, system.L);
    }
    if( system.startedSq && Math.floor(t_idx)%ndt_analyze == 0) {
        system.computeSq(npoints_sq);
        plotSq(system.sq, system.L);
    }
    requestAnimationFrame(draw);
}

/* Interactive functions */

function changeT(value) {
    T = parseFloat(value);
}

function changeP(value) {
    P = parseFloat(value);
}

function changeL(value) {
    L = parseFloat(value);
    if(L>system.L.x)
    {
        system.expand(L);
    }
}

function pin_RDF() {
    if(system.startedRDF) {
        num_pinnedRDF+=1;
        pinRDF(system.rdf, system.L, "pinned"+num_pinnedRDF);
    }
}
function pin_Sq() {
    if(system.startedSq) {
        num_pinnedSq+=1;
        pinSq(system.sq, system.L, "pinned"+num_pinnedSq);
    }
}

function changeRDF(value) {
    nbins_rdf = parseFloat(value);
    system.startedRDF=false;
}
function changeSq(value) {
    npoints_sq = parseFloat(value);
}
////////////////
setup();
draw();
