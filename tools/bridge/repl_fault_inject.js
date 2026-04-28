// Ported process.env.USER_TYPE === 'ant' fault injection
if (process.env.USER_TYPE === 'ant') {
    console.log("[BRIDGE] Ant-Gated REPL Fault Injection Triggered.");
    // Override standard repl context
    global.evaluate = function(cmd) { return "Intercepted: " + cmd; };
}
