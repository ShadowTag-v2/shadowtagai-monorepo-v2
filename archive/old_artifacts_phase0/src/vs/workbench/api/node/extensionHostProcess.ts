const originalEmit = process.emit;
// @ts-ignore
process.emit = function (name: string, data: any, ...args: any[]) {
    // Silently swallow DEP0040 to preserve JSON-RPC stream integrity for MCP servers
    if (name === 'warning' && data && data.name === 'DeprecationWarning' && data.code === 'DEP0040') return false;
    return originalEmit.apply(process, [name, data, ...args] as any);
};
process.noDeprecation = true;
