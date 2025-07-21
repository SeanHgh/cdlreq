# cdlreq Tests

This directory contains comprehensive unit and integration tests for cdlreq.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                 # Pytest configuration and shared fixtures
├── README.md                   # This file
├── test_integration.py         # End-to-end integration tests
├── core/                      # Tests for core functionality
│   ├── __init__.py
│   ├── test_models.py         # Tests for Requirement and Specification models
│   ├── test_parser.py         # Tests for YAML parsing functionality
│   └── test_validator.py      # Tests for validation logic
├── cli/                       # Tests for CLI commands
│   ├── __init__.py
│   └── test_commands.py       # Tests for all CLI commands
└── fixtures/                  # Test data files
    ├── __init__.py
    ├── sample_requirement.yaml
    ├── sample_specification.yaml
    └── test_output.txt
```

## Running Tests

### Prerequisites

Install test dependencies:
```bash
pip install -e ".[test]"
# or for development
pip install -e ".[dev]"
```

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/core/test_models.py

# Run specific test class
pytest tests/core/test_models.py::TestRequirement

# Run specific test method
pytest tests/core/test_models.py::TestRequirement::test_requirement_creation
```

### Using the Test Runner Script

```bash
# Run all tests
python run_tests.py

# Run only unit tests
python run_tests.py --unit

# Run only integration tests  
python run_tests.py --integration

# Run only CLI tests
python run_tests.py --cli

# Run fast tests (exclude slow ones)
python run_tests.py --fast

# Run with coverage report
python run_tests.py --coverage
```

### Test Categories

Tests are marked with the following categories:

- `unit` - Unit tests for individual components
- `integration` - Integration tests that test multiple components together
- `cli` - Tests for CLI commands
- `slow` - Tests that take longer to run (can be excluded with `-m "not slow"`)

### Coverage Reports

To generate coverage reports:

```bash
# Terminal coverage report
pytest --cov=cdlreq --cov-report=term

# HTML coverage report 
pytest --cov=cdlreq --cov-report=html
# Open htmlcov/index.html in browser

# Both terminal and HTML
python run_tests.py --coverage
```

## Test Data and Fixtures

### Shared Fixtures

The `conftest.py` file provides shared fixtures used across tests:

- `temp_dir` - Temporary directory for file operations
- `sample_requirement` - Sample Requirement object
- `sample_specification` - Sample Specification object  
- `project_structure` - Complete project directory structure with files
- `test_output_content` - Sample test execution output for coverage testing
- `multiple_requirements_data` - Data for testing multiple requirements
- `multiple_specifications_data` - Data for testing multiple specifications

### Test Fixtures Directory

The `fixtures/` directory contains static test data files:

- `sample_requirement.yaml` - Example requirement YAML
- `sample_specification.yaml` - Example specification YAML  
- `test_output.txt` - Example test execution output

## Writing New Tests

### Unit Test Guidelines

1. **Test one thing at a time** - Each test should focus on a single behavior
2. **Use descriptive names** - Test names should clearly describe what is being tested
3. **Follow AAA pattern** - Arrange, Act, Assert
4. **Use fixtures** - Reuse common test data and setup via fixtures
5. **Mock external dependencies** - Use `pytest-mock` for mocking external calls

### Example Unit Test

```python
def test_requirement_creation(self):
    """Test creating a basic requirement"""
    # Arrange
    req_data = {
        "id": "REQ-001",
        "title": "Test Requirement", 
        "description": "A test requirement",
        "type": "functional"
    }
    
    # Act
    req = Requirement(**req_data)
    
    # Assert
    assert req.id == "REQ-001"
    assert req.title == "Test Requirement"
    assert req.type == "functional"
```

### Integration Test Guidelines

1. **Test workflows** - Test complete user workflows end-to-end
2. **Use realistic data** - Use data that resembles real usage
3. **Test error conditions** - Ensure proper error handling
4. **Mark as integration** - Use `@pytest.mark.integration` decorator

### CLI Test Guidelines

1. **Use CliRunner** - Use Click's CliRunner for testing CLI commands
2. **Test both success and failure paths** - Test valid and invalid inputs
3. **Check exit codes** - Verify proper exit codes are returned
4. **Verify output** - Check that expected messages appear in output

## Continuous Integration

Tests are designed to run in CI environments. The test suite:

- Runs on multiple Python versions (3.8+)
- Uses temporary directories for file operations
- Handles missing optional dependencies gracefully
- Provides clear pass/fail indicators

## Troubleshooting

### Common Issues

1. **Missing dependencies** - Install test dependencies with `pip install -e ".[test]"`
2. **Path issues** - Tests use absolute paths and temporary directories
3. **Permission errors** - Tests create/modify files in temp directories only
4. **Import errors** - Make sure cdlreq is installed in development mode (`pip install -e .`)

### Debug Mode

Run tests with additional debugging:

```bash
# Show all output (don't capture)
pytest -s

# Drop into debugger on failures
pytest --pdb

# Show local variables in tracebacks  
pytest -l
```