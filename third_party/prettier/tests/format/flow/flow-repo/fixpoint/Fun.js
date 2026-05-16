/* @providesModule Fun */

function eq(x:number, y:number) {
  return true;
}
function sub(x:number, y:number) {
  return 0;
}
function mul(x:number, y:number) {
  return 0;
}

function fix(fold) {
  var delta = (delta) =>
    fold((x) => {
      var eta = delta(delta);
      return eta(x);
    });
  return delta(delta);
}

function mk_factorial() {
  return fix((factorial) => (n) => {
    if (eq(n, 1)) {
      return 1;
    }
    return mul(factorial(sub(n, 1)), n);
  });
}

var factorial = mk_factorial();
factorial("...");

module.exports = { fn: fix };
