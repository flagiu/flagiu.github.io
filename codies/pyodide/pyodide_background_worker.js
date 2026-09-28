self.importScripts("https://cdn.jsdelivr.net/pyodide/v0.26.1/full/pyodide.js");

let pyodide;

// It receives an event 'e' from the .js script contained in the .html file:
// - if e.data.type is 'init':
//    Initialize pyodide and run the script with imports and definitions
// - else if e.data.type is 'calculate':
//    Run the calculation specified by the input code

self.onmessage = async function (e) {
  if (e.data.type === "init") {
    try {
      // Prepare Pyodide
      pyodide = await loadPyodide();
      // Load the required Python packages
      for (const package of e.data.packages) {
        await pyodide.loadPackage(package);
      }
      // Run the initialization code (i.e. the full .py script)
      pyodide.runPython(e.data.initCode);

      self.postMessage({
        type: "ready"
      });
    } catch (error) {
      self.postMessage({
        type: "error",
        error: error.message,
      });
    }
  } else if (e.data.type === "calculate") {
    try {
      // e.data.code is a string of python code;
      // runPython() returns a PyProxy object, that "allows idiomatic use of a Python object from JavaScript";
      // toJs() "Converts the PyProxy into a JavaScript object as best as possible";
      // see: https://pyodide.org/en/stable/usage/type-conversions.html#type-translations-pyproxy
      console.log("running pyodide:",e.data.code);
      const result = pyodide.runPython(e.data.code).toJs();
      console.log("... pyodide done");

      self.postMessage({
        type: "result",
        data: result,
      });
    } catch (error) {
      self.postMessage({
        type: "error",
        error: error.message,
      });
    }
  }
};
