import type { Transform } from "codemod:ast-grep";
import type JS from "codemod:ast-grep/langs/javascript";
import type TSX from "codemod:ast-grep/langs/tsx";
import type TS from "codemod:ast-grep/langs/typescript";

const transform: Transform<TS | TSX | JS> = async (root) => {
  const rootNode = root.root();

  const nodes = rootNode.findAll({
    rule: {
      pattern: "var $VAR = $VALUE",
    },
  });

  const edits = nodes.map((node) => {
    const varName = node.getMatch("VAR")?.text();
    const value = node.getMatch("VALUE")?.text();
    return node.replace(`const ${varName} = ${value}`);
  });

  const newSource = rootNode.commitEdits(edits);
  return newSource;
};

export default transform;
