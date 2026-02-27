from flask import jsonify


def response_success(message: str, data: dict, status_code: int = 200):
    return jsonify(
        {
            "success": True,
            "message": message,
            "data": data,
        }
    ), status_code


def response_error(message: str, error: any, status_code: int = 400):
    return jsonify(
        {
            "success": False,
            "message": message,
            "error": error,
        }
    ), status_code
