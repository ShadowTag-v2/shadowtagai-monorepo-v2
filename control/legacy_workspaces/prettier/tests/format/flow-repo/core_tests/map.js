// @flow

function* generator(): Iterable<[string, number]> {
  while (true) {
    yield ['foo', 123];
  }
}

const tests = [
  // good constructors
  () => {
    const w = new Map();
    const x = new Map(null);
    const y = new Map([['foo', 123]]);
    const z = new Map(generator());
    let a: Map<string, number> = new Map();
    let b: Map<string, number> = new Map([['foo', 123]]);
    let c: Map<string, number> = new Map(generator());
  },

  // bad constructors
  () => {
    const x = new Map(['foo', 123]); // error
    let y: Map<number, string> = new Map([['foo', 123]]); // error
  },

  // get()
  (x: Map<string, number>) => {
    (x.get('foo'): boolean); // error, string | void
    x.get(123); // error, wrong key type
  },
];
