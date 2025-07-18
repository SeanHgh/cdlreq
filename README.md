# cdlreq

A Python library and CLI for managing medical software requirements and specifications using YAML files stored alongside source code.

## Features

- **YAML-based**: Requirements and specifications stored in structured YAML files
- **Traceability**: Link requirements to specifications, implementation units, and tests
- **Interactive Selection**: Use keyboard navigation to select existing requirements when creating specifications
- **Validation**: Schema validation ensures data integrity
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

Create a new specification with interactive requirement selection:
```bash
cdlreq create specification
```
The CLI will show existing requirements and let you select them using keyboard navigation.

Validate all files:
```bash
cdlreq validate
```

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
- `unit_test`: Path to test file/function
- `test_criteria`: List of test criteria

Files are automatically identified by their ID prefix - no special file naming conventions required.