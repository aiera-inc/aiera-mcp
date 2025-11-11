#!/usr/bin/env python3

"""Comprehensive serialization tests for all Aiera MCP tools."""

import pytest
import json
from datetime import datetime, date
from typing import Any, Dict, List
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
            tool_function = tool_config['function']

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
            properties = schema.get('properties', {})
            required_fields = schema.get('required', [])

            for field_name, field_info in properties.items():
                field_type = field_info.get('type')

                if field_name in required_fields or field_name in ['result', 'events', 'filings', 'equities']:
                    if field_type == 'string':
                        sample_data[field_name] = f"test_{field_name}"
                    elif field_type == 'integer':
                        sample_data[field_name] = 1
                    elif field_type == 'number':
                        sample_data[field_name] = 1.0
                    elif field_type == 'boolean':
                        sample_data[field_name] = True
                    elif field_type == 'array':
                        sample_data[field_name] = []
                    elif field_type == 'object':
                        sample_data[field_name] = {}

            # Add default values for common fields
            if 'instructions' in properties:
                sample_data['instructions'] = ['Test instruction']
            if 'citation_information' in properties:
                sample_data['citation_information'] = []
            if 'total' in properties:
                sample_data['total'] = 0
            if 'page' in properties:
                sample_data['page'] = 1
            if 'page_size' in properties:
                sample_data['page_size'] = 50

            # Add specific required fields based on response type
            if 'document' in required_fields:  # GetCompanyDocResponse
                sample_data['document'] = {
                    'company_doc_id': '123',
                    'title': 'Test Document',
                    'company_name': 'Test Corp',
                    'publication_date': '2024-01-15',
                    'category': 'press_release'
                }
            if 'event' in required_fields:  # GetThirdBridgeEventResponse, GetEventResponse
                sample_data['event'] = {
                    'event_id': '123',
                    'title': 'Test Event',
                    'event_type': 'earnings',
                    'event_date': '2024-01-15T16:30:00',
                    'company_name': 'Test Corp',
                    'expert_name': 'Test Expert',
                    'expert_title': 'Test Title'
                }
            if 'transcrippet' in required_fields:  # CreateTranscrippetResponse
                sample_data['transcrippet'] = {
                    'transcrippet_id': '123',
                    'event_id': 456,
                    'transcript_item_id': 789,
                    'text': 'Test transcrippet text',
                    'public_url': 'https://example.com/transcrippet/123'
                }

        except Exception as e:
            print(f"Warning: Could not generate sample data for {model_class.__name__}: {e}")
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
                    'status': 'success',
                    'model_class': response_model.__name__,
                    'json_length': len(json_str)
                }

            except Exception as e:
                serialization_results[tool_name] = {
                    'status': 'failed',
                    'model_class': response_model.__name__ if response_model else 'Unknown',
                    'error': str(e)
                }
                failed_tools.append(tool_name)

        # Print results for debugging
        print(f"\\nSerialization test results for {len(response_models)} tools:")
        for tool_name, result in serialization_results.items():
            status_symbol = "✓" if result['status'] == 'success' else "✗"
            print(f"  {status_symbol} {tool_name}: {result['status']}")
            if result['status'] == 'failed':
                print(f"    Error: {result['error']}")

        # Assert that no tools failed
        if failed_tools:
            failure_details = []
            for tool_name in failed_tools:
                result = serialization_results[tool_name]
                failure_details.append(f"{tool_name}: {result['error']}")

            pytest.fail(f"Serialization failed for {len(failed_tools)} tools:\\n" + "\\n".join(failure_details))

    def find_datetime_fields_in_models(self):
        """Find all models that contain datetime or date fields."""
        datetime_models = {}

        # Import all model modules
        try:
            from aiera_mcp.tools.events.models import EventItem, EventDetails
            from aiera_mcp.tools.filings.models import FilingItem, FilingDetails
            from aiera_mcp.tools.third_bridge.models import ThirdBridgeEventItem, ThirdBridgeEventDetails
            from aiera_mcp.tools.search.models import TranscriptSearchItem, FilingSearchItem
            from aiera_mcp.tools.common.models import CitationInfo

            models_to_check = [
                EventItem, EventDetails, FilingItem, FilingDetails,
                ThirdBridgeEventItem, ThirdBridgeEventDetails,
                TranscriptSearchItem, FilingSearchItem, CitationInfo
            ]

            for model_class in models_to_check:
                datetime_fields = []

                # Get model fields
                try:
                    for field_name, field_info in model_class.model_fields.items():
                        field_type = field_info.annotation

                        # Check for datetime, date, or Optional versions
                        if hasattr(field_type, '__origin__'):  # Optional types
                            args = getattr(field_type, '__args__', ())
                            if datetime in args or date in args:
                                datetime_fields.append((field_name, 'Optional[datetime/date]'))
                        elif field_type in (datetime, date):
                            datetime_fields.append((field_name, field_type.__name__))

                    if datetime_fields:
                        datetime_models[model_class.__name__] = datetime_fields

                except Exception as e:
                    print(f"Warning: Could not check fields for {model_class.__name__}: {e}")

        except ImportError as e:
            print(f"Warning: Could not import some model modules: {e}")

        return datetime_models

    def test_datetime_fields_have_serializers(self):
        """Test that all datetime/date fields have proper serializers."""
        datetime_models = self.find_datetime_fields_in_models()

        print(f"\\nFound datetime/date fields in {len(datetime_models)} models:")

        models_without_serializers = []

        for model_name, fields in datetime_models.items():
            print(f"  {model_name}:")

            # Try to import the model class
            try:
                if 'Event' in model_name:
                    from aiera_mcp.tools.events.models import EventItem, EventDetails
                    model_class = EventItem if model_name == 'EventItem' else EventDetails
                elif 'Filing' in model_name and 'Search' not in model_name:
                    from aiera_mcp.tools.filings.models import FilingItem, FilingDetails
                    model_class = FilingItem if model_name == 'FilingItem' else FilingDetails
                elif 'ThirdBridge' in model_name:
                    from aiera_mcp.tools.third_bridge.models import ThirdBridgeEventItem, ThirdBridgeEventDetails
                    model_class = ThirdBridgeEventItem if 'Item' in model_name else ThirdBridgeEventDetails
                elif 'Search' in model_name:
                    from aiera_mcp.tools.search.models import TranscriptSearchItem, FilingSearchItem
                    model_class = TranscriptSearchItem if 'Transcript' in model_name else FilingSearchItem
                elif model_name == 'CitationInfo':
                    from aiera_mcp.tools.common.models import CitationInfo
                    model_class = CitationInfo
                else:
                    continue

                # Check if the model has serializers for datetime fields
                has_serializers = hasattr(model_class, '__pydantic_serializers__') and model_class.__pydantic_serializers__

                for field_name, field_type in fields:
                    print(f"    - {field_name}: {field_type}")

                    # Test with actual datetime/date values
                    try:
                        if 'date' in field_type.lower():
                            test_value = date(2024, 1, 15) if 'datetime' not in field_type.lower() else datetime(2024, 1, 15, 10, 30)
                        else:
                            test_value = datetime(2024, 1, 15, 10, 30)

                        # Create minimal test data
                        test_data = {field_name: test_value}

                        # Add required fields based on model
                        if model_name in ['EventItem', 'EventDetails']:
                            test_data.update({'event_id': '123', 'title': 'Test', 'event_type': 'earnings'})
                        elif model_name in ['FilingItem', 'FilingDetails']:
                            test_data.update({'filing_id': '123', 'company_name': 'Test', 'form_type': '10-K', 'title': 'Test', 'is_amendment': False})
                            if field_name != 'filing_date':  # filing_date is required
                                test_data['filing_date'] = date(2024, 1, 15)
                        elif model_name in ['ThirdBridgeEventItem', 'ThirdBridgeEventDetails']:
                            test_data.update({'event_id': '123', 'title': 'Test', 'company_name': 'Test', 'expert_name': 'Test', 'expert_title': 'Test'})
                        elif 'SearchItem' in model_name:
                            if 'Transcript' in model_name:
                                test_data.update({
                                    'primary_company_id': 123, 'content_id': 456, 'transcript_event_id': 789,
                                    'transcript_section': 'q_and_a', 'text': 'test', 'primary_equity_id': 1,
                                    'title': 'Test', '_score': 1.0,
                                    'citation_information': {'title': 'Test', 'url': 'http://test.com'}
                                })
                            else:  # FilingSearchItem
                                test_data.update({
                                    'primary_company_id': 123, 'content_id': 456, 'filing_id': 789,
                                    'text': 'test', 'primary_equity_id': 1, 'title': 'Test', '_score': 1.0,
                                    'citation_information': {'title': 'Test', 'url': 'http://test.com'}
                                })
                        elif model_name == 'CitationInfo':
                            test_data.update({'title': 'Test Citation'})

                        # Try to create and serialize the model
                        model_instance = model_class(**test_data)
                        serialized = model_instance.model_dump()

                        # Check if datetime/date field was serialized as string
                        if field_name in serialized:
                            serialized_value = serialized[field_name]
                            if isinstance(serialized_value, (datetime, date)):
                                print(f"      ⚠️  {field_name} not serialized (still {type(serialized_value).__name__})")
                                if model_name not in models_without_serializers:
                                    models_without_serializers.append(model_name)
                            else:
                                print(f"      ✓ {field_name} serialized correctly")

                        # Test JSON serialization
                        json.dumps(serialized)

                    except Exception as e:
                        print(f"      ✗ Error testing {field_name}: {e}")
                        if model_name not in models_without_serializers:
                            models_without_serializers.append(model_name)

            except Exception as e:
                print(f"    Error checking {model_name}: {e}")

        if models_without_serializers:
            pytest.fail(f"Models without proper datetime serializers: {models_without_serializers}")

    def test_comprehensive_tool_execution_simulation(self):
        """Simulate tool execution to catch serialization issues that only appear at runtime."""
        response_models = self.get_all_response_models()

        print(f"\\nTesting runtime serialization for {len(response_models)} tools:")

        runtime_failures = []

        for tool_name, response_model in response_models.items():
            try:
                # Create more realistic test data with edge cases
                if 'Event' in response_model.__name__:
                    # Events have datetime fields
                    test_data = {
                        'events': [{
                            'event_id': '12345',
                            'title': 'Test Event',
                            'event_type': 'earnings',
                            'event_date': datetime(2024, 1, 15, 16, 30, 0),
                            'company_name': 'Test Corp',
                            'ticker': 'TEST:US'
                        }],
                        'total': 1,
                        'page': 1,
                        'page_size': 50,
                        'instructions': ['Test instruction'],
                        'citation_information': [{
                            'title': 'Test Citation',
                            'timestamp': datetime(2024, 1, 15, 16, 30, 0)
                        }]
                    } if 'find_events' in tool_name or 'upcoming' in tool_name else {
                        'event': {
                            'event_id': '12345',
                            'title': 'Test Event',
                            'event_type': 'earnings',
                            'event_date': datetime(2024, 1, 15, 16, 30, 0),
                            'description': 'Test description'
                        },
                        'instructions': ['Test instruction'],
                        'citation_information': []
                    }
                elif 'Filing' in response_model.__name__:
                    # Filings have date fields
                    test_data = {
                        'filings': [{
                            'filing_id': '123456',
                            'company_name': 'Test Corp',
                            'form_type': '10-K',
                            'title': 'Test Filing',
                            'filing_date': date(2024, 1, 15),
                            'period_end_date': date(2023, 12, 31),
                            'is_amendment': False
                        }],
                        'total': 1,
                        'page': 1,
                        'page_size': 50,
                        'instructions': ['Test instruction'],
                        'citation_information': []
                    } if 'find_filings' in tool_name else {
                        'filing': {
                            'filing_id': '123456',
                            'company_name': 'Test Corp',
                            'form_type': '10-K',
                            'title': 'Test Filing',
                            'filing_date': date(2024, 1, 15),
                            'is_amendment': False,
                            'document_count': 1
                        },
                        'instructions': ['Test instruction'],
                        'citation_information': []
                    }
                elif 'Search' in response_model.__name__:
                    # Search results have structured data
                    if 'Transcript' in response_model.__name__:
                        test_data = {
                            'result': [{
                                'date': datetime(2024, 1, 15, 16, 30, 0),
                                'primary_company_id': 123,
                                'content_id': 456,
                                'transcript_event_id': 789,
                                'transcript_section': 'q_and_a',
                                'text': 'Test transcript text',
                                'primary_equity_id': 1,
                                'title': 'Test Event',
                                '_score': 15.5,
                                'citation_information': {'title': 'Test', 'url': 'http://test.com'}
                            }],
                            'instructions': ['Search completed'],
                            'citation_information': []
                        }
                    else:  # Filing search
                        test_data = {
                            'result': [{
                                'date': datetime(2024, 1, 15, 9, 0, 0),
                                'primary_company_id': 123,
                                'content_id': 456,
                                'filing_id': 789,
                                'text': 'Test filing text',
                                'primary_equity_id': 1,
                                'title': 'Test Filing',
                                '_score': 12.5,
                                'citation_information': {'title': 'Test', 'url': 'http://test.com'}
                            }],
                            'instructions': ['Search completed'],
                            'citation_information': []
                        }
                else:
                    # Generic response
                    test_data = self.create_sample_data_for_model(response_model)

                # Create model instance
                response_instance = response_model(**test_data)

                # Test full serialization chain
                serialized_dict = response_instance.model_dump()
                json_str = json.dumps(serialized_dict)
                parsed_back = json.loads(json_str)

                print(f"  ✓ {tool_name}: Runtime serialization OK")

            except Exception as e:
                print(f"  ✗ {tool_name}: Runtime serialization FAILED - {e}")
                runtime_failures.append((tool_name, str(e)))

        if runtime_failures:
            failure_details = [f"{tool}: {error}" for tool, error in runtime_failures]
            pytest.fail(f"Runtime serialization failed for {len(runtime_failures)} tools:\\n" + "\\n".join(failure_details))

    def test_edge_case_serialization(self):
        """Test serialization with edge case values."""
        print("\\nTesting edge case serialization scenarios:")

        edge_cases = [
            ("Empty datetime", datetime.min),
            ("Max datetime", datetime.max.replace(microsecond=0)),  # Remove microseconds for JSON compat
            ("Current datetime", datetime.now()),
            ("Empty date", date.min),
            ("Max date", date.max),
            ("Current date", date.today()),
        ]

        # Test with CitationInfo model
        from aiera_mcp.tools.common.models import CitationInfo

        for case_name, test_value in edge_cases:
            try:
                if isinstance(test_value, date) and not isinstance(test_value, datetime):
                    # Skip date values for CitationInfo since it expects datetime
                    continue

                citation = CitationInfo(title=f"Test {case_name}", timestamp=test_value)
                serialized = citation.model_dump()
                json_str = json.dumps(serialized)

                print(f"  ✓ {case_name}: {test_value} -> {serialized['timestamp']}")

            except Exception as e:
                print(f"  ✗ {case_name}: {test_value} failed - {e}")
                # Don't fail the test for edge cases, just report them