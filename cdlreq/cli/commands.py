"""CLI commands for cdlreq"""

import click
import yaml
from pathlib import Path
from typing import List, Optional
from ..core.models import Requirement, Specification
from ..core.parser import ProjectParser, RequirementParser, SpecificationParser
from ..core.validator import RequirementValidator, SpecificationValidator, CrossReferenceValidator


@click.group()
@click.version_option()
def cli():
    """cdlreq - Medical software requirements and specifications management"""
    pass


@cli.command()
@click.option('--directory', '-d', default='.', help='Directory to initialize')
def init(directory: str):
    """Initialize a new cdlreq project"""
    project_path = Path(directory)
    project_path.mkdir(exist_ok=True)
    
    # Create directory structure
    (project_path / "requirements").mkdir(exist_ok=True)
    (project_path / "specifications").mkdir(exist_ok=True)
    
    # Create example files
    example_req = Requirement(
        id="REQ-SYS-001",
        title="System shall authenticate users",
        description="The system must provide secure user authentication using industry-standard methods.",
        type="security",
        acceptance_criteria=[
            "User can log in with valid credentials",
            "Invalid credentials are rejected",
            "Account lockout after failed attempts"
        ],
        tags=["authentication", "security"]
    )
    
    example_spec = Specification(
        id="SPEC-SYS-001",
        title="User authentication implementation",
        description="Implementation of secure user authentication system using OAuth 2.0.",
        related_requirements=["REQ-SYS-001"],
        implementation_unit="src/auth/authentication.py",
        unit_test="tests/test_authentication.py",
        test_criteria=[
            "Test successful login with valid credentials",
            "Test failed login with invalid credentials",
            "Test account lockout mechanism"
        ]
    )
    
    # Save example files
    parser = ProjectParser()
    parser.save_requirement(example_req, project_path / "requirements" / "authentication.req.yaml")
    parser.save_specification(example_spec, project_path / "specifications" / "authentication.spec.yaml")
    
    click.echo(f"Initialized cdlreq project in {project_path}")
    click.echo("Created example files:")
    click.echo("  requirements/authentication.req.yaml")
    click.echo("  specifications/authentication.spec.yaml")


@cli.command()
@click.option('--directory', '-d', default='.', help='Directory to validate')
@click.option('--requirements-only', '-r', is_flag=True, help='Validate only requirements')
@click.option('--specifications-only', '-s', is_flag=True, help='Validate only specifications')
def validate(directory: str, requirements_only: bool, specifications_only: bool):
    """Validate requirements and specifications"""
    project_path = Path(directory)
    
    if not project_path.exists():
        click.echo(f"Error: Directory {directory} does not exist", err=True)
        return
    
    parser = ProjectParser()
    req_validator = RequirementValidator()
    spec_validator = SpecificationValidator()
    
    errors = []
    
    # Validate requirements
    if not specifications_only:
        try:
            requirements = parser.req_parser.parse_requirements_directory(project_path)
            click.echo(f"Found {len(requirements)} requirements")
            
            for req in requirements:
                result = req_validator.validate_requirement(req)
                if not result.is_valid:
                    errors.extend([f"Requirement {req.id}: {error}" for error in result.errors])
        except Exception as e:
            errors.append(f"Error parsing requirements: {e}")
    
    # Validate specifications
    if not requirements_only:
        try:
            specifications = parser.spec_parser.parse_specifications_directory(project_path)
            click.echo(f"Found {len(specifications)} specifications")
            
            for spec in specifications:
                result = spec_validator.validate_specification(spec)
                if not result.is_valid:
                    errors.extend([f"Specification {spec.id}: {error}" for error in result.errors])
        except Exception as e:
            errors.append(f"Error parsing specifications: {e}")
    
    # Cross-reference validation
    if not requirements_only and not specifications_only:
        try:
            requirements = parser.req_parser.parse_requirements_directory(project_path)
            specifications = parser.spec_parser.parse_specifications_directory(project_path)
            
            cross_validator = CrossReferenceValidator(requirements, specifications)
            result = cross_validator.validate_cross_references()
            if not result.is_valid:
                errors.extend(result.errors)
        except Exception as e:
            errors.append(f"Error in cross-reference validation: {e}")
    
    if errors:
        click.echo("Validation failed:", err=True)
        for error in errors:
            click.echo(f"  - {error}", err=True)
        exit(1)
    else:
        click.echo("Validation successful!")


