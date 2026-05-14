import syntaxImportAssertions from "@babel/plugin-syntax-import-assertions" with {
  BABEL_8_BREAKING: "false",
  IS_STANDALONE: "false",
  USE_ESM: "true",
};

import a1 from "foo" with { BABEL_8_BREAKING: "false", IS_STANDALONE: "false", USE_ESM: "true" };
import a2 from "foo" with { BABEL_8_BREAKING: "false", IS_STANDALONE: "false", USE_ESM: "true" };
import a3 from "foo" with { BABEL_8_BREAKING: "false" };
import a4 from "foo" with { BABEL_8_BREAKING: "false" };
