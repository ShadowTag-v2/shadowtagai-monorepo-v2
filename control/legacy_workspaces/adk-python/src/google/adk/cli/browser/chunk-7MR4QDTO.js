import {
  Bc as _,
  ob as a,
  Zb as C,
  eb as c,
  ub as d,
  yb as f,
  Lb as g,
  zb as h,
  vb as l,
  md as M,
  xb as m,
  Da as o,
  wb as p,
  Qa as r,
  ab as s,
  Gb as u,
  nd as v,
  Yb as y,
} from "./chunk-BX7YU7E6.js";
import "./chunk-W7GRJBO5.js";
function O(e, x) {
  if ((e & 1 && u(0, 0), e & 2)) {
    const n = x.$implicit,
      i = g();
    m("surfaceId", i.surfaceId())("component", n);
  }
}
var D = (() => {
  class e extends M {
    direction = _("vertical");
    static \u0275fac = (() => {
      let n;
      return (t) => (n || (n = o(e)))(t || e);
    })();
    static \u0275cmp = s({
      type: e,
      selectors: [["a2ui-list"]],
      hostVars: 1,
      hostBindings: (i, t) => {
        i & 2 && a("direction", t.direction());
      },
      inputs: { direction: [1, "direction"] },
      features: [c],
      decls: 3,
      vars: 4,
      consts: [["a2ui-renderer", "", 3, "surfaceId", "component"]],
      template: (i, t) => {
        i & 1 && (f(0, "section"), l(1, O, 1, 2, "ng-container", 0, d), h()),
          i & 2 &&
            (y(t.theme.additionalStyles == null ? null : t.theme.additionalStyles.List),
            C(t.theme.components.List),
            r(),
            p(t.component().properties.children));
      },
      dependencies: [v],
      styles: [
        '[_nghost-%COMP%]{display:block;flex:var(--weight);min-height:0;overflow:auto}[direction="vertical"][_nghost-%COMP%]   section[_ngcontent-%COMP%]{display:grid}[direction="horizontal"][_nghost-%COMP%]   section[_ngcontent-%COMP%]{display:flex;max-width:100%;overflow-x:scroll;overflow-y:hidden;scrollbar-width:none}[direction="horizontal"][_nghost-%COMP%]   section[_ngcontent-%COMP%] > [_ngcontent-%COMP%]::slotted(*){flex:1 0 fit-content;max-width:min(80%,400px)}',
      ],
    });
  }
  return e;
})();

export { D as List };
