from app.core.redis import redis_db

PREFIX = "blacklist:"

def add(jti: str, expires_in: int):
    redis_db.setex(f"{PREFIX}{jti}", expires_in, "1")

def exists(jti: str) -> bool:
    return redis_db.exists(f"{PREFIX}{jti}") == 1