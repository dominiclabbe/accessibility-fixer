# Tests

This directory contains unit tests for the accessibility-fixer GitHub App.

## Running Tests

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_diff_parser.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

## Test Files

### test_diff_parser.py (21 tests)

Tests for the `DiffParser` class and related utilities:

- **Diff parsing**: Parse unified diffs into per-file sections
- **File filtering**: Filter diffs to specific files
- **Line mapping**: Extract commentable lines from diffs
- **Line adjustment**: Find nearest commentable line
- **Validation**: Validate issues are in batch and on commentable lines
- **Placeholder detection**: Detect "no issues" placeholder comments

**Key test cases:**
- Single file and multi-file diff parsing
- Accurate commentable line extraction
- Android XML layout diff handling
- Issue validation and adjustment
- Placeholder issue filtering

### test_sarif_generator.py (12 tests)

Tests for the `SARIFGenerator` class:

- **SARIF structure**: Generate valid SARIF 2.1.0 reports
- **Rule generation**: Create rules from WCAG Success Criteria
- **Result mapping**: Map issues to SARIF results
- **Severity conversion**: Map severity levels to SARIF levels
- **File I/O**: Write SARIF to files with directory creation
- **Repository provenance**: Include repo URI and commit SHA

**Key test cases:**
- Empty and populated issue lists
- Severity to SARIF level mapping
- Multiple WCAG SCs in single report
- Issues without WCAG SC (generic rule)
- File writing with nested directories

## Test Coverage

Current coverage (as of latest commit):

- `app/diff_parser.py`: 95%+
- `app/sarif_generator.py`: 95%+

## Adding New Tests

When adding new functionality:

1. **Create test file** in `tests/` following naming convention `test_<module>.py`
2. **Use pytest conventions** with test classes and test_ prefixed functions
3. **Add fixtures** at module level for reusable test data
4. **Test edge cases** including empty inputs, invalid data, errors
5. **Document tests** with clear docstrings explaining what's being tested
6. **Update this README** with new test file descriptions

Example test structure:

```python
"""
Tests for MyNewModule

Description of what this module does.
"""

import pytest
from app.my_new_module import MyClass

# Test fixtures
SAMPLE_DATA = "..."

class TestMyClass:
    """Tests for MyClass."""
    
    def test_basic_functionality(self):
        """Test basic use case."""
        obj = MyClass()
        result = obj.do_something(SAMPLE_DATA)
        assert result == expected
    
    def test_edge_case(self):
        """Test edge case handling."""
        obj = MyClass()
        result = obj.do_something(None)
        assert result is None
```

## Continuous Integration

These tests should be run in CI/CD pipelines:

```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements-app.txt -r requirements-dev.txt
      - run: pytest tests/ -v --cov=app --cov-report=xml
      - uses: codecov/codecov-action@v3
```

## Test Philosophy

- **Fast**: Tests should run quickly (<1s per test typically)
- **Isolated**: Each test should be independent
- **Readable**: Clear test names and docstrings
- **Comprehensive**: Cover happy path, edge cases, and errors
- **Maintainable**: Use fixtures and helpers to reduce duplication

## Debugging Tests

```bash
# Run with verbose output
pytest tests/ -v -s

# Run specific test
pytest tests/test_diff_parser.py::TestDiffParser::test_parse_diff_single_file -v

# Drop into debugger on failure
pytest tests/ --pdb

# Show local variables on failure
pytest tests/ -l
```

## Test Data

Test fixtures and sample data are defined inline in test files for clarity. For larger fixtures, consider:

1. Creating `tests/fixtures/` directory
2. Loading from JSON/text files
3. Using `pytest.fixture` decorator for reusable setup

## Mocking

For tests that interact with external services:

```python
from unittest.mock import Mock, patch

def test_with_mock():
    with patch('app.module.external_call') as mock_call:
        mock_call.return_value = "mocked result"
        # Test code that calls external_call
```

Currently, our tests don't require mocking as they test pure logic functions.
