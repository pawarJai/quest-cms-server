def format_response(data=None, message: str = "", success: bool = True):
    return {
        "status": "success" if success else "error",
        "message": message,
        "data": data,
    }
