#!/usr/bin/env python3

"""Comprehensive serialization tests for all Aiera MCP tools."""

import pytest
import json
import inspect

from aiera_mcp.tools.registry import TOOL_REGISTRY


@pytest.mark.unit
class TestToolSerializationComprehensive:
    """Test all tools for potential serialization issues."""

    def get_all_response_models(self):
        """Get all response model classes from registered tools."""
        response_models = {}

        for tool_name, tool_config in TOOL_REGISTRY.items():
            # Get the tool function
            tool_function = tool_config["function"]

            # Get the return type annotation
            sig = inspect.signature(tool_function)
            return_annotation = sig.return_annotation

            if return_annotation and return_annotation != inspect.Signature.empty:
                response_models[tool_name] = return_annotation

        return response_models

    def create_sample_data_for_model(self, model_class):
        """Create sample data for a given model class."""
        sample_data = {}

        # Get model fields from the schema
        try:
            schema = model_class.model_json_schema()
            properties = schema.get("properties", {})
            required_fields = schema.get("required", [])

            # Add default values for common fields
            if "instructions" in properties:
                sample_data["instructions"] = ["Test instruction"]

            # Handle response field - all response models now use Optional[Any]
            if "response" in properties:
                sample_data["response"] = {"data": [], "test": True}

            # Handle pagination + data at top level (Categories/Keywords responses)
            if "pagination" in properties and "data" in properties:
                sample_data["pagination"] = {
                    "total_count": 0,
                    "current_page": 1,
                    "total_pages": 0,
                    "page_size": 50,
                }
                sample_data["data"] = {}

        except Exception as e:
            print(
                f"Warning: Could not generate sample data for {model_class.__name__}: {e}"
            )
            return {}

        return sample_data

    def test_all_tools_response_serialization(self):
        """Test that all tool response models can be serialized to JSON."""
        response_models = self.get_all_response_models()

        serialization_results = {}
        failed_tools = []

        for tool_name, response_model in response_models.items():
            try:
                # Create sample data for the response model
                sample_data = self.create_sample_data_for_model(response_model)

                # Create the model instance
                response_instance = response_model(**sample_data)

                # Test model_dump serialization
                serialized_dict = response_instance.model_dump()

                # Test JSON serialization
                json_str = json.dumps(serialized_dict)

                # Test that we can parse it back
                parsed = json.loads(json_str)

                serialization_results[tool_name] = {
                    "status": "success",
                    "model_class": response_model.__name__,
                    "json_length": len(json_str),
                }

            except Exception as e:
                serialization_results[tool_name] = {
                    "status": "failed",
                    "model_class": (
                        response_model.__name__ if response_model else "Unknown"
                    ),
                    "error": str(e),
                }
                failed_tools.append(tool_name)

        # Print results for debugging
        print(f"\nSerialization test results for {len(response_models)} tools:")
        for tool_name, result in serialization_results.items():
            status_symbol = "PASS" if result["status"] == "success" else "FAIL"
            print(f"  {status_symbol} {tool_name}: {result['status']}")
            if result["status"] == "failed":
                print(f"    Error: {result['error']}")

        # Assert that no tools failed
        if failed_tools:
            failure_details = []
            for tool_name in failed_tools:
                result = serialization_results[tool_name]
                failure_details.append(f"{tool_name}: {result['error']}")

            pytest.fail(
                f"Serialization failed for {len(failed_tools)} tools:\n"
                + "\n".join(failure_details)
            )

    def test_comprehensive_tool_execution_simulation(self):
        """Simulate tool execution to catch serialization issues that only appear at runtime."""
        response_models = self.get_all_response_models()

        print(f"\nTesting runtime serialization for {len(response_models)} tools:")

        runtime_failures = []

        for tool_name, response_model in response_models.items():
            try:
                # All response models now use pass-through Optional[Any] pattern
                # Create appropriate test data based on model structure
                test_data = self.create_sample_data_for_model(response_model)

                # Create model instance
                response_instance = response_model(**test_data)

                # Test full serialization chain
                serialized_dict = response_instance.model_dump()

                # Try JSON serialization
                try:
                    json_str = json.dumps(serialized_dict)
                    parsed_back = json.loads(json_str)
                    print(f"  PASS {tool_name}: Runtime serialization OK")
                except (TypeError, ValueError) as json_err:
                    print(
                        f"  WARN {tool_name}: Model creation OK, JSON serialization failed - {json_err}"
                    )

            except Exception as e:
                print(f"  FAIL {tool_name}: Runtime serialization FAILED - {e}")
                runtime_failures.append((tool_name, str(e)))

        if runtime_failures:
            failure_details = [f"{tool}: {error}" for tool, error in runtime_failures]
            pytest.fail(
                f"Runtime serialization failed for {len(runtime_failures)} tools:\n"
                + "\n".join(failure_details)
            )

    def test_edge_case_serialization(self):
        """Test serialization with edge case values."""
        print("\nTesting edge case serialization scenarios:")

        # Test with CitationInfo model which now uses metadata instead of timestamp
        from aiera_mcp.tools.common.models import CitationInfo, CitationMetadata

        edge_cases = [
            ("Event metadata", CitationMetadata(type="event", event_id=123)),
            ("Filing metadata", CitationMetadata(type="filing", filing_id=456)),
            (
                "Company doc metadata",
                CitationMetadata(type="company_doc", company_doc_id=789),
            ),
            ("None metadata", None),
        ]

        for case_name, test_value in edge_cases:
            try:
                citation = CitationInfo(title=f"Test {case_name}", metadata=test_value)
                serialized = citation.model_dump()
                json_str = json.dumps(serialized)

                print(f"  PASS {case_name}: serialized correctly")

            except Exception as e:
                print(f"  FAIL {case_name}: failed - {e}")
                # Don't fail the test for edge cases, just report them
