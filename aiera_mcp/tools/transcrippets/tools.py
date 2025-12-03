#!/usr/bin/env python3

"""Transcrippet tools for Aiera MCP."""

import logging

from .models import (
    FindTranscrippetsArgs,
    CreateTranscrippetArgs,
    DeleteTranscrippetArgs,
    FindTranscrippetsResponse,
    CreateTranscrippetResponse,
    DeleteTranscrippetResponse,
    TranscrippetItem,
)
from ..base import get_http_client, make_aiera_request, validate_response_model
from ... import get_api_key
from ..common.models import CitationInfo

# Setup logging
logger = logging.getLogger(__name__)


def get_transcrippet_template() -> str:
    """Get the transcrippet UI template implementing MCP Apps protocol.

    The template implements the MCP Apps notification protocol:
    1. Sends ui/initialize request to the host
    2. Listens for ui/notifications/tool-result with structuredContent
    3. Renders transcrippets from the result data

    Returns:
        HTML template that communicates with MCP host via JSON-RPC
    """
    return """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Transcrippet Viewer</title>
</head>
<body style="margin: 0; padding: 0;">
    <script src="https://public.aiera.com/aiera-sdk/0.0.69/embed.js"></script>
    <div id="transcrippet-container"></div>
    <script>
        // MCP Apps UI Protocol Implementation
        let messageId = 0;
        let apiKey = null;
        let toolResult = null;

        // Send JSON-RPC message to host
        function sendMessage(method, params = {}) {
            const message = {
                jsonrpc: "2.0",
                id: ++messageId,
                method: method,
                params: params
            };
            window.parent.postMessage(message, "*");
        }

        // Initialize MCP UI connection
        sendMessage("ui/initialize", {
            protocolVersion: "2025-06-18"
        });

        // Listen for messages from host
        window.addEventListener("message", async (event) => {
            const message = event.data;

            if (!message || !message.jsonrpc) return;

            // Handle ui/initialize response
            if (message.id && message.result) {
                console.log("MCP UI initialized:", message.result);
                // Extract API key from context if available
                if (message.result.context && message.result.context.apiKey) {
                    apiKey = message.result.context.apiKey;
                }
            }

            // Handle tool result notification
            if (message.method === "ui/notifications/tool-result") {
                console.log("Received tool result:", message.params);
                toolResult = message.params;

                // Extract transcrippets from structuredContent
                const structuredContent = toolResult.structuredContent || toolResult;

                // Extract API key from UI metadata
                if (structuredContent._ui && structuredContent._ui.apiKey) {
                    apiKey = structuredContent._ui.apiKey;
                    console.log("API key extracted from structuredContent");
                }

                const response = structuredContent.response;

                // Handle both find_transcrippets (array) and create_transcrippet (single object)
                const transcrippets = Array.isArray(response) ? response : [response];

                // Render each transcrippet
                const container = document.getElementById("transcrippet-container");
                container.innerHTML = '';

                for (const transcrippet of transcrippets) {
                    if (transcrippet && transcrippet.transcrippet_guid) {
                        await renderTranscrippet(transcrippet.transcrippet_guid, container);
                    }
                }
            }

            // Handle tool input notification (contains API key)
            if (message.method === "ui/notifications/tool-input") {
                console.log("Received tool input:", message.params);
                // API key should be available from the host context
                // We'll extract it when rendering
            }
        });

        // Render a single transcrippet
        async function renderTranscrippet(transcrippetGuid, container) {
            // Create iframe for this transcrippet
            const iframeId = `aiera-transcrippet-${transcrippetGuid}`;
            const iframe = document.createElement('iframe');
            iframe.id = iframeId;
            iframe.width = '100%';
            iframe.style.border = 'none';
            iframe.style.marginBottom = '20px';
            container.appendChild(iframe);

            // Initialize Aiera SDK module
            const module = new Aiera.Module(
                "https://public.aiera.com/aiera-sdk/0.0.69/modules/Transcrippet/index.html",
                iframeId
            );

            await module.load();

            // Authenticate with API key from structuredContent
            if (apiKey) {
                module.authenticateApiKey(apiKey);
            } else {
                console.error("No API key available for authentication");
                return;
            }

            // Configure transcrippet when authenticated
            module.on("authenticated", () => {
                module.configure({
                    options: {
                        transcrippetGuid: transcrippetGuid
                    }
                });
            });

            // Handle dynamic height
            module.on("transcrippet-height", (height) => {
                iframe.style.height = height + 'px';
            });
        }
    </script>
</body>
</html>"""


