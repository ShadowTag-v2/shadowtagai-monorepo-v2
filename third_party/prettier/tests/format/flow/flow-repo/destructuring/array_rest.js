const xs = [0, "", true];
const [a, ...ys] = xs;
const [b, ...zs] = ys;
const c = zs[0]; // retain tuple info
const d = zs[1]; // run off the end

(a: void); // error: number ~> void
(b: void); // error: string ~> void
(c: void); // error: boolean ~> void
(d: void); // error: number|string|boolean ~> void

const [...e] = 0;
