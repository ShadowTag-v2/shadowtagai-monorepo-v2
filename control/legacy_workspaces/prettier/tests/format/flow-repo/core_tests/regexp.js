// @flow

const tests = [
  // constructor
  () => {
    /foo/;
    new RegExp(/foo/);
    /foo/i;
    /foo/gi;
    new RegExp(/foo/, "i"); // invalid in ES5, valid in ES6
    new RegExp(/foo/g, "i"); // invalid in ES5, valid in ES6
  },

  // called as a function (equivalent to the constructor per ES6 21.2.3)
  () => {
    /foo/;
    RegExp(/foo/);
    /foo/i;
    /foo/gi;
    RegExp(/foo/, "i"); // invalid in ES5, valid in ES6
    RegExp(/foo/g, "i"); // invalid in ES5, valid in ES6
  },

  // invalid flags
  () => {
    /foo/z; // error
    /foo/z; // error
  },
];
