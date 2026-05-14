function C() {}
C.prototype.f = () => C.g(0);
C.g = (x) => x;

var x:string = new C().f();
