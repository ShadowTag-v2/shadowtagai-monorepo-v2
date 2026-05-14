// @flow

// Boolean (the class) tests. booleans (the literals) are not part of core.js

const tests = [
  // constructor
  () => {
    new Boolean();
    new Boolean(0);
    new Boolean(-0);
    new Boolean(null);
    new Boolean(false);
    new Boolean(NaN);
    new Boolean(undefined);
    new Boolean("");
  },

  // toString
  () => {
    true.toString();
    let x: boolean = false;
    x.toString();
    new Boolean(true).toString();
  },

  // valueOf
  () => {
    ((new Boolean(0)).valueOf()
    : boolean)
  },

  // casting
  () => {
    Boolean();
    Boolean(0);
    Boolean(-0);
    Boolean(null);
    Boolean(false);
    Boolean(NaN);
    Boolean(undefined);
    Boolean("");
  },
];
