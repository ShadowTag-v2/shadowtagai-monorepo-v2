module.exports = {
  root: true,
  parser: "@typescript-eslint/parser",
  plugins: ["@typescript-eslint", "cor-rules"],
  extends: ["eslint:recommended", "plugin:@typescript-eslint/recommended"],
  env: { node: true, es2022: true, browser: true },
  rules: {
    "cor-rules/no-dynamic-imports": "error",
    "cor-rules/no-any-cast": "error",
    "cor-rules/no-empty-catch": "warn",
    "cor-rules/max-function-lines": "warn",
    "cor-rules/no-console-log": "warn",
    "@typescript-eslint/no-explicit-any": "off"
  },
  ignorePatterns: ["node_modules/**", "dist/**", "build/**", ".next/**"]
};
