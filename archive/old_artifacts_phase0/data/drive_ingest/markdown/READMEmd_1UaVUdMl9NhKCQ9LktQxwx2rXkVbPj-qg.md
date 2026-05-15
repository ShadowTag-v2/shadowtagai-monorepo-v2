# Judge #6: AI Governance & Risk Management System

Version 2.0.0 - Refactored for production use

## Overview

Judge #6 is a cryptographically-enforced AI governance framework implementing:

- **Cor.53 Constitutional Axioms** - Immutable governance rules
- **ATP 5-19 Risk Stratification** - Military-grade risk assessment
- **ShadowTag 2.0 Provenance** - Cryptographic audit trails
- **Six-Gate Evaluation Process** - Multi-stage decision validation

## Architecture

### Core Components

```
judge6/
├── __init__.py           # Package exports
├── models.py             # Data models and enums
├── constitutional.py     # Cor.53 axioms
├── config.py             # Configuration management
├── risk_manager.py       # ATP 5-19 risk assessment
├── provenance.py         # ShadowTag 2.0 cryptography
├── judgment.py           # Core judgment engine
└── main.py              # Entry point and demo
```

### Six-Gate Evaluation Process

1. **GATE 1**: ATP 5-19 Risk Classification (pre-execution)
2. **GATE 2**: Purpose Declaration Validation
3. **GATE 3**: Constitutional Axiom Verification
4. **GATE 4**: Resource Allocation per Risk Level
5. **GATE 5**: Execution with Monitoring
6. **GATE 6**: Cryptographic Provenance Stamp

## Installation

```bash
# Install dependencies
pip install typing-extensions dataclasses-json

# Or using uv
uv pip install typing-extensions dataclasses-json
```

## Usage

### Basic Usage

```python
from judge6 import JudgmentRule

# Initialize Judge #6
judge = JudgmentRule(cor_instance_id="my-instance")

# Evaluate a request
decision = judge.evaluate_request(
    user_input="Purpose: AI research. What are transformer architectures?",
    declared_purpose="AI research query"
)

# Check decision
if decision.approved:
    print(f"Request approved (Risk: {decision.risk_level.value})")
    print(f"Provenance: {decision.provenance_stamp.signature}")
else:
    print(f"Request rejected")
    for axiom in decision.violated_axioms:
        print(f"  Violated: {axiom.name}")
```

### Running the Demo

```bash
# Run demonstration
python -m judge6.main

# Run with verbose logging
python -m judge6.main --verbose
```

### Configuration

```python
from judge6.config import Judge6Config, get_config, set_config

# Create custom configuration
config = Judge6Config(
    COR_INSTANCE_ID="my-custom-instance",
    TEST_COVERAGE_TARGET=0.99
)

# Set as global configuration
set_config(config)
```

## Key Features

### Cryptographic Guarantees

Unlike competitors that rely on "aspirational language" (e.g., "NEVER do X"), Judge #6 provides:

- **Immutable Axioms**: Cannot be overridden by user input
- **Cryptographic Signatures**: Tamper-evident audit trails
- **Content-Addressable Hashing**: Proof of decision provenance
- **Deterministic Enforcement**: Rule-based, not probabilistic

### Competitive Advantages

| Feature | PNKLN Judge #6 | Anthropic Claude | OpenAI GPT | Google Gemini |
|---------|----------------|------------------|------------|---------------|
| Governance Model | Cryptographic | Aspirational | Opaque | Probabilistic |
| Risk Assessment | Pre-execution | Reactive | Implicit | Probabilistic |
| Provenance | Cryptographic | None | None | None |
| Audit Trail | Complete | None | None | None |
| Override Protection | Cryptographic | Text-based | Unknown | Unknown |

### Target Markets

- **Defense**: ATP 5-19 is DoD-native risk management
- **Healthcare**: HIPAA requires cryptographic audit trails
- **Finance**: SOX/FINRA demand provenance proof
- **Government**: FedRAMP compliance requirements

## API Reference

### JudgmentRule

Main governance engine.

#### Methods

- `evaluate_request(user_input, declared_purpose=None)` - Evaluate request through six gates
- `get_statistics()` - Get governance statistics

### YourRiskManager

ATP 5-19 risk assessment engine.

#### Methods

- `classify_request(user_input)` - Classify risk level
- `assess_axiom_violations(user_input, axioms)` - Check axiom violations

### ShadowTagEngine

Cryptographic provenance system.

#### Methods

- `generate_stamp(purpose, reasoning, risk_level, axioms_verified)` - Generate provenance
- `verify_stamp(stamp, purpose, reasoning)` - Verify stamp integrity
- `export_stamp(stamp)` - Export as JSON
- `import_stamp(json_str)` - Import from JSON

## Risk Levels (ATP 5-19)

- **RA-1 (Negligible)**: Minimal impact, routine operations
- **RA-2 (Low)**: Limited impact, easily mitigated
- **RA-3 (Moderate)**: Significant impact, requires intervention
- **RA-4 (Catastrophic)**: Severe consequences, mission failure

## Constitutional Axioms (Cor.53)

1. **A1: PURPOSE_REQUIRED** - Explicit purpose declaration mandatory
2. **A2: HARM_PROHIBITION** - No outputs facilitating harm
3. **A3: PROVENANCE_MANDATORY** - Cryptographic signatures required
4. **A4: REASONS_DOCUMENTED** - Reasoning chains signed
5. **A5: AUDIT_TRAIL** - Full provenance retained
6. **A6: NO_USER_OVERRIDE** - Axioms cannot be overridden

## Development

### Running Tests

```bash
# Run unit tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=judge6 tests/
```

### Code Quality

- **Type Hints**: Full type annotations throughout
- **Error Handling**: Comprehensive exception handling
- **Logging**: Structured logging at all levels
- **Documentation**: Docstrings for all public APIs

## License

Copyright Erik Bjontegard, Pnkln

## Version History

### 2.0.0 (Current)

- Complete refactoring into modular architecture
- Enhanced type safety and error handling
- Improved cryptographic provenance
- Configuration management system
- Comprehensive logging

### 1.0.0

- Initial monolithic implementation
- Basic six-gate evaluation
- Simplified cryptography
