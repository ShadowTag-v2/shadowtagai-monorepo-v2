// @flow

class Foo {}
class Bar extends Foo {}

const tests = [
  () => {
    const x = new Bar();
    (Object.getPrototypeOf(x)
    : Foo)
  },
];
