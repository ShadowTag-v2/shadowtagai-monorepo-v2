namespace m2 {
  function fn() {
    return 1;
  }
  export function exports() {
    return 1;
  }
  export function require() {
    return "require";
  }
}

namespace m2 {
  export function exports() {
    return 1;
  }

  export function require() {
    return "require";
  }
}
