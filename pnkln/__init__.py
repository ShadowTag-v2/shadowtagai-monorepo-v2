# Namespace package extension — merges root pnkln with apps/aiyou_stack pnkln
# This allows pnkln.core (root) and pnkln.governance (apps) to coexist
from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)
