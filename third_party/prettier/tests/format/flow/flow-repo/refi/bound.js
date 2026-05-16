// refinements of bound vars (closed-over locals)
// should have the same lifetimes as heap objects.

var x :
?string = "xxx"

var tests = [
  () => {
    var y : string = x; // not ok
  },

  () => {
    if (x != null) {
      var y : string = x; // ok
    }
  },

  () => {
    if (x == null) {
    } else {
      var y : string = x; // ok
    }
  },

  () => {
    if (x == null) return;
    var y : string = x; // ok
  },

  () => {
    if (!(x != null)) {
    } else {
      var y : string = x; // ok
    }
  },

  /* TODO we actually allow this currently; fix
  // requires further remedial work in Env
  function() {
    if (x != null) {
      alert("");
      var y : string = x;  // not ok
    }
  },
  */
  () => {
    if (x != null) {
    }
    var y : string = x; // not ok
  },

  () => {
    if (x != null) {
    } else {
      var y : string = x; // not ok
    }
  },

  () => {
    var y : string = x != null ? x : ""; // ok
  },

  () => {
    var y : string = x || ""; // ok
  },
];
