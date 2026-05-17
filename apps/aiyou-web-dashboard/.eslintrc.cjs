/** @type {import('eslint').Linter.Config} */
module.exports = {
  root: true,
  parser: "@typescript-eslint/parser",
  plugins: ["@typescript-eslint", "vibeshield"],
  extends: ["eslint:recommended", "plugin:@typescript-eslint/recommended"],
  env: { node: true, es2022: true, browser: true },
  rules: {
    "vibeshield/no-dynamic-imports": "error",
    "vibeshield/no-any-cast": "error",
    "vibeshield/no-extra-trycatch": "warn",
    "@typescript-eslint/no-explicit-any": "off",
  },
  overrides: [{ files: ["**/*.js"], parser: null }],
  ignorePatterns: ["node_modules/**", "dist/**", "build/**"],
};