@cli.command()
@click.option('--directory', '-d', default='.', help='Directory to search')
@click.option('--type', '-t', help='Filter by type (requirements/specifications)')
@click.option('--format', '-f', default='table', type=click.Choice(['table', 'json', 'yaml']), help='Output format')
def list(directory: str, type: Optional[str], format: str):
    """List requirements and specifications"""
    project_path = Path(directory)
    
    if not project_path.exists():
        click.echo(f"Error: Directory {directory} does not exist", err=True)
        return
    
    parser = ProjectParser()
    
    try:
        data = parser.parse_project(project_path)
        requirements = data["requirements"]
        specifications = data["specifications"]
        
        if format == 'json':
            import json
            output = {}
            if type != 'specifications':
                output['requirements'] = [req.to_dict() for req in requirements]
            if type != 'requirements':
                output['specifications'] = [spec.to_dict() for spec in specifications]
            click.echo(json.dumps(output, indent=2))
        
        elif format == 'yaml':
            output = {}
            if type != 'specifications':
                output['requirements'] = [req.to_dict() for req in requirements]
            if type != 'requirements':
                output['specifications'] = [spec.to_dict() for spec in specifications]
            click.echo(yaml.dump(output, default_flow_style=False))
        
        else:  # table format
            if type != 'specifications':
                click.echo("Requirements:")
                click.echo("ID\t\tTitle\t\tType")
                click.echo("-" * 50)
                for req in requirements:
                    click.echo(f"{req.id}\t{req.title[:30]}\t{req.type}")
            
            if type != 'requirements':
                click.echo("\nSpecifications:")
                click.echo("ID\t\tTitle\t\tRelated Requirements")
                click.echo("-" * 60)
                for spec in specifications:
                    related = ", ".join(spec.related_requirements[:2])
                    if len(spec.related_requirements) > 2:
                        related += "..."
                    click.echo(f"{spec.id}\t{spec.title[:30]}\t{related}")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument('type', type=click.Choice(['requirement', 'specification']))
@click.option('--id', help='ID for the new item')
@click.option('--title', help='Title for the new item')
@click.option('--req-type', help='Type of requirement (functional, security, etc.)')
@click.option('--output', '-o', help='Output file path')
def create(type: str, id: Optional[str], title: Optional[str], req_type: Optional[str], output: Optional[str]):
    """Create a new requirement or specification"""
    
    if not id:
        id = click.prompt(f"Enter {type} ID")
    
    if not title:
        title = click.prompt(f"Enter {type} title")
    
    if type == 'requirement':
        if not req_type:
            req_type = click.prompt("Enter requirement type", 
                                   type=click.Choice(['functional', 'security', 'performance', 'usability', 
                                                    'reliability', 'maintainability', 'portability', 'regulatory', 'safety']))
        
        description = click.prompt("Enter requirement description")
        acceptance_criteria = []
        
        click.echo("Enter acceptance criteria (empty line to finish):")
        while True:
            criterion = click.prompt("Criterion", default="", show_default=False)
            if not criterion:
                break
            acceptance_criteria.append(criterion)
        
        req = Requirement(
            id=id,
            title=title,
            description=description,
            type=req_type,
            acceptance_criteria=acceptance_criteria
        )
        
        if not output:
            output = f"requirements/{id.lower().replace('-', '_')}.req.yaml"
        
        parser = ProjectParser()
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        parser.save_requirement(req, output_path)
        
        click.echo(f"Created requirement: {output}")
    
    else:  # specification
        description = click.prompt("Enter specification description")
        related_requirements = click.prompt("Enter related requirement IDs (comma-separated)").split(',')
        related_requirements = [req.strip() for req in related_requirements if req.strip()]
        
        implementation_unit = click.prompt("Enter implementation unit path")
        unit_test = click.prompt("Enter unit test path")
        
        test_criteria = []
        click.echo("Enter test criteria (empty line to finish):")
        while True:
            criterion = click.prompt("Test criterion", default="", show_default=False)
            if not criterion:
                break
            test_criteria.append(criterion)
        
        spec = Specification(
            id=id,
            title=title,
            description=description,
            related_requirements=related_requirements,
            implementation_unit=implementation_unit,
            unit_test=unit_test,
            test_criteria=test_criteria
        )
        
        if not output:
            output = f"specifications/{id.lower().replace('-', '_')}.spec.yaml"
        
        parser = ProjectParser()
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        parser.save_specification(spec, output_path)
        
        click.echo(f"Created specification: {output}")


def main():
    """Main entry point"""
    cli()