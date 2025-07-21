"""Tests for cdlreq.core.parser"""

try:
    import pytest
except ImportError:
    # Create a dummy pytest module for environments without pytest
    class DummyPytest:
        @staticmethod
        def skip(reason):
            print(f"SKIP: {reason}")
    pytest = DummyPytest()

import tempfile
import yaml
from pathlib import Path
from cdlreq.core.parser import RequirementParser, SpecificationParser, ProjectParser
from cdlreq.core.models import Requirement, Specification


class TestRequirementParser:
    """Test cases for RequirementParser"""
    
    def test_create_requirement_from_data(self):
        """Test creating requirement from data dictionary"""
        parser = RequirementParser()
        data = {
            "id": "REQ-TEST-001",
            "title": "Test requirement",
            "description": "A test requirement",
            "type": "functional",
            "acceptance_criteria": ["Criteria 1"],
            "tags": ["test"]
        }
        
        req = parser.create_requirement_from_data(data)
        
        assert isinstance(req, Requirement)
        assert req.id == "REQ-TEST-001"
        assert req.title == "Test requirement"
        assert req.type == "functional"
    
    def test_parse_requirement_file(self):
        """Test parsing requirement from YAML file"""
        parser = RequirementParser()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({
                "id": "REQ-FILE-001",
                "title": "File requirement",
                "description": "A requirement from file",
                "type": "security",
                "acceptance_criteria": ["Must be secure"]
            }, f)
            temp_path = f.name
        
        try:
            req = parser.parse_requirement_file(Path(temp_path))
            assert req.id == "REQ-FILE-001"
            assert req.type == "security"
        finally:
            Path(temp_path).unlink()
    
    def test_parse_requirements_directory(self):
        """Test parsing multiple requirements from directory"""
        parser = RequirementParser()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test requirement files
            req1_data = {
                "id": "REQ-DIR-001",
                "title": "Directory req 1",
                "description": "First requirement",
                "type": "functional",
                "acceptance_criteria": ["Must work functionally"]
            }
            req2_data = {
                "id": "REQ-DIR-002", 
                "title": "Directory req 2",
                "description": "Second requirement",
                "type": "security",
                "acceptance_criteria": ["Must be secure"]
            }
            
            with open(temp_path / "req1.yaml", 'w') as f:
                yaml.dump(req1_data, f)
            with open(temp_path / "req2.yaml", 'w') as f:
                yaml.dump(req2_data, f)
            
            requirements = parser.parse_requirements_directory(temp_path)
            
            assert len(requirements) == 2
            req_ids = [req.id for req in requirements]
            assert "REQ-DIR-001" in req_ids
            assert "REQ-DIR-002" in req_ids


class TestSpecificationParser:
    """Test cases for SpecificationParser"""
    
    def test_create_specification_from_data(self):
        """Test creating specification from data dictionary"""
        parser = SpecificationParser()
        data = {
            "id": "SPEC-TEST-001",
            "title": "Test specification",
            "description": "A test specification",
            "related_requirements": ["REQ-001"],
            "implementation_unit": "src/test.py",
            "unit_test": "tests/test_test.py"
        }
        
        spec = parser.create_specification_from_data(data)
        
        assert isinstance(spec, Specification)
        assert spec.id == "SPEC-TEST-001"
        assert spec.related_requirements == ["REQ-001"]
        assert spec.implementation_unit == "src/test.py"
    
    def test_parse_specification_file(self):
        """Test parsing specification from YAML file"""
        parser = SpecificationParser()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({
                "id": "SPEC-FILE-001",
                "title": "File specification",
                "description": "A specification from file",
                "related_requirements": ["REQ-FILE-001"],
                "implementation_unit": "src/file.py",
                "unit_test": "tests/test_file.py",
                "design_notes": "Important notes"
            }, f)
            temp_path = f.name
        
        try:
            spec = parser.parse_specification_file(Path(temp_path))
            assert spec.id == "SPEC-FILE-001"
            assert spec.design_notes == "Important notes"
        finally:
            Path(temp_path).unlink()
    
    def test_parse_specifications_directory(self):
        """Test parsing multiple specifications from directory"""
        parser = SpecificationParser()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create specifications subdirectory
            spec_dir = temp_path / "specifications"
            spec_dir.mkdir()
            
            spec1_data = {
                "id": "SPEC-DIR-001",
                "title": "Directory spec 1", 
                "description": "First specification",
                "related_requirements": ["REQ-001"],
                "implementation_unit": "src/spec1.py",
                "unit_test": "tests/test_spec1.py"
            }
            
            with open(spec_dir / "spec1.yaml", 'w') as f:
                yaml.dump(spec1_data, f)
            
            specifications = parser.parse_specifications_directory(temp_path)
            
            assert len(specifications) == 1
            assert specifications[0].id == "SPEC-DIR-001"


class TestProjectParser:
    """Test cases for ProjectParser"""
    
    def test_parse_project(self):
        """Test parsing complete project structure"""
        parser = ProjectParser()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create requirements directory and file
            req_dir = temp_path / "requirements"
            req_dir.mkdir()
            
            req_data = {
                "id": "REQ-PROJ-001",
                "title": "Project requirement",
                "description": "A project requirement",
                "type": "functional",
                "acceptance_criteria": ["Must work in project"]
            }
            
            with open(req_dir / "requirement.yaml", 'w') as f:
                yaml.dump(req_data, f)
            
            # Create specifications subdirectory and file
            spec_dir = req_dir / "specifications"
            spec_dir.mkdir()
            
            spec_data = {
                "id": "SPEC-PROJ-001",
                "title": "Project specification",
                "description": "A project specification",
                "related_requirements": ["REQ-PROJ-001"],
                "implementation_unit": "src/proj.py",
                "unit_test": "tests/test_proj.py"
            }
            
            with open(spec_dir / "specification.yaml", 'w') as f:
                yaml.dump(spec_data, f)
            
            result = parser.parse_project(temp_path)
            
            assert "requirements" in result
            assert "specifications" in result
            assert len(result["requirements"]) == 1
            assert len(result["specifications"]) == 1
            assert result["requirements"][0].id == "REQ-PROJ-001"
            assert result["specifications"][0].id == "SPEC-PROJ-001"