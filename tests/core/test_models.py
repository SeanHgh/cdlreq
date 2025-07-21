"""Tests for cdlreq.core.models"""

try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False
    # Create a dummy pytest module for environments without pytest
    class DummyPytest:
        @staticmethod
        def skip(reason):
            print(f"SKIP: {reason}")
    pytest = DummyPytest()

from cdlreq.core.models import Requirement, Specification


class TestRequirement:
    """Test cases for Requirement model"""
    
    def test_requirement_creation(self):
        """Test creating a basic requirement"""
        req = Requirement(
            id="REQ-001",
            title="Test Requirement",
            description="A test requirement",
            type="functional",
            acceptance_criteria=[]  # This is required in the dataclass
        )
        
        assert req.id == "REQ-001"
        assert req.title == "Test Requirement"
        assert req.description == "A test requirement"
        assert req.type == "functional"
        assert req.acceptance_criteria == []
        assert req.tags == []
    
    def test_requirement_with_optional_fields(self):
        """Test creating a requirement with all fields"""
        req = Requirement(
            id="REQ-002",
            title="Complex Requirement",
            description="A complex requirement",
            type="security",
            acceptance_criteria=["Criteria 1", "Criteria 2"],
            tags=["auth", "security"]
        )
        
        assert req.acceptance_criteria == ["Criteria 1", "Criteria 2"]
        assert req.tags == ["auth", "security"]
    
    def test_requirement_to_dict(self):
        """Test requirement serialization to dictionary"""
        req = Requirement(
            id="REQ-003",
            title="Dict Test",
            description="Testing dict conversion",
            type="functional",
            acceptance_criteria=["Test criteria"],
            tags=["test"]
        )
        
        result = req.to_dict()
        expected_keys = {"id", "title", "description", "type", "acceptance_criteria", "tags"}
        
        # Check that required keys are present
        assert all(key in result for key in ["id", "title", "description", "type", "acceptance_criteria"])
        assert result["id"] == "REQ-003"
        assert result["title"] == "Dict Test"
        assert result["type"] == "functional"
        assert result["acceptance_criteria"] == ["Test criteria"]


class TestSpecification:
    """Test cases for Specification model"""
    
    def test_specification_creation(self):
        """Test creating a basic specification"""
        spec = Specification(
            id="SPEC-001",
            title="Test Spec",
            description="A test specification",
            related_requirements=["REQ-001"],
            implementation_unit="src/test.py",
            unit_test="tests/test_test.py"
        )
        
        assert spec.id == "SPEC-001"
        assert spec.title == "Test Spec"
        assert spec.description == "A test specification"
        assert spec.related_requirements == ["REQ-001"]
        assert spec.implementation_unit == "src/test.py"
        assert spec.unit_test == "tests/test_test.py"
        assert spec.design_notes is None
    
    def test_specification_with_design_notes(self):
        """Test creating a specification with design notes"""
        spec = Specification(
            id="SPEC-002",
            title="Complex Spec",
            description="A complex specification",
            related_requirements=["REQ-001", "REQ-002"],
            implementation_unit="src/complex.py",
            unit_test="tests/test_complex.py",
            design_notes="Important design considerations"
        )
        
        assert spec.design_notes == "Important design considerations"
        assert len(spec.related_requirements) == 2
    
    def test_specification_to_dict(self):
        """Test specification serialization to dictionary"""
        spec = Specification(
            id="SPEC-003",
            title="Dict Spec",
            description="Testing dict conversion",
            related_requirements=["REQ-003"],
            implementation_unit="src/dict.py",
            unit_test="tests/test_dict.py",
            design_notes="Test notes"
        )
        
        result = spec.to_dict()
        
        # Check that required keys are present
        assert all(key in result for key in ["id", "title", "description", "related_requirements", "implementation_unit", "unit_test"])
        assert result["id"] == "SPEC-003"
        assert result["title"] == "Dict Spec"
        assert result["related_requirements"] == ["REQ-003"]
        assert result["design_notes"] == "Test notes"
    
    def test_specification_without_design_notes_dict(self):
        """Test specification dict conversion without design notes"""
        spec = Specification(
            id="SPEC-004",
            title="No Notes Spec",
            description="Spec without design notes",
            related_requirements=["REQ-004"],
            implementation_unit="src/no_notes.py",
            unit_test="tests/test_no_notes.py"
        )
        
        result = spec.to_dict()
        
        # Check required fields are present
        assert result["id"] == "SPEC-004"
        assert result["title"] == "No Notes Spec"
        assert result["related_requirements"] == ["REQ-004"]
        # design_notes should not be in dict when None (according to the actual implementation)
        assert "design_notes" not in result or result.get("design_notes") is None