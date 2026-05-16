// @flow

const tests = [
  // global
  () => {
    (mergeInto()); // error, unknown global
  },

  // annotation
  (mergeInto: $Facebookism$MergeInto) => {
    const result = {};
    result.baz = false;
    (mergeInto(result, { foo: 'a' }, { bar: 123 }): void);
    (result: { foo: string, bar: number, baz: boolean });
  },

  // module from lib
  () => {
    const mergeInto = require('mergeInto');
    let result: { foo?: string, bar?: number, baz: boolean } = { baz: false };
    (mergeInto(result, { foo: 'a' }, { bar: 123 }): void);
  },

  // too few args
  (mergeInto: $Facebookism$MergeInto) => {
    mergeInto();
  },

  // passed as a function
  (mergeInto: $Facebookism$MergeInto) => {
    function x(cb: Function) {}
    x(mergeInto);
  }
];
