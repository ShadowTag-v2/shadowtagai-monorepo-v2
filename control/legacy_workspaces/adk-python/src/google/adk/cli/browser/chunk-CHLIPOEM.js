import {
  Qa as a,
  eb as c,
  zb as d,
  Zb as f,
  nd as g,
  Bc as h,
  yb as l,
  Yb as m,
  Da as o,
  Jb as p,
  ab as r,
  xb as s,
  Gb as u,
  md as y,
} from "./chunk-BX7YU7E6.js";
import "./chunk-W7GRJBO5.js";
var _ = (() => {
  class n extends y {
    action = h.required();
    handleClick() {
      const t = this.action();
      t && super.sendAction(t);
    }
    static \u0275fac = (() => {
      let t;
      return (e) => (t || (t = o(n)))(e || n);
    })();
    static \u0275cmp = r({
      type: n,
      selectors: [["a2ui-button"]],
      inputs: { action: [1, "action"] },
      features: [c],
      decls: 2,
      vars: 6,
      consts: [
        [3, "click"],
        ["a2ui-renderer", "", 3, "surfaceId", "component"],
      ],
      template: (i, e) => {
        i & 1 && (l(0, "button", 0), p("click", () => e.handleClick()), u(1, 1), d()),
          i & 2 &&
            (m(e.theme.additionalStyles == null ? null : e.theme.additionalStyles.Button),
            f(e.theme.components.Button),
            a(),
            s("surfaceId", e.surfaceId())("component", e.component().properties.child));
      },
      dependencies: [g],
      styles: ["[_nghost-%COMP%]{display:block;flex:var(--weight);min-height:0}"],
    });
  }
  return n;
})();

export { _ as Button };
