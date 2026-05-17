"use strict";

module.exports = {
  rules: {
    "no-dynamic-imports": (context) => ({
      ImportExpression(node) {
        context.report({ node, message: "Dynamic import forbidden. Use static imports." });
      },
    }),
    "no-any-cast": (context) => ({
      TSAnyKeyword(node) {
        context.report({ node, message: "Avoid `any`. Use explicit, safe types." });
      },
    }),
    "no-extra-trycatch": (context) => ({
      TryStatement(node) {
        // Lightweight heuristic: flag blanket try/catch without specific handling
        const hasEmptyCatch =
          node.handler &&
          (!node.handler.param || (node.handler.body && node.handler.body.body.length === 0));
        if (hasEmptyCatch) {
          context.report({
            node,
            message: "Remove unnecessary try/catch or handle specific errors at the call site.",
          });
        }
      },
    }),
  },
};
