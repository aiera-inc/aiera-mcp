#!/usr/bin/env python3

"""Integration tests for transcrippets tools with real Aiera API."""

import pytest
import pytest_asyncio
from unittest.mock import patch

from aiera_mcp.tools.transcrippets.tools import (
    find_transcrippets, create_transcrippet, delete_transcrippet
)
from aiera_mcp.tools.transcrippets.models import (
    FindTranscrippetsArgs, CreateTranscrippetArgs, DeleteTranscrippetArgs,
    FindTranscrippetsResponse, CreateTranscrippetResponse, DeleteTranscrippetResponse,
    TranscrippetItem
)


@pytest.mark.integration
@pytest.mark.requires_api_key
@pytest.mark.slow
class TestTranscrippetsIntegration:
    """Integration tests for transcrippets tools with real API."""

    @pytest.mark.asyncio
    async def test_find_transcrippets_real_api(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        sample_date_ranges,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test find_transcrippets with real API."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # Test with a date range that might have transcrippets
            date_range = sample_date_ranges[1]  # Q1 2024
            args = FindTranscrippetsArgs(
                start_date=date_range["start_date"],
                end_date=date_range["end_date"]
            )

            result = await find_transcrippets(args)

            # Verify response structure - note transcrippets has different structure than paginated responses
            assert isinstance(result, FindTranscrippetsResponse)
            assert isinstance(result.transcrippets, list)

            # If we found transcrippets, verify their structure
            if result.transcrippets:
                first_transcrippet = result.transcrippets[0]
                assert isinstance(first_transcrippet, TranscrippetItem)
                assert first_transcrippet.transcrippet_id
                assert first_transcrippet.public_url
                # Title might be None for some transcrippets, but should have either title or event_title
                assert first_transcrippet.title or first_transcrippet.event_title
                assert first_transcrippet.company_name
                # Verify public URL format
                assert first_transcrippet.public_url.startswith("https://public.aiera.com/shared/transcrippet.html?id=")

    @pytest.mark.asyncio
    async def test_find_transcrippets_with_ticker_filter(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        sample_tickers,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test find_transcrippets with ticker filter."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # Test with Apple ticker
            args = FindTranscrippetsArgs(
                start_date="2023-01-01",
                end_date="2023-12-31",
                bloomberg_ticker=sample_tickers[0]  # AAPL:US
            )

            result = await find_transcrippets(args)

            assert isinstance(result, FindTranscrippetsResponse)
            assert isinstance(result.transcrippets, list)

            # If we found transcrippets, they should be for Apple or related companies
            for transcrippet in result.transcrippets:
                assert isinstance(transcrippet, TranscrippetItem)
                # Note: Transcrippets might not have exact ticker matches
                # so we verify the structure without enforcing specific content
                assert transcrippet.public_url.startswith("https://public.aiera.com/")

    @pytest.mark.asyncio
    async def test_find_transcrippets_extended_date_range(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test find_transcrippets with extended date range to increase chance of finding results."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # Test with a longer date range to increase chance of finding transcrippets
            args = FindTranscrippetsArgs(
                start_date="2023-01-01",
                end_date="2024-06-30"
            )

            result = await find_transcrippets(args)

            assert isinstance(result, FindTranscrippetsResponse)
            assert isinstance(result.transcrippets, list)

            # Verify structure of any found transcrippets
            for transcrippet in result.transcrippets:
                assert isinstance(transcrippet, TranscrippetItem)
                assert transcrippet.transcrippet_id
                assert transcrippet.public_url
                # Title might be None for some transcrippets, but should have either title or event_title
                assert transcrippet.title or transcrippet.event_title
                assert transcrippet.company_name

    @pytest.mark.asyncio
    async def test_find_transcrippets_with_search(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test find_transcrippets with search query."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # Test search for earnings-related transcrippets
            args = FindTranscrippetsArgs(
                start_date="2023-01-01",
                end_date="2024-06-30",
                search="earnings"
            )

            result = await find_transcrippets(args)

            assert isinstance(result, FindTranscrippetsResponse)
            assert isinstance(result.transcrippets, list)

            # If we found transcrippets, verify they are related to earnings
            for transcrippet in result.transcrippets:
                assert isinstance(transcrippet, TranscrippetItem)
                # The search might find related transcrippets, so we don't enforce strict matching

    @pytest.mark.asyncio
    async def test_create_transcrippet_real_api(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test create_transcrippet with real API - requires complex transcript data."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # Creating transcrippets requires detailed transcript item data
            # that's not available in simple integration tests
            pytest.skip("CreateTranscrippet requires detailed transcript item IDs and offsets not available in basic integration testing")

            try:
                # This would require actual transcript item data:
                # args = CreateTranscrippetArgs(
                #     event_id=2818995,
                #     transcript="Sample transcript text",
                #     transcript_item_id=123456,
                #     transcript_item_offset=0,
                #     transcript_end_item_id=123457,
                #     transcript_end_item_offset=100
                # )
                # result = await create_transcrippet(args)
                pass

                # Verify response structure if creation succeeds
                assert isinstance(result, CreateTranscrippetResponse)
                assert isinstance(result.transcrippet, TranscrippetItem)
                assert result.transcrippet.transcrippet_id
                assert result.transcrippet.public_url
                assert result.transcrippet.title == "Test Integration Transcrippet"

                # Clean up - try to delete the created transcrippet
                if hasattr(result.transcrippet, 'transcrippet_id'):
                    await api_rate_limiter.wait()
                    delete_args = DeleteTranscrippetArgs(
                        transcrippet_id=result.transcrippet.transcrippet_id
                    )
                    try:
                        await delete_transcrippet(delete_args)
                    except Exception:
                        # If deletion fails, that's okay for testing purposes
                        pass

            except Exception as e:
                # Creation might fail if the event doesn't exist or other validation issues
                # This is acceptable for integration tests as we're using test data
                if "not found" in str(e).lower() or "invalid" in str(e).lower():
                    pytest.skip(f"Cannot create transcrippet with test event ID: {str(e)}")
                else:
                    raise

    @pytest.mark.asyncio
    async def test_delete_transcrippet_invalid_id(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test delete_transcrippet with invalid transcrippet ID."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # Test with invalid transcrippet ID
            delete_args = DeleteTranscrippetArgs(transcrippet_id="invalid-transcrippet-id-12345")

            # This should raise an exception or return an error
            try:
                result = await delete_transcrippet(delete_args)
                # If no exception, the result should indicate an error or success (deletion of non-existent is sometimes OK)
                assert isinstance(result, DeleteTranscrippetResponse)
            except (ValueError, Exception) as e:
                # Expected - invalid transcrippet ID should cause an error
                assert "not found" in str(e).lower() or "invalid" in str(e).lower()

    @pytest.mark.asyncio
    async def test_transcrippets_api_error_handling(
        self,
        integration_mcp_server,
        real_http_client,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test transcrippets API error handling with invalid API key."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.tools.base.get_api_key_from_context', return_value="invalid-api-key"):

            args = FindTranscrippetsArgs(
                start_date="2023-10-01",
                end_date="2023-10-31"
            )

            # This should raise an exception or return an error response
            try:
                result = await find_transcrippets(args)
                # If it doesn't raise an exception, check for error indicators
                if hasattr(result, 'error') or len(result.transcrippets) == 0:
                    # API handled the error gracefully
                    pass
            except Exception as e:
                # Expected - invalid API key should cause an error
                assert "401" in str(e) or "Unauthorized" in str(e) or "Invalid" in str(e)

    @pytest.mark.asyncio
    async def test_transcrippets_response_structure_no_data(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test that transcrippets return proper response structures even when no data exists."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # Test with a narrow date range that probably won't have transcrippets
            args = FindTranscrippetsArgs(
                start_date="2024-01-01",
                end_date="2024-01-01"
            )

            result = await find_transcrippets(args)

            # Even with no transcrippets, response should have proper structure
            assert isinstance(result, FindTranscrippetsResponse)
            assert isinstance(result.transcrippets, list)
            assert hasattr(result, 'instructions')
            assert hasattr(result, 'citation_information')
            assert isinstance(result.citation_information, list)

    @pytest.mark.asyncio
    async def test_transcrippets_citations_integration(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test that transcrippets responses include citation information with public URLs."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            args = FindTranscrippetsArgs(
                start_date="2023-01-01",
                end_date="2024-06-30"
            )

            result = await find_transcrippets(args)

            # Verify citations are generated with public URLs
            assert hasattr(result, 'citation_information')
            assert isinstance(result.citation_information, list)

            # If we found transcrippets, citations should be created
            if result.transcrippets:
                assert len(result.citation_information) >= len(result.transcrippets)

                for i, citation in enumerate(result.citation_information):
                    assert citation.title
                    assert citation.url
                    assert citation.url.startswith("https://public.aiera.com/shared/transcrippet.html?id=")

    @pytest.mark.asyncio
    async def test_transcrippets_with_multiple_filters(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        sample_tickers,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test transcrippets with multiple filter combinations."""

        filter_combinations = [
            {
                "start_date": "2023-01-01",
                "end_date": "2024-06-30",
                "bloomberg_ticker": sample_tickers[0]
            },
            {
                "start_date": "2023-01-01",
                "end_date": "2024-06-30",
                "search": "earnings"
            },
            {
                "start_date": "2023-06-01",
                "end_date": "2024-06-30",
                "event_type": "earnings"
            }
        ]

        with patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            for filter_combo in filter_combinations:
                await api_rate_limiter.wait()

                args = FindTranscrippetsArgs(**filter_combo)
                result = await find_transcrippets(args)

                assert isinstance(result, FindTranscrippetsResponse)
                assert isinstance(result.transcrippets, list)

                # Verify structure of any found transcrippets
                for transcrippet in result.transcrippets:
                    assert isinstance(transcrippet, TranscrippetItem)
                    assert transcrippet.transcrippet_id
                    assert transcrippet.public_url
                    # Title might be None, but should have either title or event_title
                    assert transcrippet.title or transcrippet.event_title

    @pytest.mark.asyncio
    async def test_transcrippets_public_url_format(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test that transcrippets generate properly formatted public URLs."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            args = FindTranscrippetsArgs(
                start_date="2023-01-01",
                end_date="2024-06-30"
            )

            result = await find_transcrippets(args)

            # Verify public URL format for all found transcrippets
            for transcrippet in result.transcrippets:
                public_url = transcrippet.public_url

                # Verify URL format
                assert public_url.startswith("https://public.aiera.com/shared/transcrippet.html?id=")

                # Extract the ID part and verify it's not empty
                url_parts = public_url.split("?id=")
                assert len(url_parts) == 2
                transcrippet_guid = url_parts[1]
                assert len(transcrippet_guid) > 0

    @pytest.mark.asyncio
    async def test_transcrippets_array_response_handling(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test that transcrippets properly handle array response format (different from other APIs)."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            args = FindTranscrippetsArgs(
                start_date="2023-01-01",
                end_date="2024-06-30"
            )

            result = await find_transcrippets(args)

            # The response should handle the array format correctly
            assert isinstance(result, FindTranscrippetsResponse)
            assert isinstance(result.transcrippets, list)

            # Even if no transcrippets found, the structure should be correct
            # (transcrippets API returns array vs other APIs that return response.data)
            assert hasattr(result, 'instructions')
            assert hasattr(result, 'citation_information')