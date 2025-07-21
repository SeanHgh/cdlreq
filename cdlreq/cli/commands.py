"""CLI commands for cdlreq"""

import click
import yaml
from pathlib import Path
from typing import List, Optional
from ..core.models import Requirement, Specification
from ..core.parser import ProjectParser, RequirementParser, SpecificationParser
from ..core.validator import (
    RequirementValidator,
    SpecificationValidator,
    CrossReferenceValidator,
)
from ..core.exporter import TraceabilityMatrixExporter


def load_existing_requirements(directory: Path) -> List[Requirement]:
    """Load existing requirements from the project directory"""
    try:
        parser = RequirementParser()
        return parser.parse_requirements_directory(directory)
    except Exception:
        return []


def interactive_requirement_selection(
    existing_requirements: List[Requirement],
) -> List[str]:
    """Interactive selection of existing requirements"""
    if not existing_requirements:
        click.echo(
            "No existing requirements found. Please enter requirement IDs manually."
        )
        related_requirements = click.prompt(
            "Enter related requirement IDs (comma-separated)"
        ).split(",")
        return [req.strip() for req in related_requirements if req.strip()]

    click.echo("\nExisting requirements:")
    for i, req in enumerate(existing_requirements, 1):
        click.echo(f"  {i}. {req.id} - {req.title}")

    click.echo("\nSelect requirements by number (e.g., '1,3,5' or '1-3,5'):")
    click.echo("Or press ENTER to enter requirement IDs manually")

    selection = click.prompt("Selection", default="", show_default=False)

    if not selection.strip():
        # Manual entry
        related_requirements = click.prompt(
            "Enter related requirement IDs (comma-separated)"
        ).split(",")
        return [req.strip() for req in related_requirements if req.strip()]

    try:
        selected_ids = []
        parts = selection.split(",")

        for part in parts:
            part = part.strip()
            if "-" in part:
                # Handle ranges like "1-3"
                start, end = part.split("-", 1)
                start_idx = int(start.strip()) - 1
                end_idx = int(end.strip()) - 1
                for idx in range(start_idx, end_idx + 1):
                    if 0 <= idx < len(existing_requirements):
                        selected_ids.append(existing_requirements[idx].id)
            else:
                # Handle single numbers
                idx = int(part) - 1
                if 0 <= idx < len(existing_requirements):
                    selected_ids.append(existing_requirements[idx].id)

        # Remove duplicates while preserving order
        unique_ids = []
        for req_id in selected_ids:
            if req_id not in unique_ids:
                unique_ids.append(req_id)

        return unique_ids

    except (ValueError, IndexError):
        click.echo("Invalid selection. Please enter requirement IDs manually.")
        related_requirements = click.prompt(
            "Enter related requirement IDs (comma-separated)"
        ).split(",")
        return [req.strip() for req in related_requirements if req.strip()]


@click.group()
@click.version_option()
def cli():
    """cdlreq - Medical software requirements and specifications management"""
    pass


@cli.command()
@click.option("--directory", "-d", default=".", help="Directory to initialize")
def init(directory: str):
    """Initialize a new cdlreq project"""
    project_path = Path(directory)
    project_path.mkdir(exist_ok=True)

    # Create directory structure
    (project_path / "requirements").mkdir(exist_ok=True)
    (project_path / "requirements" / "specifications").mkdir(exist_ok=True)

    # Create example files
    example_req = Requirement(
        id="REQ-SYS-001",
        title="System shall authenticate users",
        description="The system must provide secure user authentication using industry-standard methods.",
        type="security",
        acceptance_criteria=[
            "User can log in with valid credentials",
            "Invalid credentials are rejected",
            "Account lockout after failed attempts",
        ],
        tags=["authentication", "security"],
    )

    example_spec = Specification(
        id="SPEC-SYS-001",
        title="User authentication implementation",
        description="Implementation of secure user authentication system using OAuth 2.0.",
        related_requirements=["REQ-SYS-001"],
        implementation_unit="src/auth/authentication.py",
        unit_test="tests/test_authentication.py",
    )

    # Save example files
    parser = ProjectParser()
    parser.save_requirement(
        example_req, project_path / "requirements" / "authentication.yaml"
    )
    parser.save_specification(
        example_spec,
        project_path / "requirements" / "specifications" / "authentication.yaml",
    )

    click.echo(f"Initialized cdlreq project in {project_path}")
    click.echo("Created example files:")
    click.echo("  requirements/authentication.yaml")
    click.echo("  requirements/specifications/authentication.yaml")


