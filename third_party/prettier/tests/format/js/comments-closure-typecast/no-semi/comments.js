// https://github.com/prettier/prettier/issues/18307
class C {
  typeCastS() {
    /** @type {string} */ (this.s).length; // 7
  }
}
// https://github.com/prettier/prettier/issues/12794
/** @type {(token: Token)=>void} */ (onToken)(token); // 1
/** @type {(token: Token)=>void} */ (onToken)(token); // 2

/** @type {(token: Token)=>void} */ // unparenthesized
[onToken](token); // 3
/** @type {(token: Token)=>void} */ onToken(token); /* not a type cast comment */ // 4

[](token); /* don't need leading semicolon */ // 5

foo(token); // 5
