from resources.github.openai_service import OpenAIService
from resources.github.github_service import GitHubService 
from core.redis_service import RedisService 
from core.celery_app import celery_app
from core.database import get_session
from sqlalchemy.orm import Session
from models.code import TaskResult, TaskStatus
import uuid 
from utils.logger import logger
from typing import Optional  
from sqlalchemy.exc import SQLAlchemyError 
import asyncio 


class TaskService:
    def __init__(self,db:Session):
        self.db = db 

    @celery_app.task(bind=True, autoretry_for=(),retry_backoff=False)
    def analyze_pr_task(self, repo_url: str, pr_number: int, task_id: str, github_token: Optional[str] = None):
        """
        Celery task to fetch code from a GitHub PR and analyze it asynchronously.
        :param repo_url: GitHub repository URL
        :param pr_number: Pull request number
        :param task_id: Unique task ID to track the task
        :param github_token: Optional GitHub token for authentication
        """
        # Set initial task status in Redis 
        RedisService.set_task_status(task_id, TaskStatus.processing.value) 
        
        try:
            # Fetch code files from the GitHub PR
            github_service = GitHubService(github_token=github_token)
            code_files = asyncio.run(github_service.fetch_pr_code_files(repo_url, pr_number))
            # Run code analysis via OpenAI service
            analysis_results = asyncio.run(OpenAIService.analyze_code(code_files)) 
            # Save the results in Redis temporarily
            RedisService.set_task_result(task_id, {
                "status": TaskStatus.completed.value,
                "results": analysis_results
            })
            
            # Update the database with the final result 
            
            total_files = 0
            total_issues = 0
            critical_issues = 0
            task_result = TaskResult(
                task_id=uuid.UUID(task_id),  # Ensure task_id is a valid UUID
                status=TaskStatus.completed,
                results=analysis_results,
                total_files=total_files,
                total_issues=total_issues,
                critical_issues=critical_issues
            ) 

            # self.db.add(task_result)
            # self.db.commit()
            logger.info(f"Task result saved successfully for task_id: {task_id}")

            # Update Redis with task completion
            RedisService.set_task_status(task_id, TaskStatus.completed.value)
        
        except Exception as e: 
            print(e)
            # Handle errors by updating Redis and logging
            RedisService.set_task_status(task_id, TaskStatus.failed.value)
            # raise self.retry(exc=e, countdown=60, max_retries=3) 
        

    async def save_analysis_result(self, task_id: str, analysis_results: dict):
        """
        Save analysis results in PostgreSQL database with error handling.
        """
    # Extract summary data from analysis_results
        total_files = analysis_results["summary"].get("total_files", 0)
        total_issues = analysis_results["summary"].get("total_issues", 0)
        critical_issues = analysis_results["summary"].get("critical_issues", 0)
        print(f"Total Files: {total_files}, Total Issues: {total_issues}, Critical Issues: {critical_issues}")
    # Create the TaskResult object
        try:
            task_result = TaskResult(
                task_id=uuid.UUID(task_id),  # Ensure task_id is a valid UUID
                status=TaskStatus.completed,
                results=analysis_results,
                total_files=total_files,
                total_issues=total_issues,
                critical_issues=critical_issues
            )

            # Debug print to verify task_result values before saving
            print(f"Task Result Details:\n - Task ID: {task_result.task_id}\n"
                f" - Status: {task_result.status}\n - Total Files: {task_result.total_files}\n"
                f" - Total Issues: {task_result.total_issues}\n - Critical Issues: {task_result.critical_issues}")

            # Attempt to save the task result to the database
            self.db.add(task_result)
            self.db.commit()
            logger.info(f"Task result saved successfully for task_id: {task_id}")

        except SQLAlchemyError as e:
            # Rollback in case of an error
            self.db.rollback()
            logger.error(f"SQLAlchemyError: Error saving task result for task_id {task_id}: {e}")
            print(f"SQLAlchemyError: Error saving task result for task_id {task_id}: {e}")  # Additional print for debugging
            raise e  # Optionally re-raise the exception if needed

        except ValueError as ve:
            # Catch ValueErrors specifically, such as UUID conversion errors
            logger.error(f"ValueError: Invalid task_id format for {task_id}. Error: {ve}")
            print(f"ValueError: Invalid task_id format for {task_id}. Error: {ve}")
            raise ve

        except Exception as ex:
            # Catch any other unexpected exceptions
            logger.error(f"Unexpected error while saving task result for task_id {task_id}: {ex}")
            print(f"Unexpected error: {ex}")  # Additional print for debugging
            raise ex