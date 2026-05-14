var undef_tests = [
  // NOTE: not (yet?) supporting non-strict eq test for undefined

  // expr !== undefined
  () => {
    var x :
    ?string = "xxx"
    if (x !== undefined && x !== null) {
      var y : string = x; // ok
    }
  },

  () => {
    var x :
    ?string = "xxx"
    if (undefined !== x && x !== null) {
      var y : string = x; // ok
    }
  },

  () => {
    var x : {p:?string} = {p:"xxx"};
    if (x.p !== undefined && x.p !== null) {
      var y : string = x.p; // ok
    }
  },

  () => {
    var x : {p:{q:?string}} = {p:{q:"xxx"}};
    if (x.p.q !== undefined && x.p.q !== null) {
      var y : string = x.p.q; // ok
    }
  },

  // expr === undefined
  () => {
    var x :
    ?string = "xxx"
    if (x === undefined || x === null) {
    } else {
      var y : string = x; // ok
    }
  },

  () => {
    var x : {p:?string} = {p:"xxx"};
    if (x.p === undefined || x.p === null) {
    } else {
      var y : string = x.p; // ok
    }
  },

  () => {
    var x : {p:{q:?string}} = {p:{q:"xxx"}};
    if (x.p.q === undefined || x.p.q === null) {
    } else {
      var y : string = x.p.q; // ok
    }
  },
];

// this.p op undefined
class A {
  p:
  ?string

  ensure0(): string {
    if (this.p !== undefined && this.p !== null)
      return this.p;
    else
      return "";
  }

  ensure1(): string {
    if (this.p === undefined || this.p === null)
      return "";
    else
      return this.p;
  }
}
