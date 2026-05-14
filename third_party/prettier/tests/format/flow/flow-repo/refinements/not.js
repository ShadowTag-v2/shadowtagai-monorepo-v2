/* @flow */

function foo(x: ?bool) {
  if (!x) {
    x++; // should error for null, void and bool (false)
  }
}

function bar(x: ?number) {
  if (!x) {
    x[0]; // should error for null, void and number (0)
  }
}

function baz (x: ?number) {
  if (x === null || x === undefined) {
    return;
  }

  if (!x) {
    x[0]; // should error for number (0)
  }
}

class TestClass {}

const tests = [
  () => {
    var y = true;
    while (y) {
      y = !y;
    }
  },
  (x: Function) => {
    (!x: false); // ok, functions are always truthy
  },
  (x: Object) => {
    (!x: false); // ok, objects are always truthy
  },
  (x: string) => {
    (!x: false); // error, strings are not always truthy
  },
  (x: number) => {
    (!x: false); // error, numbers are not always truthy
  },
  (x: boolean) => {
    (!x: false); // error, bools are not always truthy
  },
  (x: TestClass) => {
    (!x: false); // ok, classes are always truthy
  },
];
