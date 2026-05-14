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

class Foo {
  static {}
}

class A1 {
  static {
    foo;
  }
}

class A2 {
  static {
    foo;
    bar;
  }
}
