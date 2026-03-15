/* Useful functions for physics */

// average of the arguments (it can also receive an array preceeded by ...)
function avg(...args) {
  let sum = 0;
  for (const item of args) {
    sum += item;
  }
  return sum / args.length;
} // example: array=[1,2,3]; avg.apply(...array);

//Kronecher's delta
function deltaKron(a,b) {
    if(a==b) return 1;
    return 0;
}

//random integer in [min,max)
function randInt(min,max) {
    return Math.floor(Math.random() * (max-min)) + min;
}

// Standard Normal variate using Box-Muller transform.
function gaussianRandom(mean=0, stdev=1) {
  const u = 1 - Math.random(); // Converting [0,1) to (0,1]
  const v = Math.random();
  const z = Math.sqrt( -2.0 * Math.log( u ) ) * Math.cos( 2.0 * Math.PI * v );
  // Transform to the desired mean and standard deviation:
  return z * stdev + mean;
}

// creates a (multi)dimensional empty array
function createEmptyArray(length) { // it can receive multiple lengths iteratively
    var arr = new Array(length || 0);
    var l = length;
    if (arguments.length > 1) {
        var args = Array.prototype.slice.call(arguments, 1);
        while(l--) arr[length-1 - l] = createEmptyArray.apply(this, args);
    }
    return arr;
}

// creates a (multi)dimensional array with constant value
function createConstArray(value, length) { // it can receive multiple length iteratively
    var arr = new Array(length || 0);
    var l = length;
    if (arguments.length > 2) {
        var args = Array.prototype.slice.call(arguments, 2);
        while(l--) arr[length-1 - l] = createConstArray.apply(this, [value].concat(args));
    } else arr.fill(value);
    return arr;
}

/* Useful functions for graphics */
function avgP5Colors(colArr, weightsArr) {
    if(colArr.length != weightsArr.length) return null;
    var r=0.0, g=0.0, b=0.0;
    for(let i=0; i< colArr.length; i++) {
	r += weightsArr[i] * colArr[i]._getRed() / colArr.length;
	g += weightsArr[i] * colArr[i]._getGreen() / colArr.length;
	b += weightsArr[i] * colArr[i]._getBlue() / colArr.length;
    }
    return color(int(r),int(g),int(b));
}

// Draw a circle on 2d context
function drawCircle(ctx, x, y, radius, fill, stroke, strokeWidth) {
  ctx.beginPath()
  ctx.arc(x, y, radius, 0, 2 * Math.PI, false)
  if (fill) {
    ctx.fillStyle = fill
    ctx.fill()
  }
  if (stroke) {
    ctx.lineWidth = strokeWidth
    ctx.strokeStyle = stroke
    ctx.stroke()
  }
}

// Draw a line on 2d context
function drawLine(ctx, x0, y0, x1, y1, stroke, strokeWidth) {
  ctx.beginPath()
  ctx.moveTo(x0,y0);
  ctx.lineTo(x1, y1)
  if (stroke) {
    ctx.lineWidth = strokeWidth
    ctx.strokeStyle = stroke
    ctx.stroke()
  }
}

function getRandomColor() {
  var letters = '0123456789ABCDEF';
  var color = '#';
  for (var i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)];
  }
  return color;
}

// Function to play a sine wave
function playSineWave(audioCtx, frequency, duration) {
  // frequency: Hertz; duration: seconds
  return new Promise((resolve) => {
    // Create an oscillator node
    const oscillator = audioCtx.createOscillator();

    // Create a gain node
    var gainNode = audioCtx.createGain();
    const fading_time = 0.015; // seconds
    const num_time_constants = 3;

    // Set the oscillator type to 'sine'
    oscillator.type = 'sine';
    // Set the frequency
    oscillator.frequency.setValueAtTime(frequency, audioCtx.currentTime);

    // Connect the oscillator to the audio context's destination (the speakers)
    oscillator.connect(audioCtx.destination);
    gainNode.connect(audioCtx.destination)
    oscillator.connect(gainNode);

    // Start the oscillator and fade in
    gainNode.gain.value = 0;
    oscillator.start();
    gainNode.gain.setTargetAtTime(0.5, audioCtx.currentTime, fading_time);

    // fade out and stop the oscillator after the specified duration
    const fadingStartTime = audioCtx.currentTime + duration - num_time_constants*fading_time;
    gainNode.gain.setTargetAtTime(0, fadingStartTime, fading_time);

    oscillator.stop(audioCtx.currentTime + duration);

    // Resolve the promise when the oscillator stops
    oscillator.onended = resolve;
  });
}

/**
 * Source: https://gist.github.com/mjackson/5311256
 * 
 * Converts an RGB color value to HSV. Conversion formula
 * adapted from http://en.wikipedia.org/wiki/HSV_color_space.
 * Assumes r, g, and b are contained in the set [0, 255] and
 * returns h, s, and v in the set [0, 1].
 *
 * @param   Number  r       The red color value
 * @param   Number  g       The green color value
 * @param   Number  b       The blue color value
 * @return  Array           The HSV representation
 */
function rgbToHsv(r, g, b) {
  r /= 255, g /= 255, b /= 255;

  var max = Math.max(r, g, b), min = Math.min(r, g, b);
  var h, s, v = max;

  var d = max - min;
  s = max == 0 ? 0 : d / max;

  if (max == min) {
    h = 0; // achromatic
  } else {
    switch (max) {
      case r: h = (g - b) / d + (g < b ? 6 : 0); break;
      case g: h = (b - r) / d + 2; break;
      case b: h = (r - g) / d + 4; break;
    }

    h /= 6;
  }

  return [ h, s, v ];
}

/**
 * Converts an HSV color value to RGB. Conversion formula
 * adapted from http://en.wikipedia.org/wiki/HSV_color_space.
 * Assumes h, s, and v are contained in the set [0, 1] and
 * returns r, g, and b in the set [0, 255].
 *
 * @param   Number  h       The hue
 * @param   Number  s       The saturation
 * @param   Number  v       The value
 * @return  Array           The RGB representation
 */
function hsvToRgb(h, s, v) {
  var r, g, b;

  var i = Math.floor(h * 6);
  var f = h * 6 - i;
  var p = v * (1 - s);
  var q = v * (1 - f * s);
  var t = v * (1 - (1 - f) * s);

  switch (i % 6) {
    case 0: r = v, g = t, b = p; break;
    case 1: r = q, g = v, b = p; break;
    case 2: r = p, g = v, b = t; break;
    case 3: r = p, g = q, b = v; break;
    case 4: r = t, g = p, b = v; break;
    case 5: r = v, g = p, b = q; break;
  }

  return [ r * 255, g * 255, b * 255 ];
}