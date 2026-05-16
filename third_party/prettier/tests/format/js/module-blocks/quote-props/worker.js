worker = new Worker(module {
  onmessage = ({data}) => {
    const mod = import(data);
    postMessage(mod.fn());
  }
}, {type: "module"});

worker = new Worker(module {
  onmessage = ({data}) => {
    const mod = import(data);
    postMessage(mod.fn());
  }
}, {'type': "module"});

worker = new Worker(module {
  onmessage = ({data}) => {
    const mod = import(data);
    postMessage(mod.fn());
  }
}, {type: "module", foo: "bar" });

worker = new Worker(module {
  onmessage = ({data}) => {
    const mod = import(data);
    postMessage(mod.fn());
  }
}, {...{type: "module"}});

worker = new Worker(module {
  onmessage = ({data}) => {
    const mod = import(data);
    postMessage(mod.fn());
  }
}, {[type]: "module"});

worker.postMessage(module { export function fn() { return "hello!" } });
