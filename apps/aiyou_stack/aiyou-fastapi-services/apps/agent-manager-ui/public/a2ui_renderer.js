class A2UIRenderer {
  constructor(target) {
    this.target = target;
    this.componentMap = {};
  }

  render(payload) {
    this.target.innerHTML = "";
    this.componentMap = Object.fromEntries(payload.components.map((c) => [c.id, c]));
    if (payload.root_id) this.target.appendChild(this.createElement(payload.root_id));
  }

  createElement(id) {
    const comp = this.componentMap[id];
    if (!comp) return document.createElement("div");

    const el = document.createElement("div");
    el.className = `a2ui-component type-${comp.type.toLowerCase()}`;
    el.style.margin = "10px";

    // --- DISTINCTION: RICH MEDIA SUPPORT ---

    if (comp.type === "Map") {
      el.style.height = "300px";
      el.style.background = "#e0e0e0";
      el.style.display = "flex";
      el.style.alignItems = "center";
      el.style.justifyContent = "center";
      el.innerText = `🗺️ MAP VIEW\nLat: ${comp.props.lat}\nLng: ${comp.props.lng}`;
    } else if (comp.type === "Chart") {
      const canvas = document.createElement("canvas");
      el.appendChild(canvas);
      // In a real app, we'd initialize Chart.js here
      el.innerHTML += `📊 CHART: ${comp.props.title} (Data: ${comp.props.data.length} points)`;
      el.style.border = "1px dashed #666";
      el.style.padding = "20px";
    } else if (comp.type === "Text") {
      el.innerText = comp.props.content || "";
      if (comp.props.variant === "h1") el.style.fontSize = "2em";
    } else if (comp.type === "Button") {
      const btn = document.createElement("button");
      btn.innerText = comp.props.label;
      btn.onclick = () => console.log("Action:", comp.props.action);
      btn.style.padding = "10px 20px";
      btn.style.cursor = "pointer";
      btn.style.background = comp.props.variant === "danger" ? "#d32f2f" : "#1976d2";
      btn.style.color = "white";
      btn.style.border = "none";
      el.appendChild(btn);
    }

    // Recursion
    if (comp.children) {
      comp.children.forEach((childId) => el.appendChild(this.createElement(childId)));
    }
    return el;
  }
}
