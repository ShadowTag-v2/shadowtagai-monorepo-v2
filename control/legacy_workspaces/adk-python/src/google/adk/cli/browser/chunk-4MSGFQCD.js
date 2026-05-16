import {
  Da as a,
  vc as C,
  qb as c,
  Cb as d,
  _b as f,
  gc as g,
  hc as h,
  Bc as I,
  Qa as i,
  sb as l,
  md as M,
  Bb as m,
  Lb as p,
  eb as r,
  ab as s,
  Yb as u,
  Zb as v,
  ic as x,
  $b as y,
} from "./chunk-BX7YU7E6.js";
import "./chunk-W7GRJBO5.js";
function _(e, D) {
  if ((e & 1 && (m(0, "section")(1, "span", 1), f(2), d()()), e & 2)) {
    const t = p(),
      n = x(0);
    u(t.theme.additionalStyles == null ? null : t.theme.additionalStyles.Icon),
      v(t.theme.components.Icon),
      i(2),
      y(n);
  }
}
var S = (() => {
  class e extends M {
    name = I.required();
    resolvedName = C(() => this.resolvePrimitive(this.name()));
    static \u0275fac = (() => {
      let t;
      return (o) => (t || (t = a(e)))(o || e);
    })();
    static \u0275cmp = s({
      type: e,
      selectors: [["a2ui-icon"]],
      inputs: { name: [1, "name"] },
      features: [r],
      decls: 2,
      vars: 2,
      consts: [
        [3, "class", "style"],
        [1, "g-icon"],
      ],
      template: (n, o) => {
        if ((n & 1 && (g(0), c(1, _, 3, 5, "section", 0)), n & 2)) {
          const N = h(o.resolvedName());
          i(), l(N ? 1 : -1);
        }
      },
      styles: ["[_nghost-%COMP%]{display:block;flex:var(--weight);min-height:0;overflow:auto}"],
    });
  }
  return e;
})();

export { S as Icon };