@cli.command()
@click.option("--directory", "-d", default=".", help="Directory to validate")
@click.option(
    "--requirements-only", "-r", is_flag=True, help="Validate only requirements"
)
@click.option(
    "--specifications-only", "-s", is_flag=True, help="Validate only specifications"
)
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
                    errors.extend(
                        [f"Requirement {req.id}: {error}" for error in result.errors]
                    )
        except Exception as e:
            errors.append(f"Error parsing requirements: {e}")

    # Validate specifications
    if not requirements_only:
        try:
            specifications = parser.spec_parser.parse_specifications_directory(
                project_path
            )
            click.echo(f"Found {len(specifications)} specifications")

            for spec in specifications:
                result = spec_validator.validate_specification(spec)
                if not result.is_valid:
                    errors.extend(
                        [f"Specification {spec.id}: {error}" for error in result.errors]
                    )
        except Exception as e:
            errors.append(f"Error parsing specifications: {e}")

    # Cross-reference validation
    warnings = []
    if not requirements_only and not specifications_only:
        try:
            requirements = parser.req_parser.parse_requirements_directory(project_path)
            specifications = parser.spec_parser.parse_specifications_directory(
                project_path
            )

            cross_validator = CrossReferenceValidator(requirements, specifications)

            # Check for missing requirement links (warnings)
            missing_links = cross_validator.get_missing_requirement_links()
            for spec_id, missing_req_id in missing_links:
                warnings.append(
                    f"Specification {spec_id} references non-existent requirement {missing_req_id}"
                )

            # Check for other cross-reference errors
            result = cross_validator.validate_cross_references()
            if not result.is_valid:
                # Filter out missing requirement errors since we show them as warnings
                filtered_errors = [
                    error
                    for error in result.errors
                    if not error.startswith("Specification")
                    or "references non-existent requirement" not in error
                ]
                errors.extend(filtered_errors)
        except Exception as e:
            errors.append(f"Error in cross-reference validation: {e}")

    # Display warnings in orange/yellow
    if warnings:
        click.echo()
        click.echo(click.style("⚠️  Warnings:", fg="bright_yellow", bold=True))
        for warning in warnings:
            click.echo(click.style(f"  - {warning}", fg="bright_yellow"))
        click.echo()

    if errors:
        click.echo("Validation failed:", err=True)
        for error in errors:
            click.echo(f"  - {error}", err=True)
        exit(1)
    else:
        success_msg = "Validation successful!"
        if warnings:
            success_msg += (
                f" ({len(warnings)} warning{'s' if len(warnings) > 1 else ''})"
            )
        click.echo(click.style(success_msg, fg="green", bold=True))


