# Contributing to Meta Lead Quality Analyzer

Thank you for your interest in contributing to `meta-lead-quality-analyzer`! We welcome contributions from growth marketers, performance media buyers, data analysts, and software engineers.

---

## Local Development Workflow

1. **Clone the repository**:
   ```bash
   git clone https://github.com/hamid-digitalmarketer/meta-lead-quality-analyzer.git
   cd meta-lead-quality-analyzer
   ```

2. **Setup virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install development dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

---

## Code Quality Standards

```bash
# Run unit tests
pytest

# Check code formatting & linting
ruff check .

# Run static type checking
mypy src
```
