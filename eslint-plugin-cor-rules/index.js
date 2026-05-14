"use strict";

module.exports = {
  rules: {
    "no-dynamic-imports": (context) => ({
      ImportExpression(node) {
        context.report({
          node,
          message:
            "SEC-DEBT: Dynamic import forbidden. Use static imports. (Cor.Rule: no-dynamic-imports)",
        });
      },
    }),
    "no-any-cast": (context) => ({
      TSAnyKeyword(node) {
        context.report({
          node,
          message: "Avoid `any`. Use explicit typed schemas. (Cor.Rule: no-any-cast)",
        });
      },
    }),
    "no-extra-trycatch": (context) => ({
      TryStatement(node) {
        const hasEmptyCatch =
          node.handler && node.handler.body && node.handler.body.body.length === 0;
        if (hasEmptyCatch) {
          context.report({
            node,
            message:
              "Empty catch swallows errors. Handle specific errors or bubble up. (Cor.Rule: no-extra-trycatch)",
          });
        }
      },
    }),
    "no-console-in-client": (context) => ({
      CallExpression(node) {
        if (
          node.callee.type === "MemberExpression" &&
          node.callee.object.name === "console" &&
          ["log", "debug", "info"].includes(node.callee.property.name)
        ) {
          context.report({
            node,
            message: "Remove console.log before shipping. Use structured logging. (Cor.Rule 11)",
          });
        }
      },
    }),
  },
};
