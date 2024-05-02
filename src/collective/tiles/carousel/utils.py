"""Utilities."""

from plone import api
from plone.app.querystring import queryparser


def parse_query_from_data(data, context=None):
    """Parse query from data dictionary"""
    if context is None:
        context = api.portal.get()
    query = data.get("query", {}) or {}
    try:
        parsed = queryparser.parseAndModifyFormquery(
            context,
            query,
            data.get("sort_on"),
            "desc" if data.get("sort_reversed", False) else "asc",
        )
    except KeyError:
        parsed = {}

    return parsed
