// @flow

const tests = [
  (x: Object) => {
    ({...x}: Object);
    ({...x}: void); // error, Object
  },
];
