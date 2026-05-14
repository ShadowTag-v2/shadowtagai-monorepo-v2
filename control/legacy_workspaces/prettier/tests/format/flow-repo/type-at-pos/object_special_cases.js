/* @flow */

const tests = [
  () => {
    const x = {};
    Object.defineProperty(x, "foo", { value: "" });
  },
];
