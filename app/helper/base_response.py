from typing import Any, Optional

from flask import jsonify


def response_success(
    message: str,
    data: Optional[Any] = None,
    meta: Optional[dict] = None,
    status_code: int = 200,
):
    body = {
        "success": True,
        "message": message,
    }
    if data is not None:
        body["data"] = data
    if meta is not None:
        body["meta"] = meta
    return jsonify(body), status_code


def response_error(message: str, error: Any = None, status_code: int = 400):
    body = {
        "success": False,
        "message": message,
    }
    if error is not None:
        body["error"] = error
    return jsonify(body), status_code
