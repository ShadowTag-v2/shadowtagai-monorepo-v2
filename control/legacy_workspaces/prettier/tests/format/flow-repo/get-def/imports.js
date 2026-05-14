// @flow

import thing from "./helpers/exports_default.js";

thing;

import { bar as baz, foo } from "./helpers/exports_named.js";

foo;
baz;

import * as things from "./helpers/exports_named.js";

things;
