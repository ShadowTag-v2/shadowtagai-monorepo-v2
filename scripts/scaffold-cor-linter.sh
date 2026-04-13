#!/usr/bin/env bash
# ==============================================================================
# COR.HYBRID LINTER SCAFFOLDING
# Sets up: ESLint plugin (cor-rules), Husky pre-commit hooks, Vulture for Python
# ==============================================================================
set -e
echo "🚀 Scaffolding Cor.Hybrid Linter & Git Hooks..."

# --- Step 1: Install NPM dev dependencies (preserves existing package.json) ---
echo "📦 Installing ESLint, Husky, lint-staged..."
npm i -D eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin husky lint-staged 2>/dev/null || {
    echo "⚠️ npm install had warnings (non-fatal). Continuing..."
}

# --- Step 2: Install Vulture via pip (no git clone required) ---
echo "🐍 Installing Vulture for Python dead-code detection..."
pip3 install vulture ruff 2>/dev/null || python3 -m pip install vulture ruff 2>/dev/null || {
    echo "⚠️ Vulture/Ruff pip install failed. Install manually: pip install vulture ruff"
}

# --- Step 3: Create Cor.Hybrid Custom ESLint Plugin ---
echo "🔧 Creating eslint-plugin-cor-rules..."
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
    "no-dynamic-imports": {
      create(context) {
        return {
          ImportExpression(node) {
            context.report({ node, message: "Dynamic import forbidden. Use static imports or next/dynamic." });
          }
        };
      }
    },
    "no-any-cast": {
      create(context) {
        return {
          TSAnyKeyword(node) {
            context.report({ node, message: "Avoid `any`. Use explicit, safe types." });
          }
        };
      }
    },
    "no-extra-trycatch": {
      create(context) {
        return {
          TryStatement(node) {
            const hasEmptyCatch = node.handler && (!node.handler.param || (node.handler.body && node.handler.body.body.length === 0));
            if (hasEmptyCatch) {
              context.report({ node, message: "Remove blanket try/catch or handle specific errors at call site." });
            }
          }
        };
      }
    },
    "no-console-log": {
      create(context) {
        return {
          CallExpression(node) {
            if (node.callee.type === 'MemberExpression' && node.callee.object.name === 'console' && node.callee.property.name === 'log') {
              context.report({ node, message: "Remove console.log before shipping. Use structured logging." });
            }
          }
        };
      }
    }
  }
};
EOF

# --- Step 4: ESLint Config ---
echo "📋 Writing .eslintrc.cjs..."
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
  ignorePatterns: ["node_modules/**", "dist/**", "build/**", ".next/**", "tools/**", "control/**", "external_sdks/**"]
};
EOF

# --- Step 5: Husky Setup ---
echo "🐶 Initializing Husky pre-commit hooks..."
npx husky init 2>/dev/null || true
mkdir -p .husky
cat << 'EOF' > .husky/pre-commit
#!/usr/bin/env sh
./scripts/dead-code-audit.sh
EOF
chmod +x .husky/pre-commit

echo "✅ Cor.Hybrid Linter and Pre-Commit Hooks Successfully Scaffolded."
