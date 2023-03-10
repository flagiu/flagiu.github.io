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

