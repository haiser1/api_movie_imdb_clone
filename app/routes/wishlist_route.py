"""Wishlist routes — user wishlist management."""

from flask import Blueprint, request, g

from app.helper.auth_middleware import jwt_required
from app.helper.base_response import response_success
from app.helper.error_handler import handle_errors
from app.helper.pagination import get_pagination_params
from app.schema.wishlist_schema import WishlistCreateSchema, WishlistUpdateSchema
from app.services import wishlist_service

wishlist_bp = Blueprint("wishlists", __name__)


@wishlist_bp.route("/")
@jwt_required
@handle_errors
def list_wishlists():
    """List user's wishlist items with movie details."""
    page, per_page = get_pagination_params()
    items, meta = wishlist_service.list_wishlists(
        g.current_user.get("sub"), page, per_page
    )
    return response_success("Wishlist retrieved", data=items, meta=meta)


@wishlist_bp.route("/", methods=["POST"])
@jwt_required
@handle_errors
def create_wishlist():
    """Add a movie to the user's wishlist."""
    body = WishlistCreateSchema(**request.get_json())
    item = wishlist_service.create_wishlist(g.current_user.get("sub"), body)
    return response_success("Added to wishlist", data=item, status_code=201)


@wishlist_bp.route("/<id>", methods=["PUT"])
@jwt_required
@handle_errors
def update_wishlist(id):
    """Update a wishlist item's scheduled watch date."""
    body = WishlistUpdateSchema(**request.get_json())
    item = wishlist_service.update_wishlist(g.current_user.get("sub"), id, body)
    return response_success("Wishlist updated", data=item)


@wishlist_bp.route("/<id>", methods=["DELETE"])
@jwt_required
@handle_errors
def delete_wishlist(id):
    """Remove a movie from the user's wishlist."""
    wishlist_service.delete_wishlist(g.current_user.get("sub"), id)
    return response_success("Removed from wishlist")
