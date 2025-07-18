"""
cdlreq - A Python library and CLI for managing medical software requirements and specifications
"""

__version__ = "0.1.0"
__author__ = "Medical Software Team"

from .core.models import Requirement, Specification
from .core.parser import RequirementParser, SpecificationParser
from .core.validator import RequirementValidator, SpecificationValidator

__all__ = [
    "Requirement",
    "Specification",
    "RequirementParser",
    "SpecificationParser",
    "RequirementValidator",
    "SpecificationValidator",
]
