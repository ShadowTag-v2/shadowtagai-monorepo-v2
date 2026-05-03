# AST-Aware QueryEngine Technical Specification

## Overview
This document outlines the design and implementation details for a standalone, AST-aware `QueryEngine` for the Antigravity ecosystem. The primary objective is to enhance code analysis, symbol resolution, and context retrieval by parsing code into Abstract Syntax Trees (ASTs) rather than treating it as raw text.

## 1. Goals and Motivation
Currently, querying codebases often relies on regex or basic string matching, which is brittle and language-agnostic. A standalone `QueryEngine` will:
- Understand structural components of the code (classes, functions, variable declarations).
- Enable intelligent reference searching (find usages, definitions).
- Support advanced refactoring operations by allowing the AI to query precise AST nodes.
- Operate efficiently across multiple languages (Python, TypeScript, Go).

## 2. Core Architecture
The `QueryEngine` will be designed as an independent service or module with the following components:

### 2.1. Parsing Layer
- **Technology Choice:** `tree-sitter` (via bindings like `py-tree-sitter` or native rust `tree-sitter-cli`). `tree-sitter` is incremental, robust, and supports numerous languages out of the box.
- **Responsibilities:** 
  - Read files from the workspace.
  - Parse code into language-specific ASTs.
  - Maintain a cache of parsed ASTs to avoid redundant parsing on subsequent queries.

### 2.2. Query Interface
- **Query Language:** Standard Tree-sitter query language (S-expressions) allowing precise targeting of nodes.
- **Higher-Level Abstractions:** A wrapper API that exposes common structural queries without requiring raw S-expressions from agents. 
  - `find_class_definition(class_name, file_path)`
  - `find_function_definition(func_name, file_path)`
  - `find_all_references(symbol_name, scope)`
  - `find_implementations(interface_name)`

### 2.3. Indexing and Caching (The Knowledge Graph)
- **Symbol Index:** A localized, lightweight index backed by **SQLite** mapping symbols to their defining AST nodes and file locations. The schema will store:
  - `symbol_name`, `type` (class, func, var), `file_path`, `start_line`, `end_line`, `ast_node_hash`.
- **SQLite Caching Strategy:** 
  - The SQLite database will reside in `.agents/cache/ast_index.db`.
  - Mtime (modification time) and file hashing will be used to conditionally invalidate cache rows.
- **Dependency Graph:** A mechanism to track imports and exports between files to accurately resolve symbol definitions across the monorepo.

### 2.4. Language Support
- **Tier 1 (Full Support):** Python, TypeScript/JavaScript, Go.
- **Tier 2 (Syntax Only):** Rust, C#, Java, C++.
- **Extensibility:** The engine will use dynamic loading for `tree-sitter-<lang>` grammar shared libraries to seamlessly add new language support.

## 3. Integration with Antigravity
The `QueryEngine` will be exposed to Antigravity agents as a new set of MCP (Model Context Protocol) tools or standard Python native tools.

### Proposed Tool Signatures
- **`ast_query`**: Accepts a language and a raw Tree-sitter query, returns a structured JSON of matching nodes with line numbers and contexts.
- **`find_symbol`**: High-level semantic search for definitions/references across the workspace.

## 4. Implementation Phasing
1. **Phase 1: Proof of Concept:** Wrap `tree-sitter` for Python and TypeScript. Provide a simple CLI and the `ast_query` tool for the agent.
2. **Phase 2: Indexing:** Implement the SQLite-based symbol index that incrementally updates when files change.
3. **Phase 3: Integration:** Expose semantic tools (`find_symbol`, `get_function_context`) to all Antigravity agents. Replace brittle regex-based context gathering.

## 5. Security & Performance Considerations
- **Sandboxing:** AST parsing must be safe against malformed or malicious code (Tree-sitter gracefully handles syntax errors).
- **Performance:** Parsing an entire monorepo can be slow. We must implement incremental parsing (parsing only changed files, relying on Git diffs or filesystem watchers) and bounding query depths.
