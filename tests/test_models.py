"""Tests for cdlreq models"""

import pytest
from cdlreq.core.models import Requirement, Specification


class TestRequirement:
    """Test Requirement model"""
    
    def test_valid_requirement(self):
        """Test creating a valid requirement"""
        req = Requirement(
            id="REQ-SYS-001",
            title="Test requirement",
            description="A test requirement for validation",
            type="functional",
            acceptance_criteria=["Criterion 1", "Criterion 2"]
        )
        assert req.id == "REQ-SYS-001"
        assert req.type == "functional"
        assert len(req.acceptance_criteria) == 2
    
    def test_invalid_requirement_id(self):
        """Test requirement with invalid ID"""
        with pytest.raises(ValueError, match="Requirement ID must start with 'REQ-'"):
            Requirement(
                id="INVALID-001",
                title="Test requirement",
                description="A test requirement",
                type="functional",
                acceptance_criteria=["Criterion 1"]
            )
    
    def test_invalid_requirement_type(self):
        """Test requirement with invalid type"""
        with pytest.raises(ValueError, match="Invalid requirement type"):
            Requirement(
                id="REQ-SYS-001",
                title="Test requirement",
                description="A test requirement",
                type="invalid_type",
                acceptance_criteria=["Criterion 1"]
            )
    
    def test_requirement_to_dict(self):
        """Test requirement to dictionary conversion"""
        req = Requirement(
            id="REQ-SYS-001",
            title="Test requirement",
            description="A test requirement",
            type="functional",
            acceptance_criteria=["Criterion 1"],
            tags=["tag1", "tag2"]
        )
        data = req.to_dict()
        assert data["id"] == "REQ-SYS-001"
        assert data["tags"] == ["tag1", "tag2"]
        assert "source" not in data  # Optional field not included if None


class TestSpecification:
    """Test Specification model"""
    
    def test_valid_specification(self):
        """Test creating a valid specification"""
        spec = Specification(
            id="SPEC-SYS-001",
            title="Test specification",
            description="A test specification",
            related_requirements=["REQ-SYS-001"],
            implementation_unit="src/test.py",
            unit_test="tests/test_test.py",
            test_criteria=["Test criterion 1"]
        )
        assert spec.id == "SPEC-SYS-001"
        assert spec.related_requirements == ["REQ-SYS-001"]
    
    def test_invalid_specification_id(self):
        """Test specification with invalid ID"""
        with pytest.raises(ValueError, match="Specification ID must start with 'SPEC-'"):
            Specification(
                id="INVALID-001",
                title="Test specification",
                description="A test specification",
                related_requirements=["REQ-SYS-001"],
                implementation_unit="src/test.py",
                unit_test="tests/test_test.py",
                test_criteria=["Test criterion 1"]
            )
    
    def test_invalid_related_requirement_id(self):
        """Test specification with invalid related requirement ID"""
        with pytest.raises(ValueError, match="Related requirement ID must start with 'REQ-'"):
            Specification(
                id="SPEC-SYS-001",
                title="Test specification",
                description="A test specification",
                related_requirements=["INVALID-001"],
                implementation_unit="src/test.py",
                unit_test="tests/test_test.py",
                test_criteria=["Test criterion 1"]
            )
    
    def test_specification_to_dict(self):
        """Test specification to dictionary conversion"""
        spec = Specification(
            id="SPEC-SYS-001",
            title="Test specification",
            description="A test specification",
            related_requirements=["REQ-SYS-001"],
            implementation_unit="src/test.py",
            unit_test="tests/test_test.py",
            test_criteria=["Test criterion 1"],
            dependencies=["SPEC-SYS-002"]
        )
        data = spec.to_dict()
        assert data["id"] == "SPEC-SYS-001"
        assert data["dependencies"] == ["SPEC-SYS-002"]
        assert "design_notes" not in data  # Optional field not included if None