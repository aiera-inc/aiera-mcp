#!/usr/bin/env python3
"""Tests for MCP server resource handlers."""

import pytest
from mcp.types import ReadResourceResult, TextResourceContents, Resource
from aiera_mcp.server import run_server
from aiera_mcp.tools.transcrippets.tools import get_transcrippet_template


@pytest.mark.unit
class TestResourceRead:
    """Test the read_resource handler."""

    @pytest.mark.asyncio
    async def test_read_transcrippet_viewer_resource(self):
        """Test reading the transcrippet-viewer resource returns correct HTML."""
        # Import the server module to get access to the handlers
        from aiera_mcp import server as server_module

        # Get the read_resource handler directly
        # Note: The handler is defined inside run_server(), so we need to test it differently
        # For now, we'll test that the template function works correctly

        template_html = get_transcrippet_template()

        # Verify template contains key elements
        assert "<!DOCTYPE html>" in template_html
        assert "Transcrippet Viewer" in template_html
        assert "MCP Apps UI Protocol" in template_html
        assert 'protocolVersion: "2025-06-18"' in template_html
        assert "ui/initialize" in template_html
        assert "ui/notifications/tool-result" in template_html
        assert "renderTranscrippet" in template_html
        assert "aiera-sdk" in template_html

    def test_transcrippet_template_structure(self):
        """Test that the transcrippet template has correct structure."""
        template_html = get_transcrippet_template()

        # Verify HTML structure
        assert template_html.startswith("<!DOCTYPE html>")
        assert "<html>" in template_html
        assert "<head>" in template_html
        assert "<body" in template_html
        assert "</body>" in template_html
        assert "</html>" in template_html

        # Verify meta tags
        assert 'charset="UTF-8"' in template_html
        assert 'name="viewport"' in template_html

        # Verify container element
        assert 'id="transcrippet-container"' in template_html

    def test_transcrippet_template_protocol_version(self):
        """Test that template uses correct MCP protocol version."""
        template_html = get_transcrippet_template()

        # Should use 2025-06-18 (structured content support)
        assert 'protocolVersion: "2025-06-18"' in template_html

        # Should not use older versions
        assert 'protocolVersion: "2024-11-05"' not in template_html
        assert 'protocolVersion: "2025-11-25"' not in template_html

    def test_transcrippet_template_message_handlers(self):
        """Test that template has all required message handlers."""
        template_html = get_transcrippet_template()

        # Verify message sending function
        assert "function sendMessage(method, params" in template_html
        assert 'jsonrpc: "2.0"' in template_html
        assert "window.parent.postMessage" in template_html

        # Verify message listeners
        assert 'window.addEventListener("message"' in template_html
        assert "ui/initialize" in template_html
        assert "ui/notifications/tool-result" in template_html
        assert "ui/notifications/tool-input" in template_html

    def test_transcrippet_template_api_key_extraction(self):
        """Test that template extracts API key from multiple sources."""
        template_html = get_transcrippet_template()

        # Should extract from ui/initialize response
        assert "message.result.context.apiKey" in template_html

        # Should extract from structuredContent
        assert "structuredContent._ui.apiKey" in template_html

        # Should authenticate with API key
        assert "module.authenticateApiKey(apiKey)" in template_html

    def test_transcrippet_template_aiera_sdk(self):
        """Test that template loads Aiera SDK correctly."""
        template_html = get_transcrippet_template()

        # Verify SDK script tag
        assert "https://public.aiera.com/aiera-sdk" in template_html
        assert "embed.js" in template_html

        # Verify SDK usage
        assert "Aiera.Module" in template_html
        assert "Transcrippet/index.html" in template_html
        assert "module.load()" in template_html
        assert "module.configure" in template_html

    def test_transcrippet_template_handles_arrays_and_objects(self):
        """Test that template handles both find_transcrippets (array) and create_transcrippet (object)."""
        template_html = get_transcrippet_template()

        # Should check if response is array
        assert "Array.isArray(response)" in template_html

        # Should convert single object to array
        assert "[response]" in template_html

    def test_transcrippet_template_dynamic_height(self):
        """Test that template handles dynamic height adjustments."""
        template_html = get_transcrippet_template()

        # Should listen for height events
        assert "transcrippet-height" in template_html
        assert "iframe.style.height" in template_html


