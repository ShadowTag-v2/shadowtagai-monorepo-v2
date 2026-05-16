// all errors imported modules conflict with local variables

namespace A {
  export var Point = { x: 0, y: 0 };
  export interface Point {
    x: number;
    y: number;
  }
}

namespace B {
  var A = { x: 0, y: 0 };
  import Point = A;
}

namespace X {
  export namespace Y {
    export interface Point {
      x: number;
      y: number;
    }
  }

  export class Y {
    name: string;
  }
}

namespace Z {
  import Y = X.Y;

  var Y = 12;
}
