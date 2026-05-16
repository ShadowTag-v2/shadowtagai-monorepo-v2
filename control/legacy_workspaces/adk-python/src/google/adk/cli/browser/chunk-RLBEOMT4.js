import {
  eb as D,
  Ib as d,
  ab as f,
  Da as g,
  _b as I,
  Bc as l,
  $b as M,
  Cb as m,
  md as N,
  vc as o,
  Zb as r,
  Bb as s,
  Yb as T,
  Qa as u,
  ob as v,
  Kb as y,
} from "./chunk-BX7YU7E6.js";
import "./chunk-W7GRJBO5.js";
var S = (() => {
  class i extends N {
    value = l.required();
    enableDate = l.required();
    enableTime = l.required();
    inputId = super.getUniqueId("a2ui-datetime-input");
    inputType = o(() => {
      const t = this.enableDate(),
        n = this.enableTime();
      return t && n ? "datetime-local" : t ? "date" : n ? "time" : "datetime-local";
    });
    label = o(() => {
      const t = this.inputType();
      return t === "date" ? "Date" : t === "time" ? "Time" : "Date & Time";
    });
    inputValue = o(() => {
      const t = this.inputType(),
        n = super.resolvePrimitive(this.value()) || "",
        e = n ? new Date(n) : null;
      if (!e || isNaN(e.getTime())) return "";
      const p = this.padNumber(e.getFullYear()),
        a = this.padNumber(e.getMonth()),
        c = this.padNumber(e.getDate()),
        b = this.padNumber(e.getHours()),
        h = this.padNumber(e.getMinutes());
      return t === "date"
        ? `${p}-${a}-${c}`
        : t === "time"
          ? `${b}:${h}`
          : `${p}-${a}-${c}T${b}:${h}`;
    });
    handleInput(t) {
      const n = this.value()?.path;
      !(t.target instanceof HTMLInputElement) ||
        !n ||
        this.processor.setData(this.component(), n, t.target.value, this.surfaceId());
    }
    padNumber(t) {
      return t.toString().padStart(2, "0");
    }
    static \u0275fac = (() => {
      let t;
      return (e) => (t || (t = g(i)))(e || i);
    })();
    static \u0275cmp = f({
      type: i,
      selectors: [["a2ui-datetime-input"]],
      inputs: { value: [1, "value"], enableDate: [1, "enableDate"], enableTime: [1, "enableTime"] },
      features: [D],
      decls: 4,
      vars: 13,
      consts: [
        [3, "for"],
        ["autocomplete", "off", 3, "input", "id", "value"],
      ],
      template: (n, e) => {
        n & 1 &&
          (s(0, "section")(1, "label", 0),
          I(2),
          m(),
          s(3, "input", 1),
          y("input", (a) => e.handleInput(a)),
          m()()),
          n & 2 &&
            (r(e.theme.components.DateTimeInput.container),
            u(),
            r(e.theme.components.DateTimeInput.label),
            d("htmlFor", e.inputId),
            u(),
            M(e.label()),
            u(),
            T(e.theme.additionalStyles == null ? null : e.theme.additionalStyles.DateTimeInput),
            r(e.theme.components.DateTimeInput.element),
            d("id", e.inputId)("value", e.inputValue()),
            v("type", e.inputType()));
      },
      styles: [
        "[_nghost-%COMP%]{display:block;flex:var(--weight);min-height:0;overflow:auto}input[_ngcontent-%COMP%]{display:block;width:100%;box-sizing:border-box}",
      ],
    });
  }
  return i;
})();

export { S as DatetimeInput };
