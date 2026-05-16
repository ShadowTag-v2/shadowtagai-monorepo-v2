class C {
  static #x = 42;
  static y;
  static {
    try {
      C.y = doSomethingWith(C.#x);
    } catch {
      C.y = "unknown";
    }
  }
}
