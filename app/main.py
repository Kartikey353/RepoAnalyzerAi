from fastapi import FastAPI 
from resources.github.task_route import GitHubPRRouter
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI() 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(GitHubPRRouter().router, prefix="/api/v1")
