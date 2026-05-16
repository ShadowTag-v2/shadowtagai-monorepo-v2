const foo = "";

export {
  foo, // comment
};

const bar = "";

export {
  // comment
  bar,
};

const fooo = "";
const barr = "";

export {
  barr, // comment
  fooo, // comment
};

const foooo = "";
const barrr = "";

export {
  // comment
  barrr as baz,
  foooo,
} from "foo";

const fooooo = "";
const barrrr = "";

export {
  // comment
  barrrr as bazz,
  fooooo,
};
