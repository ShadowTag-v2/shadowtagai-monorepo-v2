import {
  Bc as _,
  qb as a,
  md as b,
  ic as C,
  sb as c,
  ab as d,
  Lb as f,
  Zb as g,
  gc as h,
  Na as l,
  vc as M,
  Bb as m,
  Qa as n,
  Db as p,
  Da as r,
  eb as s,
  Cb as u,
  Ib as v,
  hc as x,
  Yb as y,
} from "./chunk-BX7YU7E6.js";
import "./chunk-W7GRJBO5.js";
function U(e, V) {
  if ((e & 1 && (m(0, "section"), p(1, "video", 1), u()), e & 2)) {
    const t = f(),
      i = C(0);
    y(t.theme.additionalStyles == null ? null : t.theme.additionalStyles.Video),
      g(t.theme.components.Video),
      n(),
      v("src", i, l);
  }
}
var L = (() => {
  class e extends b {
    url = _.required();
    resolvedUrl = M(() => this.resolvePrimitive(this.url()));
    static \u0275fac = (() => {
      let t;
      return (o) => (t || (t = r(e)))(o || e);
    })();
    static \u0275cmp = d({
      type: e,
      selectors: [["a2ui-video"]],
      inputs: { url: [1, "url"] },
      features: [s],
      decls: 2,
      vars: 2,
      consts: [
        [3, "class", "style"],
        ["controls", "", 3, "src"],
      ],
      template: (i, o) => {
        if ((i & 1 && (h(0), a(1, U, 2, 5, "section", 0)), i & 2)) {
          const D = x(o.resolvedUrl());
          n(), c(D ? 1 : -1);
        }
      },
      styles: [
        "[_nghost-%COMP%]{display:block;flex:var(--weight);min-height:0;overflow:auto}video[_ngcontent-%COMP%]{display:block;width:100%;box-sizing:border-box}",
      ],
    });
  }
  return e;
})();

export { L as Video };
