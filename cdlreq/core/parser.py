"""YAML parsing for requirements and specifications"""

import yaml
from pathlib import Path
from typing import List, Dict, Any, Union
from .models import Requirement, Specification
from .validator import RequirementValidator, SpecificationValidator


class ParseError(Exception):
    """Exception raised when parsing fails"""

    pass


class BaseParser:
    """Base class for parsers"""

    def __init__(self):
        self.validator = None

    def parse_yaml_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse YAML file and return data"""
        try:
            with open(file_path, "r") as f:
                data = yaml.safe_load(f)
            if not isinstance(data, dict):
                raise ParseError(f"YAML file must contain a dictionary: {file_path}")
            return data
        except yaml.YAMLError as e:
            raise ParseError(f"Invalid YAML syntax in {file_path}: {e}")
        except Exception as e:
            raise ParseError(f"Error reading file {file_path}: {e}")


class RequirementParser(BaseParser):
    """Parser for requirement files"""

    def __init__(self):
        super().__init__()
        self.validator = RequirementValidator()

    def parse_requirement_file(self, file_path: Path) -> Requirement:
        """Parse requirement YAML file"""
        data = self.parse_yaml_file(file_path)

        # Validate against schema
        validation_result = self.validator.validate_data(data)
        if not validation_result.is_valid:
            raise ParseError(
                f"Validation failed for {file_path}: {validation_result.errors}"
            )

        return self.create_requirement_from_data(data)

    def create_requirement_from_data(self, data: Dict[str, Any]) -> Requirement:
        """Create Requirement object from parsed data"""
        return Requirement(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            type=data["type"],
            acceptance_criteria=data["acceptance_criteria"],
            tags=data.get("tags", []),
            source=data.get("source"),
            rationale=data.get("rationale"),
        )

    def parse_requirements_directory(self, directory: Path) -> List[Requirement]:
        """Parse all requirement files in a directory"""
        requirements = []
        for file_path in directory.glob("**/*.yaml"):
            data = None
            try:
                # Check if this is a requirement file by looking at the ID field
                data = self.parse_yaml_file(file_path)
                if isinstance(data, dict) and data.get("id", "").startswith("REQ-"):
                    # Try to create requirement object directly, skipping schema validation for parsing
                    req = self.create_requirement_from_data(data)
                    requirements.append(req)
            except ParseError as e:
                print(f"Warning: Skipping {file_path}: {e}")
            except Exception as e:
                # Skip non-requirement files silently, but log validation errors
                if (
                    data
                    and isinstance(data, dict)
                    and data.get("id", "").startswith("REQ-")
                ):
                    print(f"Warning: Skipping {file_path}: {e}")
                pass
        return requirements


class SpecificationParser(BaseParser):
    """Parser for specification files"""

    def __init__(self):
        super().__init__()
        self.validator = SpecificationValidator()

    def parse_specification_file(self, file_path: Path) -> Specification:
        """Parse specification YAML file"""
        data = self.parse_yaml_file(file_path)

        # Validate against schema
        validation_result = self.validator.validate_data(data)
        if not validation_result.is_valid:
            raise ParseError(
                f"Validation failed for {file_path}: {validation_result.errors}"
            )

        return self.create_specification_from_data(data)

    def create_specification_from_data(self, data: Dict[str, Any]) -> Specification:
        """Create Specification object from parsed data"""
        return Specification(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            related_requirements=data["related_requirements"],
            implementation_unit=data["implementation_unit"],
            unit_test=data["unit_test"],
            design_notes=data.get("design_notes"),
            dependencies=data.get("dependencies", []),
        )

    def parse_specifications_directory(self, directory: Path) -> List[Specification]:
        """Parse all specification files in a directory"""
        specifications = []
        for file_path in directory.glob("**/*.yaml"):
            data = None
            try:
                # Check if this is a specification file by looking at the ID field
                data = self.parse_yaml_file(file_path)
                if isinstance(data, dict) and data.get("id", "").startswith("SPEC-"):
                    # Try to create specification object directly, skipping schema validation for parsing
                    spec = self.create_specification_from_data(data)
                    specifications.append(spec)
            except ParseError as e:
                print(f"Warning: Skipping {file_path}: {e}")
            except Exception as e:
                # Skip non-specification files silently, but log validation errors
                if (
                    data
                    and isinstance(data, dict)
                    and data.get("id", "").startswith("SPEC-")
                ):
                    print(f"Warning: Skipping {file_path}: {e}")
                pass
        return specifications


class ProjectParser:
    """Parser for entire project requirements and specifications"""

    def __init__(self):
        self.req_parser = RequirementParser()
        self.spec_parser = SpecificationParser()

    def parse_project(
        self, project_path: Path
    ) -> Dict[str, Union[List[Requirement], List[Specification]]]:
        """Parse all requirements and specifications in a project"""
        requirements = self.req_parser.parse_requirements_directory(project_path)
        specifications = self.spec_parser.parse_specifications_directory(project_path)

        return {"requirements": requirements, "specifications": specifications}

    def save_requirement(self, requirement: Requirement, file_path: Path) -> None:
        """Save requirement to YAML file"""
        data = requirement.to_dict()
        with open(file_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    def save_specification(self, specification: Specification, file_path: Path) -> None:
        """Save specification to YAML file"""
        data = specification.to_dict()
        with open(file_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
