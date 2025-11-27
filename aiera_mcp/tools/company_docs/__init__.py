#!/usr/bin/env python3

"""Company docs domain for Aiera MCP."""

from .tools import (
    find_company_docs,
    get_company_doc,
    get_company_doc_categories,
    get_company_doc_keywords,
)
from .models import (
    FindCompanyDocsArgs,
    GetCompanyDocArgs,
    GetCompanyDocCategoriesArgs,
    GetCompanyDocKeywordsArgs,
    FindCompanyDocsResponse,
    GetCompanyDocResponse,
    GetCompanyDocCategoriesResponse,
    GetCompanyDocKeywordsResponse,
    CompanyDocItem,
    CompanyDocDetails,
    CategoryKeyword,
)

__all__ = [
    # Tools
    "find_company_docs",
    "get_company_doc",
    "get_company_doc_categories",
    "get_company_doc_keywords",
    # Parameter models
    "FindCompanyDocsArgs",
    "GetCompanyDocArgs",
    "GetCompanyDocCategoriesArgs",
    "GetCompanyDocKeywordsArgs",
    # Response models
    "FindCompanyDocsResponse",
    "GetCompanyDocResponse",
    "GetCompanyDocCategoriesResponse",
    "GetCompanyDocKeywordsResponse",
    # Data models
    "CompanyDocItem",
    "CompanyDocDetails",
    "CategoryKeyword",
]
