const tests = [
  (x: { x: { foo: string } }, y: { x: { bar: number } }) => {
    x = y; // 2 errors: `foo` not found in y.x; `bar` not found in x.x
  },

  (x: { foo: string }, y: { foo: number }) => {
    x = y; // 2 errors: string !~> number; number !~> string
  },

  (x: { x: { foo: string } }, y: { x: { foo: number } }) => {
    x = y; // 2 errors: string !~> number; number !~> string
  },

  (x: { +foo: string }, y: { +foo: number }) => {
    x = y; // 1 error: number !~> string
  },

  (x: { x: { +foo: string } }, y: { x: { +foo: number } }) => {
    x = y; // 2 errors: string !~> number; number !~> string
  },

  (x: { -foo: string }, y: { -foo: number }) => {
    x = y; // 1 error: string !~> number
  },

  (x: { x: { -foo: string } }, y: { x: { -foo: number } }) => {
    x = y; // 2 errors: string !~> number; number !~> string
  },
];
