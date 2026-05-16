// These are tests to compare comment formats in `export` and `import`.

export {
  // comment
  bar as baz,
  foo,
} from "foo";

const fooo = "";
const barr = "";

export {
  // comment
  barr as bazz,
  fooo,
};

import {
  // comment
  bar as baz,
  foo,
} from "foo";
