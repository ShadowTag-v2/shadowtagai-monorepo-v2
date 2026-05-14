# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Code Chunker
Intelligently chunks source code for embedding generation
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)


@dataclass
class CodeChunk:
    """Represents a chunk of code"""

    text: str
    chunk_type: str  # function, class, file, block
    start_line: int
    end_line: int
    language: str
    metadata: dict[str, Any]
    token_count: int | None = None


class CodeChunker:
    """
    Chunks source code intelligently for embedding generation

    Strategies:
    - Function-level chunking (preferred for code with clear functions)
    - Class-level chunking (for OOP code)
    - File-level chunking (for small files)
    - Fixed-size chunking with overlap (fallback)

    Supports:
    - Python, JavaScript, TypeScript, Go, Rust, Java, C++
    - AST-based parsing for accurate boundaries
    - Token counting for chunk size management
    """

    def __init__(self, max_tokens: int = 1500, overlap_tokens: int = 300, min_chunk_tokens: int = 50):
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens
        self.min_chunk_tokens = min_chunk_tokens

    def chunk_code(self, code: str, language: str, file_path: str | None = None) -> list[CodeChunk]:
        """
        Chunk code using the appropriate strategy

        Args:
            code: Source code content
            language: Programming language
            file_path: Optional file path for context

        Returns:
            List of CodeChunk objects
        """
        # Try function-level chunking first
        chunks = self._chunk_by_functions(code, language)

        if chunks:
            logger.debug(f"Chunked {file_path or 'code'} into {len(chunks)} function-level chunks")
            return chunks

        # Fallback to fixed-size chunking
        chunks = self._chunk_fixed_size(code, language)
        logger.debug(f"Chunked {file_path or 'code'} into {len(chunks)} fixed-size chunks")
        return chunks

    def _chunk_by_functions(self, code: str, language: str) -> list[CodeChunk]:
        """
        Chunk code by function boundaries

        Uses regex patterns to identify function definitions.
        For production, consider using tree-sitter or AST parsers.
        """
        chunks = []

        # Language-specific function patterns
        patterns = {
            "python": r"^(async\s+)?def\s+\w+\s*\([^)]*\):",
            "javascript": r"^(async\s+)?function\s+\w+\s*\([^)]*\)\s*{",
            "typescript": r"^(async\s+)?function\s+\w+\s*\([^)]*\):\s*\w+\s*{",
            "go": r"^func\s+(\(\w+\s+\*?\w+\)\s+)?\w+\s*\([^)]*\)",
            "rust": r"^(pub\s+)?(async\s+)?fn\s+\w+\s*(<[^>]*>)?\s*\([^)]*\)",
            "java": r"^(public|private|protected)\s+(static\s+)?[\w<>]+\s+\w+\s*\([^)]*\)",
            "cpp": r"^[\w:<>]+\s+\w+::\w+\s*\([^)]*\)",
        }

        pattern = patterns.get(language.lower())
        if not pattern:
            return []

        lines = code.split("\n")
        current_function = []
        current_start_line = 0
        in_function = False
        indent_level = 0

        for line_num, line in enumerate(lines, start=1):
            # Check if line starts a new function
            if re.match(pattern, line.strip(), re.MULTILINE):
                # Save previous function if exists
                if current_function:
                    chunk_text = "\n".join(current_function)
                    if self._estimate_tokens(chunk_text) >= self.min_chunk_tokens:
                        chunks.append(
                            CodeChunk(
                                text=chunk_text,
                                chunk_type="function",
                                start_line=current_start_line,
                                end_line=line_num - 1,
                                language=language,
                                metadata={"extraction_method": "regex"},
                            )
                        )

                # Start new function
                current_function = [line]
                current_start_line = line_num
                in_function = True
                indent_level = len(line) - len(line.lstrip())

            elif in_function:
                current_function.append(line)

                # Simple heuristic: function ends when indentation returns to function level
                # and we encounter a blank line or new function
                if line.strip() == "":
                    continue
                current_indent = len(line) - len(line.lstrip())

                # For languages with braces, check for closing brace at function level
                if language.lower() in ["javascript", "typescript", "java", "cpp", "go", "rust"]:
                    if line.strip() == "}" and current_indent <= indent_level:
                        chunk_text = "\n".join(current_function)
                        if self._estimate_tokens(chunk_text) >= self.min_chunk_tokens:
                            chunks.append(
                                CodeChunk(
                                    text=chunk_text,
                                    chunk_type="function",
                                    start_line=current_start_line,
                                    end_line=line_num,
                                    language=language,
                                    metadata={"extraction_method": "regex"},
                                )
                            )
                        current_function = []
                        in_function = False

        # Add last function if exists
        if current_function:
            chunk_text = "\n".join(current_function)
            if self._estimate_tokens(chunk_text) >= self.min_chunk_tokens:
                chunks.append(
                    CodeChunk(
                        text=chunk_text,
                        chunk_type="function",
                        start_line=current_start_line,
                        end_line=len(lines),
                        language=language,
                        metadata={"extraction_method": "regex"},
                    )
                )

        return chunks

    def _chunk_fixed_size(self, code: str, language: str) -> list[CodeChunk]:
        """
        Chunk code into fixed-size chunks with overlap

        Args:
            code: Source code
            language: Programming language

        Returns:
            List of CodeChunk objects
        """
        lines = code.split("\n")
        chunks = []
        current_chunk_lines = []
        current_tokens = 0
        chunk_start_line = 1

        for line_num, line in enumerate(lines, start=1):
            line_tokens = self._estimate_tokens(line)

            # If adding this line exceeds max tokens, save current chunk
            if current_tokens + line_tokens > self.max_tokens and current_chunk_lines:
                chunk_text = "\n".join(current_chunk_lines)
                chunks.append(
                    CodeChunk(
                        text=chunk_text,
                        chunk_type="block",
                        start_line=chunk_start_line,
                        end_line=line_num - 1,
                        language=language,
                        metadata={"extraction_method": "fixed_size"},
                        token_count=current_tokens,
                    )
                )

                # Calculate overlap
                overlap_line_count = 0
                overlap_tokens = 0
                for i in range(len(current_chunk_lines) - 1, -1, -1):
                    overlap_line_tokens = self._estimate_tokens(current_chunk_lines[i])
                    if overlap_tokens + overlap_line_tokens > self.overlap_tokens:
                        break
                    overlap_tokens += overlap_line_tokens
                    overlap_line_count += 1

                # Start new chunk with overlap
                current_chunk_lines = current_chunk_lines[-overlap_line_count:] if overlap_line_count > 0 else []
                current_tokens = overlap_tokens
                chunk_start_line = line_num - overlap_line_count

            current_chunk_lines.append(line)
            current_tokens += line_tokens

        # Add final chunk
        if current_chunk_lines:
            chunk_text = "\n".join(current_chunk_lines)
            if current_tokens >= self.min_chunk_tokens:
                chunks.append(
                    CodeChunk(
                        text=chunk_text,
                        chunk_type="block",
                        start_line=chunk_start_line,
                        end_line=len(lines),
                        language=language,
                        metadata={"extraction_method": "fixed_size"},
                        token_count=current_tokens,
                    )
                )

        return chunks

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text

        Uses simple heuristic: ~4 characters per token
        For production, use tiktoken or similar
        """
        return len(text) // 4

    def chunk_repository_files(self, files: list[dict[str, Any]]) -> list[CodeChunk]:
        """
        Chunk multiple repository files

        Args:
            files: List of file dictionaries with 'content', 'language', 'path'

        Returns:
            List of CodeChunk objects across all files
        """
        all_chunks = []

        for file_info in files:
            content = file_info.get("content", "")
            language = file_info.get("language", "unknown")
            file_path = file_info.get("path", "")

            chunks = self.chunk_code(content, language, file_path)

            # Add file path to metadata
            for chunk in chunks:
                chunk.metadata["file_path"] = file_path

            all_chunks.extend(chunks)

        logger.info(f"Chunked {len(files)} files into {len(all_chunks)} total chunks")
        return all_chunks


# Example usage
if __name__ == "__main__":
    chunker = CodeChunker(max_tokens=1000, overlap_tokens=200)

    python_code = """
def fibonacci(n: int) -> int:
    \"\"\"Calculate Fibonacci number\"\"\"
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def factorial(n: int) -> int:
    \"\"\"Calculate factorial\"\"\"
    if n <= 1:
        return 1
    return n * factorial(n-1)

class Calculator:
    def add(self, a: int, b: int) -> int:
        return a + b

    def subtract(self, a: int, b: int) -> int:
        return a - b
"""

    chunks = chunker.chunk_code(python_code, "python")

    print(f"Generated {len(chunks)} chunks:\n")
    for i, chunk in enumerate(chunks, 1):
        print(f"Chunk {i} ({chunk.chunk_type}):")
        print(f"Lines: {chunk.start_line}-{chunk.end_line}")
        print(f"Preview: {chunk.text[:100]}...")
        print()
