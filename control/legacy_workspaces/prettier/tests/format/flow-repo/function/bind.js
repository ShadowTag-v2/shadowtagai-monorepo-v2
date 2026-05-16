// @flow

const tests = [
  (x: (a: string, b: string) => void) => {
    const y = x.bind(x, 'foo');
    y('bar'); // ok
    y(123); // error, number !~> string
  },

  // callable objects
  (x: (a: string, b: string) => void) => {
    const y = x.bind(x, 'foo');
    y('bar'); // ok
    y(123); // error, number !~> string
  },

  // non-callable objects
  (x: { a: string }) => {
    x.bind(x, 'foo'); // error
  },

  // callable objects with overridden `bind` method
  (x: {(a: string, b: string): void, bind(a: string): void}) => {
    (x.bind('foo'): void); // ok
    (x.bind(123): void); // error, number !~> string
  },

];
