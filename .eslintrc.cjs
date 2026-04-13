/** @type {import('eslint').Linter.Config} */
module.exports = {
  root: true,
  parser: "@typescript-eslint/parser",
  plugins: ["@typescript-eslint", "cor-rules"],
  extends: ["eslint:recommended", "plugin:@typescript-eslint/recommended"],
  env: { node: true, es2022: true, browser: true },
  rules: {
    "cor-rules/no-dynamic-imports": "error",
    "cor-rules/no-any-cast": "error",
    "cor-rules/no-extra-trycatch": "warn",
    "cor-rules/no-console-log": "warn",
    "@typescript-eslint/no-explicit-any": "off"
  },
  ignorePatterns: ["node_modules/**", "dist/**", "build/**", ".next/**", "tools/**", "control/**", "external_sdks/**"]
};
