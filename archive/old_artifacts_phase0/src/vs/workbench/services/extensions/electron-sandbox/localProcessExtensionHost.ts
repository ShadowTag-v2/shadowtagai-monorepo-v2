if (!opts.execArgv.some(arg => arg.startsWith('--max-old-space-size'))) {
    opts.execArgv.push('--max-old-space-size=8192'); // 8GB ceiling for heavy AST/DOM parsing
}
