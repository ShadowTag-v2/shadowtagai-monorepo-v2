# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import ast
import sys


class ShieldVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.violations = []

    def visit_Call(self, node) -> None:
        if isinstance(node.func, ast.Name) and node.func.id in ["eval", "exec"]:
            self.violations.append(f"CRITICAL: Found {node.func.id}() at line {node.lineno}")
        self.generic_visit(node)


def run_ast_shield(filepath) -> None:
    try:
        with open(filepath) as f:
            tree = ast.parse(f.read())
        visitor = ShieldVisitor()
        visitor.visit(tree)
        if visitor.violations:
            for _v in visitor.violations:
                pass
            sys.exit(1)
    except Exception:
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_ast_shield(sys.argv[1])
    else:
        pass
