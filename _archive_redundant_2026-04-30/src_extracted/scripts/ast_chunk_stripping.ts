import * as fs from 'fs';
import * as ts from 'typescript';

function stripChunks(sourceFile: ts.SourceFile): string {
  const transformer = (context: ts.TransformationContext) => (rootNode: ts.Node) => {
    function visit(node: ts.Node): ts.Node {
      if (
        ts.isBlock(node) &&
        node.parent &&
        (ts.isFunctionDeclaration(node.parent) ||
          ts.isMethodDeclaration(node.parent) ||
          ts.isGetAccessor(node.parent) ||
          ts.isSetAccessor(node.parent) ||
          ts.isConstructorDeclaration(node.parent) ||
          ts.isArrowFunction(node.parent))
      ) {
        // Return an empty block with a comment indicating it was stripped
        const strippedComment = ts.factory.createIdentifier('/* stripped */');
        const stmt = ts.factory.createExpressionStatement(strippedComment);
        return ts.factory.createBlock([stmt], true);
      }
      return ts.visitEachChild(node, visit, context);
    }
    return ts.visitNode(rootNode, visit) as ts.Node;
  };

  const result = ts.transform(sourceFile, [transformer]);
  const printer = ts.createPrinter({ newLine: ts.NewLineKind.LineFeed });
  return printer.printNode(ts.EmitHint.Unspecified, result.transformed[0], sourceFile);
}

export function compactFile(filePath: string) {
  const code = fs.readFileSync(filePath, 'utf-8');
  const sourceFile = ts.createSourceFile(filePath, code, ts.ScriptTarget.Latest, true);
  const compacted = stripChunks(sourceFile);
  console.log(compacted);
}

const isMain = typeof require !== 'undefined' && require.main === module;
if (isMain || process.argv[1]?.includes('ast_chunk_stripping')) {
  const file = process.argv[2];
  if (!file) {
    console.error('Usage: tsx ast_chunk_stripping.ts <file_path>');
    process.exit(1);
  }
  compactFile(file);
}
