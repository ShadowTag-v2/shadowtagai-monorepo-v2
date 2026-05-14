function Foo() {
  this.x = 0;
}
Foo.prototype.m = () => {};

var o1: { x: number; m(): void } = new Foo();

var o2: Foo = new Foo();
