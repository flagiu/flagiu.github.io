/* Plotly graphics */
var nt = 500; //max length of the trace
var ndt_refresh_hist = 50

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
    name: 'm1',
    line: {color: '#ff9933'}
};
var trace2 = {
    x: [],
    y: [],
    mode: 'lines',
    type: 'scatter',
    name: 'm2',
    line: {color: '#ff9933'}
};
var trace3 = {
    x: [],
    y: [],
    mode: 'lines',
    type: 'scatter',
    name: 'e1',
    line: {color: '#299438'}
};
var trace4 = {
    x: [],
    y: [],
    mode: 'lines',
    type: 'scatter',
    name: 'e2',
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
Plotly.newPlot("time-plot1", [trace0, trace1, trace2, trace3, trace4], layout0, {responsive: true, displayModeBar: false});


// Time plot for overlap q

var trace5 = {
    x: [],
    y: [],
    mode: 'lines',
    type: 'scatter',
    name: 'q',
    line: {color: '#1afca1'}
};

var layout1 = {
  xaxis: {
    title: {
      text: 'time'
    },
  },
  yaxis: {
    title: { text: 'q'},
      range: [-2,2]
  },
    margin: {t: 15, r:5, l: 50, b:50},
    //legend: {x:0, y:1.2, "orientation": "h"}
}
Plotly.newPlot("time-plot2", [trace5], layout1, {responsive: true, displayModeBar: false});


// Histogram of overlap q

var trace6 = {
    x: [],
    y: [],
    mode: 'lines+markers',
    type: 'scatter',
    name: 'P(q)',
    line: {color: '#ff9933'}
}
var layout2 = {
    xaxis: {
	title: { text: 'q'},
	range: [-1.1,1.1]
    },
    yaxis: {
	title: { text: 'P(q)'},
	range: [0.0, 0.5]
    },
    margin: {t: 15, r:5, l: 50, b:50},
    //legend: {x:0, y:1.2, "orientation": "h"}
}

Plotly.newPlot("overlap-plot", [trace6], layout2, {responsive: true, displayModeBar: false});

function plotOverlap(N) { // N determines the resolution on x axis
    const xmin = -1.0;
    //const xmax =  1.0;
    const Nx = Math.min(N,200);
    const dx = 2/Nx;
    let xdata = new Float32Array(Nx+1);
    let ydata = new Float32Array(Nx+1);
    for (let i=0;i<=Nx;i++) {
        xdata[i] = xmin + dx*i;
        ydata[i] = 0.0;
    }
    for (q of trace5.y) {
        let i = Math.floor( Nx*0.5*(1+q) ); // get index
        ydata[i] += 1.0 /trace5.y.length; // *dx;
        //console.log(i,ydata[i])
    }
    /*
    for (let i=0;i<=Nx;i++) {
        if(ydata[i]>0) ydata[i] = -T/N*Math.log(ydata[i]);
        else ydata[i] = gmax+0.1; // "infinity"
    }
    */
    data_update = {x: xdata, y: ydata};
    Plotly.update("overlap-plot", data_update, {});
}
