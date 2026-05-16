import {
  md as _,
  qb as a,
  vc as C,
  Bb as c,
  eb as d,
  Yb as f,
  gc as g,
  hc as h,
  ab as l,
  Bc as M,
  Db as m,
  Qa as n,
  Ib as p,
  Da as r,
  sb as s,
  Cb as u,
  Lb as v,
  ic as x,
  Zb as y,
} from "./chunk-BX7YU7E6.js";
import "./chunk-W7GRJBO5.js";
function D(e, P) {
  if ((e & 1 && (c(0, "section"), m(1, "audio", 1), u()), e & 2)) {
    const t = v(),
      o = x(0);
    f(t.theme.additionalStyles == null ? null : t.theme.additionalStyles.AudioPlayer),
      y(t.theme.components.AudioPlayer),
      n(),
      p("src", o);
  }
}
var w = (() => {
  class e extends _ {
    url = M.required();
    resolvedUrl = C(() => this.resolvePrimitive(this.url()));
    static \u0275fac = (() => {
      let t;
      return (i) => (t || (t = r(e)))(i || e);
    })();
    static \u0275cmp = l({
      type: e,
      selectors: [["a2ui-audio"]],
      inputs: { url: [1, "url"] },
      features: [d],
      decls: 2,
      vars: 2,
      consts: [
        [3, "class", "style"],
        ["controls", "", 3, "src"],
      ],
      template: (o, i) => {
        if ((o & 1 && (g(0), a(1, D, 2, 5, "section", 0)), o & 2)) {
          const b = h(i.resolvedUrl());
          n(), s(b ? 1 : -1);
        }
      },
      styles: [
        "[_nghost-%COMP%]{display:block;flex:var(--weight);min-height:0;overflow:auto}audio[_ngcontent-%COMP%]{display:block;width:100%;box-sizing:border-box}",
      ],
    });
  }
  return e;
})();

export { w as Audio };
