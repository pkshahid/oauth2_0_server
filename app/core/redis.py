import redis
from app.core.config import settings

redis_client = None

if settings.REDIS_URL:
    redis_client = redis.Redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
    )