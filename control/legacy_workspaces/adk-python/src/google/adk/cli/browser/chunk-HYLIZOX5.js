import {
  Da as _,
  vc as $,
  Qa as a,
  za as b,
  Yb as C,
  Lb as c,
  ac as D,
  xb as d,
  bd as E,
  gc as F,
  ab as f,
  Hb as g,
  eb as h,
  Gb as I,
  hc as k,
  md as L,
  yb as l,
  _b as M,
  nd as N,
  zb as o,
  na as p,
  Zb as r,
  ic as S,
  Jb as T,
  oa as u,
  vb as v,
  Bc as w,
  ub as x,
  wb as y,
} from "./chunk-BX7YU7E6.js";
import "./chunk-W7GRJBO5.js";
function B(n, m) {
  if (n & 1) {
    const t = g();
    l(0, "button", 2),
      T("click", () => {
        const e = p(t).$index,
          i = c();
        return u(i.selectedIndex.set(e));
      }),
      M(1),
      o();
  }
  if (n & 2) {
    const t = m.$implicit,
      s = m.$index,
      e = c(),
      i = S(0);
    r(e.buttonClasses()[i]), d("disabled", i === s), a(), D(" ", e.resolvePrimitive(t.title), " ");
  }
}
var z = (() => {
  class n extends L {
    selectedIndex = b(0);
    tabs = w.required();
    buttonClasses = $(() => {
      const t = this.selectedIndex();
      return this.tabs().map((s, e) =>
        e === t
          ? E.merge(
              this.theme.components.Tabs.controls.all,
              this.theme.components.Tabs.controls.selected,
            )
          : this.theme.components.Tabs.controls.all,
      );
    });
    static \u0275fac = (() => {
      let t;
      return (e) => (t || (t = _(n)))(e || n);
    })();
    static \u0275cmp = f({
      type: n,
      selectors: [["a2ui-tabs"]],
      inputs: { tabs: [1, "tabs"] },
      features: [h],
      decls: 6,
      vars: 9,
      consts: [
        [3, "disabled", "class"],
        ["a2ui-renderer", "", 3, "surfaceId", "component"],
        [3, "click", "disabled"],
      ],
      template: (s, e) => {
        if (
          (s & 1 &&
            (F(0), l(1, "section")(2, "div"), v(3, B, 2, 4, "button", 0, x), o(), I(5, 1), o()),
          s & 2)
        ) {
          const i = e.tabs(),
            V = k(e.selectedIndex());
          a(),
            C(e.theme.additionalStyles == null ? null : e.theme.additionalStyles.Tabs),
            r(e.theme.components.Tabs.container),
            a(),
            r(e.theme.components.Tabs.element),
            a(),
            y(i),
            a(2),
            d("surfaceId", e.surfaceId())("component", i[V].child);
        }
      },
      dependencies: [N],
      styles: ["[_nghost-%COMP%]{display:block;flex:var(--weight)}"],
    });
  }
  return n;
})();

export { z as Tabs };
