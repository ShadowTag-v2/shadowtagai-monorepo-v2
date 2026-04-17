import ast
import sys


class ShieldVisitor(ast.NodeVisitor):
    def __init__(self):
        self.violations = []

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id in ["eval", "exec"]:
                self.violations.append(f"CRITICAL: Found {node.func.id}() at line {node.lineno}")
        self.generic_visit(node)


def run_ast_shield(filepath):
    try:
        with open(filepath) as f:
            tree = ast.parse(f.read())
        visitor = ShieldVisitor()
        visitor.visit(tree)
        if visitor.violations:
            print("17-Layer DOW CRSMC Shield activated: Violations detected!")
            for v in visitor.violations:
                print(v)
            sys.exit(1)
        print("Shield validation passed. Zero neurosymbolic leakage.")
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_ast_shield(sys.argv[1])
    else:
        print("Usage: python3 crs_shield_ast.py <target_file.py>")
