# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""AST chunk-stripping script for micro-compaction."""

import ast


class MicroCompactionNodeTransformer(ast.NodeTransformer):
    """Transformer that strips docstrings and type annotations to compress code."""

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Strip docstrings and return type annotations from functions."""
        self.generic_visit(node)
        # Strip docstring
        if ast.get_docstring(node):
            node.body = node.body[1:]
        # Strip return type hint
        node.returns = None
        # Strip argument type hints
        for arg in node.args.args + node.args.kwonlyargs:
            arg.annotation = None
        if node.args.vararg:
            node.args.vararg.annotation = None
        if node.args.kwarg:
            node.args.kwarg.annotation = None
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        """Strip docstrings from classes."""
        self.generic_visit(node)
        if ast.get_docstring(node):
            node.body = node.body[1:]
        return node

    def visit_AnnAssign(self, node: ast.AnnAssign) -> ast.Assign | None:
        """Convert annotated assignments to regular assignments."""
        if node.value is None:
            return None  # Remove pure annotations without assignment
        return ast.Assign(targets=[node.target], value=node.value)


def strip_ast_chunks(source_code: str) -> str:
    """
    Strips non-essential AST chunks (docstrings, type hints) from source code
    for micro-compaction of the context window.

    Args:
        source_code (str): The original Python source code.

    Returns:
        str: The compacted source code.
    """
    try:
        tree = ast.parse(source_code)
        transformer = MicroCompactionNodeTransformer()
        transformed_tree = transformer.visit(tree)
        ast.fix_missing_locations(transformed_tree)
        return ast.unparse(transformed_tree)
    except SyntaxError:
        # Fallback to original code if it cannot be parsed
        return source_code
