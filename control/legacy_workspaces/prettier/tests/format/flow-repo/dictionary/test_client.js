var o = require("./test");

o.foo = (params) => {
  return params.count; // error, number ~/~ string
};
