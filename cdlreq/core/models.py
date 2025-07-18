"""Data models for requirements and specifications"""

from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path


@dataclass
class Requirement:
    """Medical software requirement model"""
    id: str
    title: str
    description: str
    type: str
    acceptance_criteria: List[str]
    tags: List[str] = field(default_factory=list)
    source: Optional[str] = None
    rationale: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Validate requirement data after initialization"""
        if not self.id.startswith("REQ-"):
            raise ValueError(f"Requirement ID must start with 'REQ-': {self.id}")
        
        valid_types = {
            "functional", "security", "performance", "usability", 
            "reliability", "maintainability", "portability", "regulatory", "safety"
        }
        if self.type not in valid_types:
            raise ValueError(f"Invalid requirement type: {self.type}")
    
    def to_dict(self) -> dict:
        """Convert requirement to dictionary"""
        result = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "type": self.type,
            "acceptance_criteria": self.acceptance_criteria,
        }
        if self.tags:
            result["tags"] = self.tags
        if self.source:
            result["source"] = self.source
        if self.rationale:
            result["rationale"] = self.rationale
        return result


@dataclass
class Specification:
    """Medical software specification model"""
    id: str
    title: str
    description: str
    related_requirements: List[str]
    implementation_unit: str
    unit_test: str
    test_criteria: List[str]
    design_notes: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        """Validate specification data after initialization"""
        if not self.id.startswith("SPEC-"):
            raise ValueError(f"Specification ID must start with 'SPEC-': {self.id}")
        
        for req_id in self.related_requirements:
            if not req_id.startswith("REQ-"):
                raise ValueError(f"Related requirement ID must start with 'REQ-': {req_id}")
        
        for dep_id in self.dependencies:
            if not dep_id.startswith("SPEC-"):
                raise ValueError(f"Dependency ID must start with 'SPEC-': {dep_id}")
    
    def to_dict(self) -> dict:
        """Convert specification to dictionary"""
        result = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "related_requirements": self.related_requirements,
            "implementation_unit": self.implementation_unit,
            "unit_test": self.unit_test,
            "test_criteria": self.test_criteria,
        }
        if self.design_notes:
            result["design_notes"] = self.design_notes
        if self.dependencies:
            result["dependencies"] = self.dependencies
        return result
    
    def get_implementation_path(self) -> Path:
        """Get Path object for implementation unit"""
        return Path(self.implementation_unit)
    
    def get_test_path(self) -> Path:
        """Get Path object for unit test"""
        return Path(self.unit_test)