"""Test coverage analysis for specification unit tests"""

import ast
import re
from pathlib import Path
from typing import List, Set, Dict
from .models import Specification


class TestCoverageReport:
    """Report containing test coverage analysis results"""

    def __init__(
        self,
        tested_units: Set[str],
        untested_units: Set[str],
        tested_functions: Dict[str, Set[str]] = None,
        untested_functions: Dict[str, Set[str]] = None,
    ):
        self.tested_units = tested_units
        self.untested_units = untested_units
        self.tested_functions = tested_functions or {}
        self.untested_functions = untested_functions or {}

    def get_tested_units(self) -> List[str]:
        """Get list of tested unit test paths"""
        return sorted(list(self.tested_units))

    def get_untested_units(self) -> List[str]:
        """Get list of untested unit test paths"""
        return sorted(list(self.untested_units))

    def get_coverage_percentage(self) -> float:
        """Calculate coverage percentage"""
        total_units = len(self.tested_units) + len(self.untested_units)
        if total_units == 0:
            return 100.0
        return (len(self.tested_units) / total_units) * 100

    def get_tested_functions(self) -> Dict[str, List[str]]:
        """Get dictionary of tested functions by file"""
        return {
            file: sorted(list(functions))
            for file, functions in self.tested_functions.items()
        }

    def get_untested_functions(self) -> Dict[str, List[str]]:
        """Get dictionary of untested functions by file"""
        return {
            file: sorted(list(functions))
            for file, functions in self.untested_functions.items()
        }


class TestCoverageAnalyzer:
    """Analyzer for unit test coverage of specifications"""

    def __init__(self, specifications: List[Specification]):
        self.specifications = specifications
        self.unit_test_paths = set(spec.unit_test for spec in specifications)

    def analyze_test_list(self, test_list_file: str) -> TestCoverageReport:
        """Analyze test list file and determine coverage"""
        test_list_path = Path(test_list_file)

        if not test_list_path.exists():
            raise FileNotFoundError(f"Test list file not found: {test_list_file}")

        # Read test list
        with open(test_list_path, "r") as f:
            test_list_content = f.read()

        # Parse the test list to extract test paths and functions
        executed_tests = self._parse_test_list(test_list_content)

        # Determine which specification unit tests are covered
        tested_unit_tests = set()
        untested_unit_tests = set()
        tested_functions = {}
        untested_functions = {}

        for unit_test_path in self.unit_test_paths:
            # Get all test functions in this file
            test_functions = self._get_test_functions(unit_test_path)

            if test_functions:
                # STRICT MODE: Only consider functions as tested if they are explicitly listed
                covered_functions = set()
                missing_functions = set()

                for test_func in test_functions:
                    if self._is_function_covered(
                        unit_test_path, test_func, executed_tests
                    ):
                        covered_functions.add(test_func)
                    else:
                        missing_functions.add(test_func)

                # A file is considered "tested" if ANY of its test functions are being executed
                # We don't require ALL functions to be tested, just the ones that are listed
                if covered_functions:
                    # Some functions are covered - file is considered tested
                    tested_unit_tests.add(unit_test_path)
                    tested_functions[unit_test_path] = covered_functions
                    # Also track missing functions for informational purposes
                    if missing_functions:
                        untested_functions[unit_test_path] = missing_functions
                else:
                    # No functions are covered - file is untested
                    untested_unit_tests.add(unit_test_path)
                    untested_functions[unit_test_path] = missing_functions
            else:
                # No test functions found - this means the file doesn't exist or has no test functions
                # Either way, we cannot verify that tests are being run, so mark as untested
                untested_unit_tests.add(unit_test_path)

        return TestCoverageReport(
            tested_unit_tests, untested_unit_tests, tested_functions, untested_functions
        )

    def _parse_test_list(self, test_list_content: str) -> Set[str]:
        """Parse test list content to extract test paths"""
        executed_tests = set()

        # Split by lines and process each line
        lines = test_list_content.strip().split("\n")

        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                # Skip empty lines and comments
                continue

            # Handle different test path formats
            if line.startswith("tests/") or line.startswith("test"):
                # Direct test path
                executed_tests.add(line)
            elif "::" in line:
                # pytest format: path::test_function
                test_path = line.split("::")[0]
                executed_tests.add(test_path)
            elif line.endswith(".py"):
                # Python file path
                executed_tests.add(line)
            else:
                # Try to match as a test file pattern
                if "test" in line.lower():
                    executed_tests.add(line)

        return executed_tests

    def _is_test_covered(self, unit_test_path: str, executed_tests: Set[str]) -> bool:
        """Check if a unit test path is covered by the executed tests"""
        # Direct match
        if unit_test_path in executed_tests:
            return True

        # Check if any executed test matches the unit test path
        unit_test_path_obj = Path(unit_test_path)

        for executed_test in executed_tests:
            executed_test_path_obj = Path(executed_test)

            # Check if paths match exactly
            if unit_test_path_obj == executed_test_path_obj:
                return True

            # Check if the executed test path contains the unit test path
            if unit_test_path in executed_test:
                return True

            # Check if the unit test path contains the executed test path
            if executed_test in unit_test_path:
                return True

            # Check if the file names match (in case of different directory structures)
            if unit_test_path_obj.name == executed_test_path_obj.name:
                return True

        return False

    def _get_test_functions(self, test_file_path: str) -> Set[str]:
        """Extract test functions from a test file"""
        test_functions = set()

        try:
            # Check if the file exists (it might be a specification requirement, not an actual file)
            file_path = Path(test_file_path)
            if not file_path.exists():
                return test_functions

            # Read and parse the Python file
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse the AST to find test functions
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if node.name.startswith("test_"):
                            test_functions.add(node.name)
            except SyntaxError:
                # If AST parsing fails, fall back to regex
                test_functions.update(self._extract_test_functions_regex(content))

        except (OSError, IOError):
            # File doesn't exist or can't be read
            pass

        return test_functions

    def _extract_test_functions_regex(self, content: str) -> Set[str]:
        """Extract test functions using regex as fallback"""
        test_functions = set()

        # Match function definitions that start with 'test_'
        pattern = r"^\s*def\s+(test_\w+)\s*\("
        matches = re.findall(pattern, content, re.MULTILINE)
        test_functions.update(matches)

        return test_functions

    def _is_function_covered(
        self, test_file_path: str, function_name: str, executed_tests: Set[str]
    ) -> bool:
        """Check if a specific test function is covered by the executed tests"""
        # Check for exact function match in pytest format
        function_reference = f"{test_file_path}::{function_name}"

        for executed_test in executed_tests:
            # Direct function match
            if function_reference == executed_test:
                return True

            # Check if the executed test contains the function reference
            if function_reference in executed_test:
                return True

            # Check if the test file and function name are both mentioned
            if test_file_path in executed_test and function_name in executed_test:
                return True

        return False
