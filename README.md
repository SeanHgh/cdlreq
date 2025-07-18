# cdlreq

A Python library and CLI for managing medical software requirements and specifications using YAML files stored alongside source code.

## Features

- **YAML-based**: Requirements and specifications stored in structured YAML files
- **Traceability**: Link requirements to specifications, implementation units, and tests
- **Interactive Selection**: Select existing requirements by number when creating specifications
- **Validation**: Schema validation ensures data integrity
- **Excel Export**: Generate traceability matrix in Excel format for compliance documentation
- **CLI Interface**: Command-line tools for common operations
- **Python Library**: Programmatic access to requirements and specifications

## Installation

```bash
pip install cdlreq
```

## Quick Start

Initialize a new project:
```bash
cdlreq init
```

Create a new requirement:
```bash
cdlreq create requirement --type functional
```
You'll be prompted to enter the ID suffix (e.g., "SYS-001") and the "REQ-" prefix will be added automatically.

Create a new specification with interactive requirement selection:
```bash
cdlreq create specification
```
The CLI will show existing requirements and let you select them by number (e.g., '1,3,5' or '1-3,5').
You'll be prompted to enter the ID suffix (e.g., "SYS-001") and the "SPEC-" prefix will be added automatically.

Validate all files:
```bash
cdlreq validate
```

Export traceability matrix to Excel:
```bash
cdlreq export --output traceability_matrix.xlsx
```
Creates an Excel file with requirements, specifications, and a traceability matrix showing relationships.

Check unit test coverage for specifications:
```bash
# Create a file listing all executed tests
echo "tests/auth/test_oauth_service.py" > test_list.txt
echo "tests/security/test_encryption_service.py" >> test_list.txt
# Or include specific test functions
echo "tests/auth/test_oauth_service.py::test_token_generation" >> test_list.txt
echo "tests/auth/test_oauth_service.py::test_token_refresh" >> test_list.txt

# Check coverage
cdlreq coverage test_list.txt
```
Analyzes the test list to ensure all specification unit tests are being executed. The command performs function-level analysis, scanning test files for test functions (starting with `test_`) and checking which specific functions are covered by the test list.

## Directory Structure

After initialization, your project will have this structure:
```
project/
├── requirements/
│   ├── requirement_files.yaml
│   └── specifications/
│       └── specification_files.yaml
```

Requirements and specifications are organized with specs nested under requirements for better organization.

## YAML Structure

### Requirements (REQ-XXX-###)
- `id`: Unique identifier starting with "REQ-"
- `title`: Brief description
- `description`: Detailed description
- `type`: functional, security, performance, usability, etc.
- `tags`: List of tags
- `acceptance_criteria`: List of acceptance criteria

### Specifications (SPEC-XXX-###)
- `id`: Unique identifier starting with "SPEC-"
- `title`: Brief description
- `description`: Detailed description
- `related_requirements`: List of requirement IDs
- `implementation_unit`: Path to source code file/module
- `unit_test`: Path to unit test file/function
- `design_notes`: Design notes and considerations (optional)
- `dependencies`: List of dependent specification IDs (optional)

Files are automatically identified by their ID prefix - no special file naming conventions required.