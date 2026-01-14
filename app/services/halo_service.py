from app.utils.logger import logger

def get_halo():
    logger.info("GET /halo dipanggil")
    return {
        "status": "success",
        "message": "Halo from flask",
        "data": "Empty Result"
    }

def post_halo(payload):
    logger.info(f"POST /halo payload: {payload}")
    return {
        "status": "success",
        "message": payload.get("message", "Post Halo"),
        "data": payload
    }
