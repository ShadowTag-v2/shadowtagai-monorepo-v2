const path = require("path");

exports.parserPath = (lang) => require.resolve(`tree-sitter-${lang}/tree-sitter-${lang}.wasm`);
