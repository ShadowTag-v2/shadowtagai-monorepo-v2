// https://babeljs.io/docs/babel-plugin-proposal-do-expressions

const a =
do {
  if(x > 10) {
    'big';
  } else {
    'small';
  }
};
// is equivalent to:
const a = x > 10 ? "big" : "small";
