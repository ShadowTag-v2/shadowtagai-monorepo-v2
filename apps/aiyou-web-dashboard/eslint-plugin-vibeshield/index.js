'use strict';
module.exports = {
  rules: {
    'no-dynamic-imports': (context) => ({
      ImportExpression(node) {
        context.report({
          node,
          message: '[Vibe Shield] Dynamic import forbidden. Use static imports.',
        });
      },
    }),
    'no-any-cast': (context) => ({
      TSAnyKeyword(node) {
        context.report({
          node,
          message:
            '[Vibe Shield] Avoid `any`. Use explicit, safe types to combat AI prop-drilling hallucinations.',
        });
      },
    }),
    'no-extra-trycatch': (context) => ({
      TryStatement(node) {
        // Flag empty or blanket catch blocks
        const hasEmptyCatch =
          node.handler &&
          (!node.handler.param || (node.handler.body && node.handler.body.body.length === 0));
        if (hasEmptyCatch) {
          context.report({
            node,
            message:
              '[Vibe Shield] Remove blank try/catch blocks. Handle specific errors at the caller site.',
          });
        }
      },
    }),
  },
};
