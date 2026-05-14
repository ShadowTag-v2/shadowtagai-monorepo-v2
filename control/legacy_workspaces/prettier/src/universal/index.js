import path from "node:path";
import { toPath } from "url-or-path";

/**
@param {string | URL} file
@returns {string}
*/
const getFileBasename = (file) => {
  try {
    return path.basename(toPath(file));
  } catch {
    return "";
  }
};

export { fileURLToPath } from "node:url";
export { isUrl } from "url-or-path";
export { default as getInterpreter } from "../utilities/get-interpreter.js";
export { getFileBasename };
