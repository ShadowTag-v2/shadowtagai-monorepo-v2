var A = require("./A");

class B extends A {}

const b = new B();
(b.foo
: number) // error, number !~> function

module.exports = B;
