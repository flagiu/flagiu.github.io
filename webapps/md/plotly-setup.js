/* Plotly graphics */
var nt = 500; //max length of the trace
// Time plot
var dt = 0.001; // internal units
var t = 0;
var ndt_refresh_thermo = 50
var ndt_refresh_free_energy = 50
var gmax = 1.0
var trace0 = {
    x: [],
    y: [],
    mode: 'lines',
    type: 'scatter',
    name: 'P',
    line: {color: '#6accbc'}
};
var trace1 = {
    x: [],
    y: [],
    mode: 'lines',
    type: 'scatter',
    name: 'v',
    line: {color: '#ff9933'}
};
var trace2 = {
    x: [],
    y: [],
    mode: 'lines',
    type: 'scatter',
    name: 'ene_kin',
    line: {color: '#299438'}
};
var trace3 = {
    x: [],
    y: [],
    mode: 'lines',
    type: 'scatter',
    name: 'ene_pot',
    line: {color: '#916013'}
};
var layout0 = {
  xaxis: {
    title: {
      text: 'time'
    },
  },
  yaxis: {
    title: { text: ''},
      range: [-5,5]
  },
    margin: {t: 15, r:5, l: 50, b:50},
    legend: {x:0, y:1.2, "orientation": "h"}
}
Plotly.newPlot("time-plot", [trace0, trace1, trace2, trace3], layout0, {responsive: true, displayModeBar: false});

// Parametric plot v vs. P

var trace4 = {
    x: [],
    y: [],
    mode: 'lines',
    type: 'scatter',
    name: 'data',
    line: {color: '#ff0000'}
}
var layout1 = {
    xaxis: {
	title: { text: 'v'},
	range: [0.0,10.0]
    },
    yaxis: {
	title: { text: 'P'},
	range: [-1.1,1.1]
    },
    margin: {t: 15, r:5, l: 50, b:50},
    legend: {x:0, y:1.2, "orientation": "h"}
}
Plotly.newPlot("parametric-plot", [trace4], layout1, {responsive: true, displayModeBar: false});

// Helmoltz/Gibbs free energy (histogram of V/P)

var trace5 = {
    x: [],
    y: [],
    mode: 'lines+markers',
    type: 'scatter',
    name: 'Prob(v|P)',
    line: {color: '#ff9933'}
}
var layout2 = {
    xaxis: {
	title: { text: 'v'},
	range: [0.0,1.0]
    },
    yaxis: {
	title: { text: 'Normalized counts'},
	range: [0.0, 1.0]
    },
    margin: {t: 15, r:5, l: 50, b:50},
    legend: {x:0, y:1.2, "orientation": "h"}
}
Plotly.newPlot("free-energy-plot", [trace5], layout2, {responsive: true, displayModeBar: false});

function plotFreeEnergy() { // x = molar volume
    let xmin = 0.0;
    let xmax = 1.0;
    let Nx = 300;
    let dx = (xmax-xmin)/Nx;
    let xdata = new Float32Array(Nx+1);
    let ydata = new Float32Array(Nx+1);
    for (let i=0;i<=Nx;i++) {
        xdata[i] = xmin + dx*i;
        ydata[i] = 0.0;
    }
    for (v of trace1.y) {
        let i = Math.floor( (v-xmin)*dx );
        ydata[i] += 1.0/trace1.y.length; // *dx;
    }
    data_update = {x: xdata, y: ydata};
    Plotly.update("free-energy-plot", data_update, {});
}
