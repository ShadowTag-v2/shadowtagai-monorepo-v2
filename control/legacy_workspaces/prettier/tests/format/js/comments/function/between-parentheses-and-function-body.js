function function_declaration() {
  // this is a function
  return 42;
}

(function named() {
  // this is a function
  return 42;
})();

(() => 42)();

/* anonymous declaration */
export default function () {
  // this is a function
  return 42;
}

a = {
  foo() {
    // this is a function
  },

  bar: () =>
    // this is a function
    {},
};

class A {
  foo() {
    // this is a function
  }

  bar = () =>
    // this is a function
    {};
}
