/* @flow */

const tests = [
  () => {
    let x: ?string = null;
    invariant(x, 'truthy only'); // error, forgot to require invariant
  },

  (invariant: Function) => {
    let x: ?string = null;
    invariant(x);
    (x: string);
  }
]
