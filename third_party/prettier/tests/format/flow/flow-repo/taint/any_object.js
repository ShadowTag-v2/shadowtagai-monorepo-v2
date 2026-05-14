// @flow

const tests = [
  // setting a property
  (x: $Tainted<string>, y: string) => {
    let obj: Object = {};
    obj.foo = x; // error, taint ~> any
    obj[y] = x; // error, taint ~> any
  },

  // getting a property
  () => {
    let obj: Object = { foo: 'foo' };
    (obj.foo: $Tainted<string>); // ok
  },

  // calling a method
  (x: $Tainted<string>) => {
    let obj: Object = {};
    obj.foo(x); // error, taint ~> any

    const foo = obj.foo;
    foo(x); // error, taint ~> any
  },
];