@cli.command()
@click.option("--directory", "-d", default=".", help="Directory to search")
@click.option("--type", "-t", help="Filter by type (requirements/specifications)")
@click.option(
    "--format",
    "-f",
    default="table",
    type=click.Choice(["table", "json", "yaml"]),
    help="Output format",
)
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

        if format == "json":
            import json

            output = {}
            if type != "specifications":
                output["requirements"] = [req.to_dict() for req in requirements]
            if type != "requirements":
                output["specifications"] = [spec.to_dict() for spec in specifications]
            click.echo(json.dumps(output, indent=2))

        elif format == "yaml":
            output = {}
            if type != "specifications":
                output["requirements"] = [req.to_dict() for req in requirements]
            if type != "requirements":
                output["specifications"] = [spec.to_dict() for spec in specifications]
            click.echo(yaml.dump(output, default_flow_style=False))

        else:  # table format
            if type != "specifications":
                click.echo("Requirements:")
                click.echo("ID\t\tTitle\t\tType")
                click.echo("-" * 50)
                for req in requirements:
                    click.echo(f"{req.id}\t{req.title[:30]}\t{req.type}")

            if type != "requirements":
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
@click.argument("type", type=click.Choice(["requirement", "specification"]))
@click.option(
    "--id",
    help="ID suffix for the new item (REQ-/SPEC- prefix will be added automatically)",
)
@click.option("--title", help="Title for the new item")
@click.option("--req-type", help="Type of requirement (functional, security, etc.)")
@click.option("--output", "-o", help="Output file path")
def create(
    type: str,
    id: Optional[str],
    title: Optional[str],
    req_type: Optional[str],
    output: Optional[str],
):
    """Create a new requirement or specification"""

    if not id:
        if type == "requirement":
            id_suffix = click.prompt(
                "Enter requirement ID (without REQ- prefix)", default="SYS-001"
            )
            id = f"REQ-{id_suffix}"
        else:  # specification
            id_suffix = click.prompt(
                "Enter specification ID (without SPEC- prefix)", default="SYS-001"
            )
            id = f"SPEC-{id_suffix}"
    else:
        # If ID is provided via option, ensure it has the correct prefix
        if type == "requirement" and not id.startswith("REQ-"):
            id = f"REQ-{id}"
        elif type == "specification" and not id.startswith("SPEC-"):
            id = f"SPEC-{id}"

    if not title:
        title = click.prompt(f"Enter {type} title")

    if type == "requirement":
        if not req_type:
            req_type = click.prompt(
                "Enter requirement type",
                type=click.Choice(
                    [
                        "functional",
                        "security",
                        "performance",
                        "usability",
                        "reliability",
                        "maintainability",
                        "portability",
                        "regulatory",
                        "safety",
                    ]
                ),
            )

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
            acceptance_criteria=acceptance_criteria,
        )

        if not output:
            output = f"requirements/{id.lower().replace('-', '_')}.yaml"

        parser = ProjectParser()
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        parser.save_requirement(req, output_path)

        click.echo(f"Created requirement: {output}")

    else:  # specification
        description = click.prompt("Enter specification description")

        # Load existing requirements for interactive selection
        current_dir = Path.cwd()
        existing_requirements = load_existing_requirements(current_dir)

        click.echo(f"\nFound {len(existing_requirements)} existing requirements.")
        related_requirements = interactive_requirement_selection(existing_requirements)

        if not related_requirements:
            click.echo(
                "Error: At least one related requirement must be specified.", err=True
            )
            return

        implementation_unit = click.prompt("Enter implementation unit path")
        unit_test = click.prompt("Enter unit test path")

        spec = Specification(
            id=id,
            title=title,
            description=description,
            related_requirements=related_requirements,
            implementation_unit=implementation_unit,
            unit_test=unit_test,
        )

        if not output:
            output = f"requirements/specifications/{id.lower().replace('-', '_')}.yaml"

        parser = ProjectParser()
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        parser.save_specification(spec, output_path)

        click.echo(f"Created specification: {output}")