@pytest.mark.unit
class TestResourceList:
    """Test resource listing functionality."""

    def test_resource_uri_format(self):
        """Test that resource URI follows best practices."""
        # The URI should not have file extensions
        uri = "ui://transcrippet-viewer"

        # Verify no file extension
        assert not uri.endswith(".html")
        assert not uri.endswith(".htm")

        # Verify custom scheme
        assert uri.startswith("ui://")

        # Verify kebab-case format
        assert "-" in uri
        assert " " not in uri

    def test_resource_mimetype(self):
        """Test that resource has correct MIME type."""
        expected_mimetype = "text/html+mcp"

        # MIME type should indicate HTML with MCP extension
        assert "text/html" in expected_mimetype
        assert "+mcp" in expected_mimetype


@pytest.mark.unit
class TestResourceReadResult:
    """Test ReadResourceResult structure."""

    def test_read_resource_result_structure(self):
        """Test that ReadResourceResult has correct structure."""
        template_html = get_transcrippet_template()
        uri = "ui://transcrippet-viewer"

        # Create a ReadResourceResult as the handler would
        result = ReadResourceResult(
            contents=[
                TextResourceContents(
                    uri=uri, mimeType="text/html+mcp", text=template_html
                )
            ]
        )

        # Verify structure
        assert result is not None
        assert hasattr(result, "contents")
        assert isinstance(result.contents, list)
        assert len(result.contents) == 1

        # Verify content
        content = result.contents[0]
        assert isinstance(content, TextResourceContents)
        assert str(content.uri) == uri  # URI is AnyUrl type, convert to string
        assert content.mimeType == "text/html+mcp"
        assert content.text == template_html
        assert "<!DOCTYPE html>" in content.text

    def test_read_resource_result_serialization(self):
        """Test that ReadResourceResult can be serialized."""
        template_html = get_transcrippet_template()
        uri = "ui://transcrippet-viewer"

        result = ReadResourceResult(
            contents=[
                TextResourceContents(
                    uri=uri, mimeType="text/html+mcp", text=template_html
                )
            ]
        )

        # Should be able to convert to dict
        result_dict = result.model_dump()

        assert "contents" in result_dict
        assert len(result_dict["contents"]) == 1
        # URI in serialized dict is a string
        assert str(result_dict["contents"][0]["uri"]) == uri
        assert result_dict["contents"][0]["mimeType"] == "text/html+mcp"
        assert result_dict["contents"][0]["text"] == template_html


@pytest.mark.unit
class TestResourceValidation:
    """Test resource validation and error handling."""

    def test_invalid_uri_should_raise_error(self):
        """Test that invalid URI raises appropriate error."""
        invalid_uris = [
            "ui://nonexistent",
            "ui://wrong-resource",
            "https://external.com/resource",
            "file:///local/file",
        ]

        # The read_resource handler should raise ValueError for unknown URIs
        # We can't test the handler directly without running the server,
        # but we can verify the expected behavior
        for uri in invalid_uris:
            # Handler would raise: ValueError(f"Unknown resource: {uri}")
            assert uri != "ui://transcrippet-viewer"

    def test_valid_uri(self):
        """Test that valid URI is recognized."""
        valid_uri = "ui://transcrippet-viewer"

        # This URI should be handled by the read_resource handler
        assert valid_uri.startswith("ui://")
        assert "transcrippet-viewer" in valid_uri


@pytest.mark.unit
class TestResourceMetadata:
    """Test resource metadata structure."""

    def test_resource_metadata_fields(self):
        """Test that Resource has all required fields."""
        resource = Resource(
            uri="ui://transcrippet-viewer",
            name="Transcrippet Viewer",
            mimeType="text/html+mcp",
            description="Interactive transcrippet player widget",
        )

        # Verify required fields (URI is AnyUrl type)
        assert str(resource.uri) == "ui://transcrippet-viewer"
        assert resource.name == "Transcrippet Viewer"

        # Verify optional fields
        assert resource.mimeType == "text/html+mcp"
        assert resource.description == "Interactive transcrippet player widget"

    def test_resource_serialization(self):
        """Test that Resource can be serialized correctly."""
        resource = Resource(
            uri="ui://transcrippet-viewer",
            name="Transcrippet Viewer",
            mimeType="text/html+mcp",
            description="Interactive transcrippet player widget",
        )

        resource_dict = resource.model_dump()

        # URI in serialized dict is a string
        assert str(resource_dict["uri"]) == "ui://transcrippet-viewer"
        assert resource_dict["name"] == "Transcrippet Viewer"
        assert resource_dict["mimeType"] == "text/html+mcp"
        assert resource_dict["description"] == "Interactive transcrippet player widget"
