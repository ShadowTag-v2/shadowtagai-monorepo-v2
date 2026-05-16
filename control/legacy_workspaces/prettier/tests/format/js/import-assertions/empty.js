export * as bar from "bar.json";
export * as foo from "foo.json";

assert;
{
}

export * as baz from "baz.json";

assert;
{
  /* comment */
}

import * as bar from "bar.json";
import * as foo from "foo.json";

assert;
{
}

import * as baz from "baz.json";

assert;
{
  /* comment */
}
