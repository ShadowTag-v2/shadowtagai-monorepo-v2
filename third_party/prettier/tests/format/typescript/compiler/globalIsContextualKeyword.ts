function a() {
  const global = 1;
}
function b() {
  class global {}
}

namespace global {}

function foo(global: number) {}

const obj = {
  global: "123",
};
