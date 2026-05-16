// @flow

const tests = [
  // global
  () => {
    (copyProperties()); // error, unknown global
  },

  // annotation
  (copyProperties: Object$Assign) => {
    const result = {};
    result.baz = false;
    (copyProperties(
      result,
      { foo: 'a' },
      { bar: 123 }
    ): foo: string, bar: number, baz: boolean );
  },

  // module from lib
  () => {
    const copyProperties = require('copyProperties');
    const x = { foo: 'a' };
    const y = { bar: 123 };
    (copyProperties({}, x, y): foo: string, bar: number );
  },

  // too few args
  (copyProperties: Object$Assign) => {
    copyProperties();
    (copyProperties({ foo: 'a' }): foo: number ); // err, num !~> string
  },

  // passed as a function
  (copyProperties: Object$Assign) => {
    function x(cb: Function) {}
    x(copyProperties);
  }
];
