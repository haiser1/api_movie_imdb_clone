"""Reusable pagination helper."""

from flask import request as flask_request


def get_pagination_params(request=None):
    """Extract and validate pagination parameters from query string.

    Args:
        request: Flask request object (uses flask.request if None).

    Returns:
        tuple: (page, per_page) with validated values.
    """
    req = request or flask_request
    try:
        page = max(1, int(req.args.get("page", 1)))
    except (ValueError, TypeError):
        page = 1
    try:
        per_page = min(100, max(1, int(req.args.get("per_page", 20))))
    except (ValueError, TypeError):
        per_page = 20
    return page, per_page


def paginate(query, page, per_page):
    """Apply pagination to a SQLAlchemy query.

    Args:
        query: SQLAlchemy query object.
        page: Page number (1-indexed).
        per_page: Items per page.

    Returns:
        tuple: (items_list, meta_dict) where meta contains pagination info.
    """
    total = query.count()
    total_pages = (total + per_page - 1) // per_page if total > 0 else 0
    items = query.offset((page - 1) * per_page).limit(per_page).all()

    meta = {
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
    }
    return items, meta
