import redis
import json
from core.settings import get_settings
settings = get_settings()

# Initialize Redis client with specified host, port, and password
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
)

class RedisService:
    @staticmethod
    def set_task_status(task_id: str, status: str, expiration: int = settings.REDIS_EXPIRATION_SECONDS):
        """
        Set the status of a task in Redis.
        """ 
        redis_client.setex(f"task_status:{task_id}", expiration, status)

    @staticmethod
    def get_task_status(task_id: str):
        """
        Retrieve the status of a task from Redis.
        """
        return redis_client.get(f"task_status:{task_id}")

    @staticmethod
    def set_task_result(task_id: str, result: dict):
        """
        Set the task result in Redis.
        """
        redis_client.setex(f"task_result:{task_id}",600, json.dumps(result))

    @staticmethod
    def get_task_result(task_id: str):
        """
        Retrieve the task result from Redis.
        """
        result = redis_client.get(f"task_result:{task_id}")
        return json.loads(result) if result else None

    @staticmethod
    def delete_task(task_id: str):
        """
        Delete task status and result from Redis.
        """
        redis_client.delete(f"task_status:{task_id}")
