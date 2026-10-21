#!/usr/bin/env python3

"""Unit tests for StrictArgsMixin — undeclared tool arguments must fail loudly."""

import pytest
from pydantic import ValidationError

from aiera_mcp.tools.common.models import TRANSPORT_ONLY_ARGUMENT_KEYS
from aiera_mcp.tools.research.models import FindResearchArgs
from aiera_mcp.tools.search.models import SearchResearchArgs


@pytest.mark.unit
class TestStrictArgs:
    """An undeclared argument used to be dropped silently by Pydantic, so a call like
    find_research(bloomberg_ticker=...) ran UNFILTERED against the whole index with no
    error. The model must now be told which argument it got wrong."""

    @pytest.mark.parametrize(
        "model, base_kwargs",
        [(FindResearchArgs, {}), (SearchResearchArgs, {"query_text": "q"})],
    )
    def test_unknown_argument_is_rejected_and_named(self, model, base_kwargs):
        with pytest.raises(ValidationError) as excinfo:
            model(**base_kwargs, ticker="INTC")
        message = str(excinfo.value)
        assert "Unknown argument(s)" in message and "ticker" in message
        # the error lists what IS accepted so the model can self-correct
        assert "bloomberg_ticker" in message

    @pytest.mark.parametrize(
        "model, base_kwargs",
        [(FindResearchArgs, {}), (SearchResearchArgs, {"query_text": "q"})],
    )
    def test_transport_keys_are_tolerated(self, model, base_kwargs):
        # the chat lambda attaches these to every call regardless of the tool schema
        extras = {
            key: "x" for key in TRANSPORT_ONLY_ARGUMENT_KEYS - set(model.model_fields)
        }
        assert (
            extras
        ), "test expects at least one transport key the model does not declare"
        args = model(**base_kwargs, **extras)
        for key in extras:
            assert key not in args.model_dump()

    def test_declared_arguments_still_validate_normally(self):
        args = FindResearchArgs(bloomberg_ticker="INTC:US", page_size="10")
        assert args.bloomberg_ticker == "INTC:US" and args.page_size == 10
