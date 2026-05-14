// inner type parameters shadow outer ones of the same name
// no errors expected

class C<T extends Date> {
  g<T extends number>() {
    var x: T;
    x.toFixed();
  }

  h() {
    var x: T;
    x.getDate();
  }
}

class C2<T extends Date, U extends Date> {
  g<T extends number, U extends number>() {
    var x: U;
    x.toFixed();
  }

  h() {
    var x: U;
    x.getDate();
  }
}
//class C2<T extends Date, U extends T> {
//    g<T extends Number, U extends T>() {
//        var x: U;
//        x.toFixed();
//    }

//    h() {
//        var x: U;
//        x.getDate();
//    }
//}
