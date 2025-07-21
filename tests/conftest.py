"""Pytest configuration and shared fixtures for cdlreq tests"""

try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False
    # Create a dummy pytest module
    class DummyPytest:
        @staticmethod
        def fixture(*args, **kwargs):
            def decorator(func):
                return func
            return decorator
        
        @staticmethod
        def skip(reason):
            print(f"SKIP: {reason}")
    
    pytest = DummyPytest()

import tempfile
import yaml
from pathlib import Path
from cdlreq.core.models import Requirement, Specification


@pytest.fixture
def temp_dir():
    """Provide a temporary directory for tests"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_requirement():
    """Provide a sample requirement for testing"""
    return Requirement(
        id="REQ-SAMPLE-001",
        title="Sample Requirement",
        description="A sample requirement for testing purposes",
        type="functional",
        acceptance_criteria=["Criteria 1", "Criteria 2"],
        tags=["sample", "test"]
    )


@pytest.fixture 
def sample_specification():
    """Provide a sample specification for testing"""
    return Specification(
        id="SPEC-SAMPLE-001",
        title="Sample Specification",
        description="A sample specification for testing purposes",
        related_requirements=["REQ-SAMPLE-001"],
        implementation_unit="src/sample.py",
        unit_test="tests/test_sample.py",
        design_notes="Sample design notes"
    )


@pytest.fixture
def project_structure(temp_dir):
    """Create a complete project structure for testing"""
    # Create directories
    req_dir = temp_dir / "requirements"
    req_dir.mkdir()
    spec_dir = req_dir / "specifications"
    spec_dir.mkdir()
    
    # Create sample requirement
    req_data = {
        "id": "REQ-PROJ-001",
        "title": "Project Test Requirement",
        "description": "A requirement for project testing",
        "type": "security",
        "acceptance_criteria": ["Must be secure", "Must be fast"],
        "tags": ["security", "performance"]
    }
    
    req_file = req_dir / "test_requirement.yaml"
    with open(req_file, 'w') as f:
        yaml.dump(req_data, f)
    
    # Create sample specification
    spec_data = {
        "id": "SPEC-PROJ-001", 
        "title": "Project Test Specification",
        "description": "A specification for project testing",
        "related_requirements": ["REQ-PROJ-001"],
        "implementation_unit": "src/project_test.py",
        "unit_test": "tests/test_project_test.py",
        "design_notes": "Important design considerations"
    }
    
    spec_file = spec_dir / "test_specification.yaml"
    with open(spec_file, 'w') as f:
        yaml.dump(spec_data, f)
    
    return {
        "base_dir": temp_dir,
        "req_dir": req_dir,
        "spec_dir": spec_dir,
        "req_file": req_file,
        "spec_file": spec_file
    }


@pytest.fixture
def test_output_content():
    """Provide sample test output content for coverage testing"""
    return """============================= test session starts ==============================
platform linux -- Python 3.11.0, pytest-7.4.0, pluggy-1.2.0
rootdir: /project
collected 12 items

tests/auth/test_oauth_auth.py::test_oauth_login_valid PASSED                [ 8%]
tests/auth/test_oauth_auth.py::test_oauth_login_invalid PASSED             [16%]
tests/auth/test_oauth_auth.py::test_oauth_logout PASSED                    [25%]
tests/security/test_rbac.py::test_rbac_admin_access PASSED                 [33%]
tests/security/test_rbac.py::test_rbac_user_access PASSED                  [41%]
tests/security/test_rbac.py::test_rbac_denied_access FAILED                [50%]
tests/performance/test_metrics.py::test_response_time PASSED               [58%]
tests/performance/test_metrics.py::test_throughput PASSED                  [66%]
tests/data/test_encryption.py::test_encrypt_data PASSED                    [75%]
tests/data/test_encryption.py::test_decrypt_data PASSED                    [83%]
tests/audit/test_logging.py::test_audit_log_creation PASSED                [91%]
tests/audit/test_logging.py::test_audit_log_retrieval FAILED               [100%]

=========================== FAILURES ===========================
FAILED tests/security/test_rbac.py::test_rbac_denied_access - AssertionError: Access should be denied
FAILED tests/audit/test_logging.py::test_audit_log_retrieval - KeyError: 'timestamp'

=========================== short test summary info ============================
FAILED tests/security/test_rbac.py::test_rbac_denied_access - AssertionError
FAILED tests/audit/test_logging.py::test_audit_log_retrieval - KeyError
========================= 2 failed, 10 passed in 2.34s ========================="""


@pytest.fixture
def invalid_yaml_content():
    """Provide invalid YAML content for error testing"""
    return """
    id: "REQ-INVALID-001"
    title: "Invalid YAML"
    description: "This YAML has invalid syntax
    type: functional
    # Missing closing quote and colon issues
    """


@pytest.fixture  
def multiple_requirements_data():
    """Provide data for multiple requirements"""
    return [
        {
            "id": "REQ-MULTI-001",
            "title": "First Multi Requirement",
            "description": "First requirement in multi-test",
            "type": "functional"
        },
        {
            "id": "REQ-MULTI-002", 
            "title": "Second Multi Requirement",
            "description": "Second requirement in multi-test",
            "type": "security"
        },
        {
            "id": "REQ-MULTI-003",
            "title": "Third Multi Requirement", 
            "description": "Third requirement in multi-test",
            "type": "performance"
        }
    ]


@pytest.fixture
def multiple_specifications_data():
    """Provide data for multiple specifications"""
    return [
        {
            "id": "SPEC-MULTI-001",
            "title": "First Multi Specification",
            "description": "First specification in multi-test",
            "related_requirements": ["REQ-MULTI-001"],
            "implementation_unit": "src/multi1.py",
            "unit_test": "tests/test_multi1.py"
        },
        {
            "id": "SPEC-MULTI-002",
            "title": "Second Multi Specification",
            "description": "Second specification in multi-test", 
            "related_requirements": ["REQ-MULTI-002", "REQ-MULTI-003"],
            "implementation_unit": "src/multi2.py",
            "unit_test": "tests/test_multi2.py",
            "design_notes": "Complex implementation notes"
        }
    ]