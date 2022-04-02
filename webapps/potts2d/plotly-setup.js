/* Plotly graphics */
var nt = 500; //max length of the trace
// Time plot
var dt = 1;
var t = 0;
var trace0 = {
    x: [],
    y: [],
    mode: 'lines',
    type: 'scatter',
    name: 'H',
    line: {color: '#6accbc'}
};
var trace1 = {
    x: [],
    y: [],
    mode: 'lines',
    type: 'scatter',
    name: 'm',
    line: {color: '#ff9933'}
};
var trace2 = {
    x: [],
    y: [],
    mode: 'lines',
    type: 'scatter',
    name: 'e',
    line: {color: '#299438'}
};
var layout0 = {
  xaxis: {
    title: {
      text: 'time'
    },
  },
  yaxis: {
    title: { text: ''},
      range: [-2,1]
  },
    margin: {t: 15, r:5, l: 50, b:50},
    legend: {x:0, y:1.2, "orientation": "h"}
}
Plotly.newPlot("time-plot", [trace0, trace1, trace2], layout0, {responsive: true, displayModeBar: false});

// Parametric plot m vs. H

var trace3 = {
    x: [],
    y: [],
    mode: 'lines',
    type: 'scatter',
    name: 'data',
    line: {color: 'rgba(255,0,0,0.5)'}
}
/*
var trace4 = { 
    x: [],
    y: [],
    mode: 'lines',
    type: 'scatter',
    name: 'nMF',
    line: {color: '#0000ff'}
};
*/
var layout1 = {
    xaxis: {
	title: { text: 'H'},
	range: [-1.1,1.1]
    },
    yaxis: {
	title: { text: 'm'},
	range: [-0.1,1.1]
    },
    margin: {t: 15, r:5, l: 50, b:50},
    legend: {x:0, y:1.2, "orientation": "h"}
}
Plotly.newPlot("parametric-plot", [trace3], layout1, {responsive: true, displayModeBar: false});

/* Plotting functions */
/*
function plotMH(T) { // plot h=T*atanh(m)-m
     // x is H, y is m !
    let ymin = -0.999;
    let ymax = 0.999;
    let Ny = 100;
    let dy = (ymax-ymin)/(Ny-1);
    data_update = {x:[[]], y:[[]]};
    //trace4.x = [];
    //trace4.y = [];
    for (i=0;i<Ny;i++) {
	let y = ymin+i*dy;
	data_update.y[0].push(y);
	data_update.x[0].push(T*Math.atanh(y)-4*y);
    }
    Plotly.update("parametric-plot", data_update, {}, [1]);
}
*/
