import {
  md as _,
  Qa as a,
  Yb as C,
  ab as c,
  eb as d,
  zb as f,
  Zb as g,
  Gb as h,
  vb as l,
  xb as m,
  Da as o,
  wb as p,
  ub as s,
  yb as u,
  nc as v,
  nd as w,
  Lb as y,
} from "./chunk-BX7YU7E6.js";
import "./chunk-W7GRJBO5.js";
var D = (e) => [e];
function M(e, F) {
  if ((e & 1 && h(0, 0), e & 2)) {
    const i = F.$implicit,
      n = y();
    m("surfaceId", n.surfaceId())("component", i);
  }
}
var T = (() => {
  class e extends _ {
    static \u0275fac = (() => {
      let i;
      return (t) => (i || (i = o(e)))(t || e);
    })();
    static \u0275cmp = c({
      type: e,
      selectors: [["a2ui-card"]],
      features: [d],
      decls: 3,
      vars: 6,
      consts: [["a2ui-renderer", "", 3, "surfaceId", "component"]],
      template: (n, t) => {
        if ((n & 1 && (u(0, "section"), l(1, M, 1, 2, "ng-container", 0, s), f()), n & 2)) {
          const r = t.component().properties,
            I = r.children || v(4, D, r.child);
          C(t.theme.additionalStyles == null ? null : t.theme.additionalStyles.Card),
            g(t.theme.components.Card),
            a(),
            p(I);
        }
      },
      dependencies: [w],
      styles: [
        `a2ui-card{display:block;flex:var(--weight);min-height:0;overflow:auto}a2ui-card>section{height:100%;width:100%;min-height:0;overflow:auto}a2ui-card>section>*{height:100%;width:100%}
`,
      ],
      encapsulation: 2,
    });
  }
  return e;
})();

export { T as Card };
