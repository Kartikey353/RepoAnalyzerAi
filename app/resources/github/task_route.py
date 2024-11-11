from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from core.database import get_session
from core.redis_service import RedisService
from resources.github.github_service import GitHubService
from resources.github.tasks   import TaskService
from models.code import TaskResult
from typing import Optional, Any, Dict
import uuid 

class GitHubPRRouter:
    def __init__(self):
        self.router = APIRouter()
        self.router.post("/analyzePR", response_model=Dict[str, Any])(self.analyze_pr)
        self.router.get("/status", response_model=Dict[str, Any])(self.get_status)
        self.router.get("/results", response_model=Dict[str, Any])(self.get_results)

    async def analyze_pr(
        self, 
        repo_url: str = Body(...),
        pr_number: int = Body(...),
        github_token: Optional[str] = Body(None),
          db: Session = Depends(get_session)
    ):
        """
        Endpoint to initiate a PR analysis task.
        """
        # Generate a unique task ID
        task_id = str(uuid.uuid4())
        # Schedule the Celery task   
        service = TaskService(db) 
        
        service.analyze_pr_task.apply_async(
            args=[repo_url, pr_number, task_id, github_token],  # Arguments for the task
            countdown=0  # Optional delay (0 starts it immediately)
        )
        return {"task_id": task_id, "status": "Task submitted"}

    async def get_status(
        self,
        task_id: str = Query(...),
        db: Session = Depends(get_session),
    ) -> Dict[str, Any]:
        """
        Endpoint to retrieve the status of a PR analysis task.
        """
        # Check Redis for the task status
        status = RedisService.get_task_status(task_id)
        
        if not status:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        
        return {"task_id": task_id, "status": status}

    async def get_results(
        self,
        task_id: str = Query(...),
        db: Session = Depends(get_session),
    ) -> Dict[str, Any]:
        """
        Endpoint to retrieve the analysis results for a PR.
        """
        # First, try to get the result from Redis cache
        results = RedisService.get_task_result(task_id)
        
        if results:
            return results
        
        # If not in Redis, retrieve from PostgreSQL
        task_result = db.query(TaskResult).filter_by(task_id=task_id).first()
        if not task_result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Results not found")
        
        return {
            "task_id": task_id,
            "status": task_result.status.value,
            "results": task_result.results
        }

github_pr_router = GitHubPRRouter().router
