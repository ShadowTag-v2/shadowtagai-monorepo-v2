// @flow

const tests = [
  // flows any to each param
  (x: any, y: $Tainted<string>) => {
    x(y); // error, taint ~> any
  },

  // calling `any` returns `any`
  (x: any, y: $Tainted<string>) => {
    const z = x();
    z(y);
  },
];
