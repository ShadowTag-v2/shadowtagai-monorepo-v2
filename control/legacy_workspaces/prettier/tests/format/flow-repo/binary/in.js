// @flow

const tests = [
  // objects on RHS
  () => {
    "foo" in {};
    "foo" in { foo: null };
    0 in {};
    0 in { 0: null };
  },

  // arrays on RHS
  () => {
    "foo" in [];
    0 in [];
    "length" in [];
  },

  // primitive classes on RHS
  () => {
    "foo" in new String("bar");
    "foo" in new Number(123);
  },

  // primitives on RHS
  () => {
    "foo" in 123; // error
    "foo" in "bar"; // error
    "foo" in (void 0); // error
    "foo" in null; // error
  },

  // bogus stuff on LHS
  () => {
    null in {}; // error
    (void 0) in {}; // error
    ({}) in {}; // error
    [] in {}; // error
    false in []; // error
  },

  // in predicates
  () => {
    if ("foo" in 123) {
    } // error
    if ((!"foo") in {}) {
    } // error, !'foo' is a boolean
    if (!("foo" in {})) {
    }
  },

  // annotations on RHS
  (x: Object, y: mixed) => {
    "foo" in x; // ok
    "foo" in y; // error
  },
];