def generate_transcrippet_ui_html(api_key: str, transcrippet_guid: str) -> str:
    """Generate HTML for embedding a transcrippet UI component (Claude MCP format).

    Args:
        api_key: The Aiera API key for authentication
        transcrippet_guid: The GUID of the transcrippet to display

    Returns:
        HTML string for embedding the transcrippet with values substituted
    """
    # Get template and substitute placeholders for Claude MCP inline embedding
    template = get_transcrippet_template()
    return template.replace("{{apiKey}}", api_key).replace(
        "{{transcrippetGuid}}", transcrippet_guid
    )


async def find_transcrippets(args: FindTranscrippetsArgs) -> FindTranscrippetsResponse:
    """Find and retrieve Transcrippets™, filtered by various identifiers and date ranges."""
    logger.info("tool called: find_transcrippets")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/transcrippets/",
        api_key=api_key,
        params=params,
    )

    # Add public URLs to each transcrippet in the response
    if raw_response.get("response") and isinstance(raw_response["response"], list):
        for transcrippet in raw_response["response"]:
            if transcrippet.get("transcrippet_guid"):
                guid = transcrippet["transcrippet_guid"]
                transcrippet["public_url"] = (
                    f"https://public.aiera.com/shared/transcrippet.html?id={guid}"
                )

    # Return the structured response with the added public URLs
    return validate_response_model(
        raw_response, FindTranscrippetsResponse, "find_transcrippets"
    )


async def create_transcrippet(
    args: CreateTranscrippetArgs,
) -> CreateTranscrippetResponse:
    """Create a new Transcrippet™ from an event transcript segment."""
    logger.info("tool called: create_transcrippet")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    data = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="POST",
        endpoint="/transcrippets/create",
        api_key=api_key,
        data=data,
    )

    # Add public URL to the response data before validation
    if raw_response.get("response") and raw_response["response"].get(
        "transcrippet_guid"
    ):
        guid = raw_response["response"]["transcrippet_guid"]
        raw_response["response"][
            "public_url"
        ] = f"https://public.aiera.com/shared/transcrippet.html?id={guid}"

    # Return the structured response with the added public URL
    return validate_response_model(
        raw_response, CreateTranscrippetResponse, "create_transcrippet"
    )


async def delete_transcrippet(
    args: DeleteTranscrippetArgs,
) -> DeleteTranscrippetResponse:
    """Delete a Transcrippet™ by its ID."""
    logger.info("tool called: delete_transcrippet")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)

    try:
        raw_response = await make_aiera_request(
            client=client,
            method="POST",
            endpoint=f"/transcrippets/{args.transcrippet_id}/delete",
            api_key=api_key,
            params=params,
        )

        # Check if deletion was successful
        success = True
        message = "Transcrippet deleted successfully"

        # If there's an error in the response, mark as failed
        if "error" in raw_response:
            success = False
            message = raw_response.get("error", "Deletion failed")
        elif raw_response.get("response", {}).get("error"):
            success = False
            message = raw_response["response"].get("error", "Deletion failed")

        return DeleteTranscrippetResponse(
            success=success,
            message=message,
            instructions=raw_response.get("instructions", []),
            citation_information=[],
        )

    except Exception as e:
        return DeleteTranscrippetResponse(
            success=False,
            message=f"Failed to delete transcrippet: {str(e)}",
            instructions=[],
            citation_information=[],
        )


# Legacy registration functions removed - all tools now registered via registry
