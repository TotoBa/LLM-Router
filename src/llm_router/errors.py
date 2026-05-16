from __future__ import annotations


class RouterError(Exception):
    def __init__(self, message: str, status_code: int, error_type: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.error_type = error_type
        self.message = message


def error_response(message: str, error_type: str) -> dict:
    return {
        "error": {
            "message": message,
            "type": error_type,
        }
    }
