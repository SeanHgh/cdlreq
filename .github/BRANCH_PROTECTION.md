# Branch Protection Setup

This repository uses GitHub Actions to automatically run tests and prevent merging of pull requests that have failing tests.

## GitHub Actions Workflows

### 1. `test.yml` - Multi-Python Version Testing
- **Triggers**: Pull requests and pushes to main branch
- **Purpose**: Runs comprehensive tests across Python versions 3.9-3.12
- **Features**:
  - Installs all dependencies including test requirements
  - Runs pytest with coverage reporting
  - Uploads coverage reports to Codecov (if configured)

### 2. `pr-checks.yml` - Pull Request Validation
- **Triggers**: Pull requests to main branch (when not draft)
- **Purpose**: Comprehensive validation before merge
- **Checks**:
  - Code formatting with ruff
  - Linting with ruff
  - Test execution with pytest
  - Test coverage validation (minimum 80%)
- **Status**: Provides single "all-checks-passed" status for branch protection

### 3. `coverage-validation.yml` - Specification Test Coverage
- **Triggers**: Pull requests to main branch (when not draft)
- **Purpose**: Ensures all specification unit test paths are executed
- **Features**:
  - Runs pytest and captures output
  - Uses `cdlreq coverage` command to analyze test execution
  - Comments on PR with detailed coverage results
  - **Blocks merge** if any specification unit tests are not executed or invalid
- **Validation**: All unit test files referenced in specifications must be executed

### 4. `branch-protection.yml` - Branch Protection Setup
- **Triggers**: Manual workflow dispatch
- **Purpose**: Automatically configure branch protection rules
- **Note**: May require admin permissions

## Manual Branch Protection Setup

If the automatic branch protection setup fails, manually configure these rules in GitHub:

1. Go to **Settings > Branches** in your repository
2. Add a branch protection rule for `main`
3. Enable these options:
   - ✅ **Require status checks to pass before merging**
   - ✅ **Require branches to be up to date before merging**
   - Required status checks:
     - `all-checks-passed` (from pr-checks.yml)
     - `coverage-validation-summary` (from coverage-validation.yml)
     - `test (3.9)` (from test.yml)
     - `test (3.10)` (from test.yml)
     - `test (3.11)` (from test.yml)
     - `test (3.12)` (from test.yml)
   - ✅ **Require a pull request before merging**
   - ✅ **Require approvals** (1 reviewer minimum)
   - ✅ **Dismiss stale reviews when new commits are pushed**
   - ✅ **Require conversation resolution before merging**
   - ✅ **Restrict pushes that create merge commits**

## Testing Locally

Before creating a pull request, run tests locally:

```bash
# Install test dependencies
pip install -e .
pip install pytest pytest-cov pytest-mock openpyxl ruff

# Run all tests
python -m pytest tests/ -v

# Check coverage
python -m pytest tests/ --cov=cdlreq --cov-report=term-missing

# Check formatting
ruff format --check .

# Run linting
ruff check .
```

## Test Coverage Requirements

- **Minimum coverage**: 80%
- **Current coverage**: 21+ tests covering models, parsers, validators, CLI commands, and integration workflows
- Tests are located in the `tests/` directory
- Simple test runner available: `python simple_test_runner.py`

## Workflow Status

The branch protection ensures that:

1. **All tests must pass** across Python 3.9-3.12
2. **Code must be properly formatted** with ruff
3. **Linting must pass** with no errors
4. **Test coverage must be ≥80%**
5. **All specification unit tests must be executed** (cdlreq coverage validation)
6. **Pull request must be approved** by at least 1 reviewer

Pull requests that fail any of these checks **cannot be merged** until issues are resolved.

## Coverage Validation Details

The `coverage-validation.yml` workflow ensures that:
- ✅ All unit test file paths referenced in specifications exist
- ✅ All unit test files referenced in specifications are executed during PR testing
- ✅ No specification has invalid or broken unit test paths
- 💬 Detailed coverage results are posted as PR comments
- ❌ **PRs are blocked** if any specification unit tests are missing or not executed

This prevents specifications from referencing non-existent or untested code files.