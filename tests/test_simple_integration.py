"""Simple integration tests that don't require external dependencies"""

import tempfile
import yaml
from pathlib import Path
from cdlreq.core.models import Requirement, Specification
from cdlreq.core.parser import ProjectParser


class TestSimpleIntegration:
    """Simple integration tests"""
    
    def test_complete_workflow_without_cli(self):
        """Test complete workflow without CLI dependencies"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create project structure
            req_dir = temp_path / "requirements"
            req_dir.mkdir()
            spec_dir = req_dir / "specifications"
            spec_dir.mkdir()
            
            # Create requirement manually
            req_data = {
                "id": "REQ-INTEGRATION-001",
                "title": "Integration Test Requirement",
                "description": "A requirement for integration testing",
                "type": "functional",
                "acceptance_criteria": ["Must integrate properly"],
                "tags": ["integration", "test"]
            }
            
            with open(req_dir / "integration_req.yaml", 'w') as f:
                yaml.dump(req_data, f)
            
            # Create specification manually
            spec_data = {
                "id": "SPEC-INTEGRATION-001",
                "title": "Integration Test Specification",
                "description": "A specification for integration testing",
                "related_requirements": ["REQ-INTEGRATION-001"],
                "implementation_unit": "src/integration.py",
                "unit_test": "tests/test_integration.py",
                "design_notes": "Integration design notes"
            }
            
            with open(spec_dir / "integration_spec.yaml", 'w') as f:
                yaml.dump(spec_data, f)
            
            # Test parsing the project
            parser = ProjectParser()
            result = parser.parse_project(temp_path)
            
            # Verify results
            assert "requirements" in result
            assert "specifications" in result
            assert len(result["requirements"]) == 1
            assert len(result["specifications"]) == 1
            
            req = result["requirements"][0]
            assert req.id == "REQ-INTEGRATION-001"
            assert req.type == "functional"
            assert "integration" in req.tags
            
            spec = result["specifications"][0]
            assert spec.id == "SPEC-INTEGRATION-001"
            assert "REQ-INTEGRATION-001" in spec.related_requirements
            assert spec.unit_test == "tests/test_integration.py"
    
    def test_model_creation_and_serialization(self):
        """Test model creation and serialization roundtrip"""
        # Create requirement
        req = Requirement(
            id="REQ-ROUNDTRIP-001",
            title="Roundtrip Test",
            description="Testing serialization roundtrip",
            type="functional",
            acceptance_criteria=["Must roundtrip correctly"],
            tags=["test", "roundtrip"]
        )
        
        # Convert to dict
        req_dict = req.to_dict()
        
        # Verify dict structure
        assert req_dict["id"] == "REQ-ROUNDTRIP-001"
        assert req_dict["type"] == "functional"
        assert "Must roundtrip correctly" in req_dict["acceptance_criteria"]
        
        # Create specification
        spec = Specification(
            id="SPEC-ROUNDTRIP-001",
            title="Roundtrip Spec Test",
            description="Testing spec serialization roundtrip",
            related_requirements=["REQ-ROUNDTRIP-001"],
            implementation_unit="src/roundtrip.py",
            unit_test="tests/test_roundtrip.py",
            design_notes="Roundtrip design"
        )
        
        # Convert to dict
        spec_dict = spec.to_dict()
        
        # Verify dict structure
        assert spec_dict["id"] == "SPEC-ROUNDTRIP-001"
        assert "REQ-ROUNDTRIP-001" in spec_dict["related_requirements"]
        assert spec_dict["design_notes"] == "Roundtrip design"
        assert spec_dict["unit_test"] == "tests/test_roundtrip.py"
    
    def test_error_handling(self):
        """Test error handling for invalid data"""
        # Test invalid requirement ID
        try:
            req = Requirement(
                id="INVALID-001",  # Should start with REQ-
                title="Invalid Requirement",
                description="This should fail",
                type="functional",
                acceptance_criteria=[]
            )
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "REQ-" in str(e)
        
        # Test invalid requirement type
        try:
            req = Requirement(
                id="REQ-INVALID-002",
                title="Invalid Type Requirement",
                description="This should fail",
                type="invalid_type",
                acceptance_criteria=[]
            )
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Invalid requirement type" in str(e)
        
        # Test invalid specification ID
        try:
            spec = Specification(
                id="INVALID-001",  # Should start with SPEC-
                title="Invalid Specification",
                description="This should fail",
                related_requirements=["REQ-001"],
                implementation_unit="src/invalid.py",
                unit_test="tests/test_invalid.py"
            )
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "SPEC-" in str(e)