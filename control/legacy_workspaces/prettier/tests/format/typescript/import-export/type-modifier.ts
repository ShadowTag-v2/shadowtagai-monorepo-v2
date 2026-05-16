export type { foo } from "bar";
export type { B as C } from "./a";
export type { A as B, foo, SomeThing };

import type foo from "bar";
import type { bar, foo as bar, foo } from "baz";
import type * as foo from "./bar";
// this should be treated as a normal import statement
import type from "./foo";
import type { SomeThing } from "./some-module.js";

import type foo, { bar } from 'bar';
