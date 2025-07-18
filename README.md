# cdlreq

A Python library and CLI for managing medical software requirements and specifications using YAML files stored alongside source code.

## Features

- **YAML-based**: Requirements and specifications stored in structured YAML files
- **Traceability**: Link requirements to specifications, implementation units, and tests
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

Validate all files:
```bash
cdlreq validate
```

## YAML Structure

### Requirements
- `id`: Unique identifier
- `title`: Brief description
- `description`: Detailed description
- `type`: functional, security, performance, usability, etc.
- `tags`: List of tags
- `acceptance_criteria`: List of acceptance criteria

### Specifications  
- `id`: Unique identifier
- `title`: Brief description
- `description`: Detailed description
- `related_requirements`: List of requirement IDs
- `implementation_unit`: Path to source code file/module
- `unit_test`: Path to test file/function
- `test_criteria`: List of test criteria