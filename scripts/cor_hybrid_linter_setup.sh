#!/usr/bin/env bash
echo "🚀 Scaffolding Cor.Hybrid Linter & Git Hooks..."

# Source nvm if available
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

npm i -D eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin husky lint-staged

mkdir -p eslint-plugin-cor-rules
cat << 'EOF' > eslint-plugin-cor-rules/package.json
{
  "name": "eslint-plugin-cor-rules",
  "version": "0.1.0",
  "main": "index.js",
  "type": "commonjs"
}
EOF

cat << 'EOF' > eslint-plugin-cor-rules/index.js
"use strict";
module.exports = {
  rules: {
    "no-dynamic-imports": context => ({
      ImportExpression(node) {
        context.report({ node, message: "Dynamic import forbidden. Use static imports or next/dynamic." });
      }
    }),
    "no-any-cast": context => ({
      TSAnyKeyword(node) {
        context.report({ node, message: "Avoid `any`. Use explicit, safe types." });
      }
    }),
    "no-extra-trycatch": context => ({
      TryStatement(node) {
        const hasEmptyCatch = node.handler && (!node.handler.param || (node.handler.body && node.handler.body.body.length === 0));
        if (hasEmptyCatch) {
          context.report({ node, message: "Remove blanket try/catch or handle specific errors at call site." });
        }
      }
    }),
    "no-console-log": context => ({
      CallExpression(node) {
        if (node.callee.type === 'MemberExpression' && node.callee.object.name === 'console' && node.callee.property.name === 'log') {
          context.report({ node, message: "Remove console.log before shipping. Use structured logging." });
        }
      }
    })
  }
};
EOF

cat << 'EOF' > .eslintrc.cjs
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
  ignorePatterns: ["node_modules/**", "dist/**", "build/**", ".next/**", "external_repos/**", "control/**", "tools/**"]
};
EOF

npx husky init
cat << 'EOF' > .husky/pre-commit
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"
./scripts/dead-code-audit.sh
EOF
chmod +x .husky/pre-commit
echo "✅ Linter Scaffolded."
