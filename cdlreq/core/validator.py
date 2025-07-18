"""Schema validation for requirements and specifications"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, List
from jsonschema import validate, ValidationError, Draft7Validator
from .models import Requirement, Specification


class ValidationResult:
    """Result of validation operation"""
    def __init__(self, is_valid: bool, errors: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []
    
    def __bool__(self) -> bool:
        return self.is_valid


class BaseValidator:
    """Base class for validators"""
    
    def __init__(self, schema_path: Path):
        self.schema_path = schema_path
        self._schema = None
    
    @property
    def schema(self) -> Dict[str, Any]:
        """Load and cache schema"""
        if self._schema is None:
            with open(self.schema_path, 'r') as f:
                self._schema = yaml.safe_load(f)
        return self._schema
    
    def validate_data(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate data against schema"""
        try:
            validate(instance=data, schema=self.schema)
            return ValidationResult(True)
        except ValidationError as e:
            return ValidationResult(False, [str(e)])
    
    def validate_file(self, file_path: Path) -> ValidationResult:
        """Validate YAML file against schema"""
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
            return self.validate_data(data)
        except Exception as e:
            return ValidationResult(False, [f"Error reading file: {str(e)}"])


class RequirementValidator(BaseValidator):
    """Validator for requirement files"""
    
    def __init__(self):
        schema_path = Path(__file__).parent.parent / "schemas" / "requirement.yaml"
        super().__init__(schema_path)
    
    def validate_requirement(self, requirement: Requirement) -> ValidationResult:
        """Validate a requirement object"""
        return self.validate_data(requirement.to_dict())


class SpecificationValidator(BaseValidator):
    """Validator for specification files"""
    
    def __init__(self):
        schema_path = Path(__file__).parent.parent / "schemas" / "specification.yaml"
        super().__init__(schema_path)
    
    def validate_specification(self, specification: Specification) -> ValidationResult:
        """Validate a specification object"""
        return self.validate_data(specification.to_dict())


class CrossReferenceValidator:
    """Validator for cross-references between requirements and specifications"""
    
    def __init__(self, requirements: List[Requirement], specifications: List[Specification]):
        self.requirements = {req.id: req for req in requirements}
        self.specifications = {spec.id: spec for spec in specifications}
    
    def validate_cross_references(self) -> ValidationResult:
        """Validate cross-references between requirements and specifications"""
        errors = []
        
        # Check that all referenced requirements exist
        for spec in self.specifications.values():
            for req_id in spec.related_requirements:
                if req_id not in self.requirements:
                    errors.append(f"Specification {spec.id} references non-existent requirement {req_id}")
        
        # Check that all specification dependencies exist
        for spec in self.specifications.values():
            for dep_id in spec.dependencies:
                if dep_id not in self.specifications:
                    errors.append(f"Specification {spec.id} depends on non-existent specification {dep_id}")
        
        # Check for circular dependencies
        circular_deps = self._find_circular_dependencies()
        if circular_deps:
            errors.extend([f"Circular dependency detected: {' -> '.join(cycle)}" for cycle in circular_deps])
        
        return ValidationResult(len(errors) == 0, errors)
    
    def _find_circular_dependencies(self) -> List[List[str]]:
        """Find circular dependencies in specifications"""
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(spec_id: str, path: List[str]) -> None:
            if spec_id in rec_stack:
                cycle_start = path.index(spec_id)
                cycles.append(path[cycle_start:] + [spec_id])
                return
            
            if spec_id in visited:
                return
            
            visited.add(spec_id)
            rec_stack.add(spec_id)
            
            if spec_id in self.specifications:
                for dep_id in self.specifications[spec_id].dependencies:
                    dfs(dep_id, path + [spec_id])
            
            rec_stack.remove(spec_id)
        
        for spec_id in self.specifications:
            if spec_id not in visited:
                dfs(spec_id, [])
        
        return cycles