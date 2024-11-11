from celery import Celery
from core.settings import get_settings  
settings = get_settings()

# Configure Celery to use Redis as the broker
celery_app = Celery(
    "app",
    broker=f"redis://default:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
    backend=f"redis://default:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
)

# Set Celery configuration options
celery_app.conf.update(
    result_expires=3600,  # 1 hour expiration for task results
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'], 
    imports=['resources.github.tasks']  # Import the tasks module
) 

