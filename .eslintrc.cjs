/** @type {import('eslint').Linter.Config} */
module.exports = {
  root: true,
  parser: "@typescript-eslint/parser",
  plugins: ["@typescript-eslint", "gpt5rules"],
  extends: ["eslint:recommended", "plugin:@typescript-eslint/recommended"],
  env: { node: true, es2022: true, browser: true },
  rules: {
    "gpt5rules/no-dynamic-imports": "error",
    "gpt5rules/no-any-cast": "error",
    "gpt5rules/no-extra-trycatch": "warn",
    "@typescript-eslint/no-explicit-any": "off", // our custom rule handles this with a clearer message
  },
  overrides: [
    { files: ["**/*.js"], parser: null }, // allow JS files without TS parser if needed
  ],
  ignorePatterns: ["node_modules/**", "dist/**", "build/**"],
};
