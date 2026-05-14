# Coding Style Guide

## Python



- **Style**: Follow PEP 8.


- **Docstrings**: Google Style.


- **Type Hints**: Mandatory for all function signatures.


- **Error Handling**: Use custom exceptions defined in `src/exceptions.py`.


- **Logging**: Use `src/logger.py` instead of `print()`.

## Project Structure



- `src/`: Core logic.


- `src/tools/`: External integrations.


- `tests/`: Pytest suite.


- `artifacts/`: Generated outputs.

## Agent Architecture



- **Think-Act-Reflect**: All agents must implement this loop.


- **Memory**: Use `src/memory.py` for state persistence.


- **Config**: Use `src/config.py` for environment variables.
