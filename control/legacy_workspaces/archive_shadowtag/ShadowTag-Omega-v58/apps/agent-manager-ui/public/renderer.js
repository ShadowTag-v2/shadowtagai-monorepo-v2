class A2UIRenderer {
    constructor(target) { self.target = target; self.registry = {}; }

    render(schema) {
        self.target.innerHTML = "";
        self.registry = Object.fromEntries(schema.components.map(c => [c.id, c]));
        if (schema.root_id) self.target.appendChild(self.build(schema.root_id));
    }

    build(id) {
        const comp = self.registry[id];
        const el = document.createElement("div");
        el.className = `a2ui-component type-${comp.type.toLowerCase()}`;

        // SAFE RENDERING: Only specific props allowed
        if (comp.type === "Text") el.innerText = comp.props.text;
        if (comp.type === "Button") {
            const btn = document.createElement("button");
            btn.innerText = comp.props.label;
            btn.className = comp.props.intent;
            el.appendChild(btn);
        }
        if (comp.type === "Map") {
            el.innerText = `[SECURE MAP: ${comp.props.lat}, ${comp.props.lng}]`;
            el.style.background = "#e0e0e0";
            el.style.padding = "20px";
        }

        if (comp.children) {
            comp.children.forEach(childId => el.appendChild(self.build(childId)));
        }
        return el;
    }
}
