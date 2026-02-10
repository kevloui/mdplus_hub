from arq.connections import RedisSettings

from src.config import settings
from src.workers.tasks.inference_task import run_inference
from src.workers.tasks.training_task import train_glimps_model


def parse_redis_url(url: str) -> RedisSettings:
    from urllib.parse import urlparse

    parsed = urlparse(str(url))
    return RedisSettings(
        host=parsed.hostname or "localhost",
        port=parsed.port or 6379,
        database=int(parsed.path.lstrip("/") or 0),
    )


class WorkerSettings:
    functions = [
        train_glimps_model,
        run_inference,
    ]

    redis_settings = parse_redis_url(str(settings.redis_url))
    max_jobs = 10
    job_timeout = 3600
