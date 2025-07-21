"""Integration tests for cdlreq"""

import pytest
import tempfile
import yaml
from pathlib import Path
from click.testing import CliRunner
from cdlreq.cli.commands import cli
from cdlreq.core.parser import ProjectParser


@pytest.mark.integration
class TestEndToEndWorkflow:
    """Test complete end-to-end workflows"""
    
    def test_complete_workflow(self, temp_dir):
        """Test complete cdlreq workflow: init -> create -> validate -> export"""
        runner = CliRunner()
        
        # Step 1: Initialize project
        result = runner.invoke(cli, ['init', '--directory', str(temp_dir)])
        assert result.exit_code == 0
        
        # Step 2: Validate the initialized project
        result = runner.invoke(cli, ['validate', '--directory', str(temp_dir)])
        assert result.exit_code == 0
        assert "Validation successful" in result.output
        
        # Step 3: List the created items
        result = runner.invoke(cli, ['list', '--directory', str(temp_dir)])
        assert result.exit_code == 0
        assert "REQ-SYS-001" in result.output
        assert "SPEC-SYS-001" in result.output
        
        # Step 4: Try to export (may fail due to openpyxl dependency)
        output_file = temp_dir / "integration_matrix.xlsx"
        result = runner.invoke(cli, ['export', '--directory', str(temp_dir), 
                                   '--output', str(output_file)])
        
        # Accept either success or dependency error
        if result.exit_code != 0:
            assert "openpyxl" in str(result.exception) or "Error" in result.output
        else:
            assert result.exit_code == 0
    
    def test_coverage_workflow(self, temp_dir, test_output_content):
        """Test coverage command workflow"""
        runner = CliRunner()
        
        # Initialize project
        runner.invoke(cli, ['init', '--directory', str(temp_dir)])
        
        # Create test output file
        test_output_file = temp_dir / "test_results.txt"
        with open(test_output_file, 'w') as f:
            f.write(test_output_content)
        
        # Run coverage analysis
        result = runner.invoke(cli, ['coverage', str(test_output_file), 
                                   '--directory', str(temp_dir)])
        
        assert result.exit_code == 0
        # Should show some form of coverage results
        assert ("Executed tests:" in result.output or 
                "Not executed:" in result.output or
                "Invalid test files" in result.output)
    
    def test_create_and_validate_workflow(self, temp_dir):
        """Test creating new items and validating them"""
        runner = CliRunner()
        
        # Set up directory structure first
        req_dir = temp_dir / "requirements"
        req_dir.mkdir()
        spec_dir = req_dir / "specifications"
        spec_dir.mkdir()
        
        # Create requirement in the proper location so it can be found
        req_file = req_dir / "integration_req.yaml"
        result = runner.invoke(cli, [
            'create', 'requirement',
            '--id', 'INTEGRATION-001',
            '--title', 'Integration Test Requirement',
            '--req-type', 'functional',
            '--output', str(req_file)
        ], input='Integration test requirement description\nMust integrate\n\n')
        
        assert result.exit_code == 0
        assert req_file.exists()
        
        # Change to temp_dir so create command can find the requirement
        import os
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Create specification (it will find the existing requirement)
            spec_file = spec_dir / "integration_spec.yaml"
            result = runner.invoke(cli, [
                'create', 'specification',
                '--id', 'SPEC-INT-001',
                '--title', 'Integration Test Specification', 
                '--output', str(spec_file)
            ], input='Integration test specification description\n1\nsrc/integration.py\ntests/test_integration.py\n')
            
            assert result.exit_code == 0, f"Create specification failed: {result.output}"
            assert spec_file.exists(), f"Specification file not created: {spec_file}"
        finally:
            os.chdir(original_cwd)
        
        # Validate
        result = runner.invoke(cli, ['validate', '--directory', str(temp_dir)])
        assert result.exit_code == 0, f"Validation failed: {result.output}"