@cli.command()
@click.option("--directory", "-d", default=".", help="Directory to export from")
@click.option(
    "--output", "-o", default="traceability_matrix.xlsx", help="Output Excel file path"
)
def export(directory: str, output: str):
    """Export requirements and specifications to Excel traceability matrix"""
    project_path = Path(directory)

    if not project_path.exists():
        click.echo(f"Error: Directory {directory} does not exist", err=True)
        return

    try:
        # Load requirements and specifications
        parser = ProjectParser()
        requirements = parser.req_parser.parse_requirements_directory(project_path)
        specifications = parser.spec_parser.parse_specifications_directory(project_path)

        if not requirements and not specifications:
            click.echo(
                "No requirements or specifications found in the project directory.",
                err=True,
            )
            return

        click.echo(
            f"Found {len(requirements)} requirements and {len(specifications)} specifications"
        )

        # Create output path
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Export to Excel
        exporter = TraceabilityMatrixExporter(requirements, specifications)
        exporter.export_to_excel(output_path)

        click.echo(f"✅ Traceability matrix exported to: {output_path}")
        click.echo(
            f"📊 Excel file contains {len(requirements)} requirements and {len(specifications)} specifications"
        )

        # Summary statistics
        if requirements and specifications:
            traced_reqs = set()
            for spec in specifications:
                traced_reqs.update(spec.related_requirements)

            untraced_count = len(requirements) - len(traced_reqs)
            if untraced_count > 0:
                click.echo(
                    click.style(
                        f"⚠️  {untraced_count} requirement(s) have no specifications",
                        fg="yellow",
                    )
                )
            else:
                click.echo(
                    click.style("✅ All requirements have specifications", fg="green")
                )

    except Exception as e:
        click.echo(f"Error during export: {e}", err=True)


@cli.command()
@click.argument("test_output_file", type=click.Path(exists=True))
@click.option("--directory", "-d", default=".", help="Project directory")
def coverage(test_output_file: str, directory: str):
    """Check if specification unit tests were executed"""
    try:
        # Read test output file
        with open(test_output_file, 'r') as f:
            test_output = f.read()

        # Load specifications
        parser = ProjectParser()
        specs = parser.spec_parser.parse_specifications_directory(Path(directory))
        
        # Get all unit test paths from specs and check file existence
        spec_tests = set()
        invalid_files = {}  # Maps test_path -> list of spec IDs
        test_to_specs = {}  # Maps test_path -> list of spec IDs for all valid tests
        
        for spec in specs:
            if hasattr(spec, 'unit_test') and spec.unit_test:
                test_path = spec.unit_test
                # Check if the test file actually exists
                if Path(test_path).exists():
                    spec_tests.add(test_path)
                    if test_path not in test_to_specs:
                        test_to_specs[test_path] = []
                    test_to_specs[test_path].append(spec.id)
                else:
                    if test_path not in invalid_files:
                        invalid_files[test_path] = []
                    invalid_files[test_path].append(spec.id)
        
        if not spec_tests and not invalid_files:
            click.echo("No unit tests found in specifications")
            return

        # Check which tests were executed
        executed = set()
        not_executed = set()
        
        for test_path in spec_tests:
            if test_path in test_output:
                executed.add(test_path)
            else:
                not_executed.add(test_path)

        # Display results
        if invalid_files:
            click.echo(click.style("⚠️  Invalid test files (do not exist):", fg="yellow", bold=True))
            for test_path in sorted(invalid_files.keys()):
                spec_ids = ", ".join(invalid_files[test_path])
                click.echo(f"  {test_path} → used in: {spec_ids}")
            click.echo()

        if executed:
            click.echo(click.style("✅ Executed tests:", fg="green"))
            for test in sorted(executed):
                spec_ids = ", ".join(test_to_specs[test])
                click.echo(f"  {test} → used in: {spec_ids}")
        
        if not_executed:
            click.echo(click.style("❌ Not executed:", fg="red"))
            for test in sorted(not_executed):
                spec_ids = ", ".join(test_to_specs[test])
                click.echo(f"  {test} → used in: {spec_ids}")

        # Summary
        total_spec_tests = len(spec_tests) + len(invalid_files)
        click.echo(f"\n{len(executed)}/{len(spec_tests)} valid tests executed")
        if invalid_files:
            click.echo(f"{len(invalid_files)} invalid test file(s) in specifications")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)





def main():
    """Main entry point"""
    cli()
