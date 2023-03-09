/* Plotly graphics */
var nt = 500; //max length of the trace
// Time plot
var dt = 1;
var t = 0;
var ndt_refresh_gibbs = 50
var gmax = 1.0
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
      range: [-2,2]
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
    line: {color: '#ff0000'}
}
var trace4 = { 
    x: [],
    y: [],
    mode: 'lines',
    type: 'scatter',
    name: 'MF prediction',
    line: {color: '#0000ff'}
};
var layout1 = {
    xaxis: {
	title: { text: 'H'},
	range: [-1.1,1.1]
    },
    yaxis: {
	title: { text: 'm'},
	range: [-1.1,1.1]
    },
    margin: {t: 15, r:5, l: 50, b:50},
    legend: {x:0, y:1.2, "orientation": "h"}
}
Plotly.newPlot("parametric-plot", [trace3, trace4], layout1, {responsive: true, displayModeBar: false});

// Gibbs free energy (histogram of m)

var trace5 = {
    x: [],
    y: [],
    mode: 'lines+markers',
    type: 'scatter',
    name: 'Prob(m|h)',
    line: {color: '#ff9933'}
}
var layout2 = {
    xaxis: {
	title: { text: 'm'},
	range: [-1.1,1.1]
    },
    yaxis: {
	title: { text: 'Normalized counts'},
	range: [0.0, 1.0]
    },
    margin: {t: 15, r:5, l: 50, b:50},
    legend: {x:0, y:1.2, "orientation": "h"}
}
Plotly.newPlot("gibbs-plot", [trace5], layout2, {responsive: true, displayModeBar: false});

/* Plotting functions */
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
function plotGibbs(T,N) { // plot h=T*atanh(m)-m
     // x is H, y is m !
    let xmin = -1.0;
    let xmax =  1.0;
    let Nx = Math.min(N,1024);
    let dx = 2/Nx;
    let xdata = new Float32Array(Nx+1);
    let ydata = new Float32Array(Nx+1);
    for (let i=0;i<=Nx;i++) {
        xdata[i] = xmin + dx*i;
        ydata[i] = 0.0;
    }
    for (m of trace1.y) {
        let i = Math.floor( Nx*0.5*(1+m) );
        ydata[i] += 1.0/trace1.y.length; // *dx;
    }
    /*
    for (let i=0;i<=Nx;i++) {
        if(ydata[i]>0) ydata[i] = -T/N*Math.log(ydata[i]);
        else ydata[i] = gmax+0.1; // "infinity"
    }
    */
    data_update = {x: xdata, y: ydata};
    Plotly.update("gibbs-plot", data_update, {});
}