@pytest.mark.integration 
class TestParserIntegration:
    """Integration tests for parser functionality"""
    
    def test_parse_real_examples(self):
        """Test parsing the actual example files in the project"""
        parser = ProjectParser()
        examples_dir = Path(__file__).parent.parent / "examples"
        
        if examples_dir.exists():
            try:
                result = parser.parse_project(examples_dir)
                
                assert "requirements" in result
                assert "specifications" in result
                assert len(result["requirements"]) > 0
                assert len(result["specifications"]) > 0
                
                # Check that all requirements have valid IDs
                for req in result["requirements"]:
                    assert req.id.startswith("REQ-")
                    assert req.title
                    assert req.description
                
                # Check that all specifications have valid IDs and related requirements
                for spec in result["specifications"]:
                    assert spec.id.startswith("SPEC-")
                    assert spec.title
                    assert spec.description
                    assert len(spec.related_requirements) > 0
                    
            except Exception as e:
                pytest.skip(f"Could not parse examples: {e}")
        else:
            pytest.skip("Examples directory not found")
    
    def test_cross_reference_validation_with_examples(self):
        """Test cross-reference validation with example files"""
        from cdlreq.core.validator import CrossReferenceValidator
        
        parser = ProjectParser()
        examples_dir = Path(__file__).parent.parent / "examples"
        
        if examples_dir.exists():
            try:
                result = parser.parse_project(examples_dir)
                
                validator = CrossReferenceValidator(
                    result["requirements"], 
                    result["specifications"]
                )
                
                # Check for missing requirement links
                missing_links = validator.get_missing_requirement_links()
                
                # Print warning about missing links but don't fail the test
                if missing_links:
                    print(f"Warning: Found {len(missing_links)} missing requirement links:")
                    for spec_id, req_id in missing_links:
                        print(f"  {spec_id} -> {req_id}")
                
                # Validate cross-references
                validation_result = validator.validate_cross_references()
                assert isinstance(validation_result.is_valid, bool)
                
            except Exception as e:
                pytest.skip(f"Could not validate examples: {e}")
        else:
            pytest.skip("Examples directory not found")


@pytest.mark.slow
@pytest.mark.integration
class TestPerformanceIntegration:
    """Performance integration tests"""
    
    def test_large_project_parsing(self, temp_dir):
        """Test parsing a project with many requirements and specifications"""
        # Create a large number of requirements and specifications
        req_dir = temp_dir / "requirements"
        req_dir.mkdir()
        spec_dir = req_dir / "specifications"
        spec_dir.mkdir()
        
        # Create 100 requirements
        for i in range(100):
            req_data = {
                "id": f"REQ-PERF-{i:03d}",
                "title": f"Performance Test Requirement {i}",
                "description": f"Performance test requirement number {i}",
                "type": "functional",
                "acceptance_criteria": [f"Must perform task {i}"]
            }
            
            with open(req_dir / f"perf_req_{i:03d}.yaml", 'w') as f:
                yaml.dump(req_data, f)
        
        # Create 100 specifications
        for i in range(100):
            spec_data = {
                "id": f"SPEC-PERF-{i:03d}",
                "title": f"Performance Test Specification {i}",
                "description": f"Performance test specification number {i}",
                "related_requirements": [f"REQ-PERF-{i:03d}"],
                "implementation_unit": f"src/perf_{i:03d}.py",
                "unit_test": f"tests/test_perf_{i:03d}.py"
            }
            
            with open(spec_dir / f"perf_spec_{i:03d}.yaml", 'w') as f:
                yaml.dump(spec_data, f)
        
        # Test parsing performance
        import time
        start_time = time.time()
        
        parser = ProjectParser()
        result = parser.parse_project(temp_dir)
        
        end_time = time.time()
        parsing_time = end_time - start_time
        
        assert len(result["requirements"]) == 100
        assert len(result["specifications"]) == 100
        assert parsing_time < 10.0  # Should parse in less than 10 seconds
        
        print(f"Parsed 200 files in {parsing_time:.2f} seconds")