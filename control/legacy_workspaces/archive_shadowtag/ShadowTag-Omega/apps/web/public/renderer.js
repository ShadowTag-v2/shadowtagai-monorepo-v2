class A2UIRenderer {
    constructor(target) { this.target = target; this.map = {}; }
    render(json) {
        this.target.innerHTML = '';
        this.map = Object.fromEntries(json.components.map(c => [c.id, c]));
        if(json.root_id) this.target.appendChild(this.build(json.root_id));
    }
    build(id) {
        const c = this.map[id];
        const el = document.createElement('div');
        el.className = `comp-${c.type.toLowerCase()}`;
        if(c.type === 'Text') el.innerText = c.props.text;
        if(c.type === 'Button') {
            const b = document.createElement('button');
            b.innerText = c.props.label;
            el.appendChild(b);
        }
        if(c.children) c.children.forEach(kid => el.appendChild(this.build(kid)));
        return el;
    }
}
