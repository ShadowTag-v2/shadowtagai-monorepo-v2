// @flow

const tests = [
  (y: number) => {
    y++;
    y--;
    ++y;
    --y;
  },

  (y: string) => {
    y++; // error, we don't allow coercion here
    (y: number); // ok, y is a number now
    y++; // error, but you still can't write a number to a string
  },

  (y: string) => {
    y--; // error, we don't allow coercion here
  },

  (y: string) => {
    ++y; // error, we don't allow coercion here
  },

  (y: string) => {
    --y; // error, we don't allow coercion here
  },

  () => {
    const y = 123;
    y++; // error, can't update const
    y--; // error, can't update const
  },

  (y: any) => {
    y++; // ok
  },
];
