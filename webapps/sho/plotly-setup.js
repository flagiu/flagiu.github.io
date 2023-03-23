/* Plotly graphics */
var nt = 500; //max length of the trace
// Time plot
var dt = 0.01; // s
var t = 0;
var ndt_refresh_plot = 50;

var trace0 = {
    x: [],
    y: [],
    mode: 'lines',
    type: 'scatter',
    name: 'U/T',
    line: {color: '#0000ff'}
};
var traceParticle = {
    x: [],
    y: [],
    mode: 'markers',
    type: 'scatter',
    name: 'particle',
    marker: {color: '#ff0000', size: 10}
};
var layout0 = {
  xaxis: {
    title: {
      text: 'x / (T/k)',
      autorange: true
    },
  },
  yaxis: {
    title: { text: 'U(x) / T'},
    autorange: true
  },
    margin: {t: 15, r:5, l: 50, b:50},
    legend: {x:0, y:1.2, "orientation": "h"}
}

Plotly.newPlot("particle-plot", [traceParticle, trace0], layout0, {responsive: false, displayModeBar: false});

function Energy(k,x) {
    return 0.5*k*x*x;
}

function plotEnergy(T,k) { // U/T vs x/xGB
    let xGB = Math.sqrt(T/k);
    let xmin = -2;
    let xmax = 2;
    //let ymin = 0.0;
    //let ymax = Energy(k,xmax);
    let Nx = 100;
    let dx = (xmax-xmin)/Nx;
    let xdata = new Float32Array(Nx+1);
    let ydata = new Float32Array(Nx+1);
    for (let i=0;i<=Nx;i++) {
        xdata[i] = xmin + dx*i;
        ydata[i] = Energy(k,xdata[i]*xGB) / T;
    }
    trace0.x = xdata;
    trace0.y = ydata;
    Plotly.newPlot("particle-plot", [traceParticle, trace0], layout0, {responsive: false, displayModeBar: false});
}
function plotParticle(T,k, x) {
    let xGB = Math.sqrt(T/k);
    data_update = {x: [x/xGB], y: [Energy(k,x)/T] };
    Plotly.animate("particle-plot", {data: [data_update]}, {
       transition: { duration: 0 },
       frame: { duration: 0, redraw: false }
    });
}

var trace1 = {
    x: [],
    y: [],
    mode: 'lines+markers',
    type: 'scatter',
    name: 'x, position',
    line: {color: '#6accbc'}
};
var trace2 = {
    x: [],
    y: [],
    mode: 'lines+markers',
    type: 'scatter',
    name: 'v, speed',
    line: {color: '#ff9933'}
};
var layout1 = {
  xaxis: {
    title: {
      text: 'time'
    },
  },
  yaxis: {
    title: { text: ''},
    autorange: true
  },
    margin: {t: 15, r:5, l: 50, b:50},
    legend: {x:0, y:1.2, "orientation": "h"}
}
Plotly.newPlot("time-plot", [trace1, trace2], layout1, {responsive: true, displayModeBar: false});

function updateTimePlot(y0,y1) {
    Plotly.extendTraces("time-plot", {x: [[t], [t]], y: [[y0], [y1]]}, [0, 1], nt);
}
// Parametric plot v vs. x

var trace3 = {
    x: [],
    y: [],
    mode: 'lines+markers',
    type: 'scatter',
    name: 'data',
    line: {color: '#ff0000'}
}
var layout2 = {
    xaxis: {
	title: { text: 'x, position'},
	autorange: true
    },
    yaxis: {
	title: { text: 'v, speed'},
	autorange: true
    },
    margin: {t: 15, r:5, l: 50, b:50},
    legend: {x:0, y:1.2, "orientation": "h"}
}
Plotly.newPlot("parametric-plot", [trace3], layout2, {responsive: true, displayModeBar: false});

function updateParametricPlot(x,v) {
        Plotly.extendTraces("parametric-plot", {x: [[x]], y: [[v]]}, [0], nt);
}

