'use strict';
module.exports = {
  rules: {
    'no-dynamic-imports': {
      create(context) {
        return {
          ImportExpression(node) {
            context.report({
              node,
              message: 'Dynamic import forbidden. Use static imports or next/dynamic.',
            });
          },
        };
      },
    },
    'no-any-cast': {
      create(context) {
        return {
          TSAnyKeyword(node) {
            context.report({ node, message: 'Avoid `any`. Use explicit, safe types.' });
          },
        };
      },
    },
    'no-extra-trycatch': {
      create(context) {
        return {
          TryStatement(node) {
            const hasEmptyCatch =
              node.handler &&
              (!node.handler.param || (node.handler.body && node.handler.body.body.length === 0));
            if (hasEmptyCatch) {
              context.report({
                node,
                message: 'Remove blanket try/catch or handle specific errors at call site.',
              });
            }
          },
        };
      },
    },
    'no-console-log': {
      create(context) {
        return {
          CallExpression(node) {
            if (
              node.callee.type === 'MemberExpression' &&
              node.callee.object.name === 'console' &&
              node.callee.property.name === 'log'
            ) {
              context.report({
                node,
                message: 'Remove console.log before shipping. Use structured logging.',
              });
            }
          },
        };
      },
    },
  },
};
