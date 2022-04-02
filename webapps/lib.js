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
    var arr = new Array(length || 0)
    var l = length;
    if (arguments.length > 1) {
        var args = Array.prototype.slice.call(arguments, 1);
        while(l--) arr[length-1 - l] = createEmptyArray.apply(this, args);
    }
    return arr;
}

// creates a (multi)dimensional array with constant value
function createConstArray(value, length) { // it can receive multiple length iteratively
    var arr = new Array(length || 0)
    var l = length;
    if (arguments.length > 2) {
        var args = Array.prototype.slice.call(arguments, 2);
        while(l--) arr[length-1 - l] = createConstArray.apply(this, [value].concat(args));
    } else arr.fill(value);
    return arr;
}
