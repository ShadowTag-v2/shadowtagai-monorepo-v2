import pluginJs from "@eslint/js";
import pluginHtml from "eslint-plugin-html";
import globals from "globals";

export default [
  {
    files: ["**/*.html"],
    plugins: { html: pluginHtml },
    rules: { "max-len": ["error", { code: 150 }] },
  },
  { languageOptions: { globals: globals.browser } },
  pluginJs.configs.recommended,
];
