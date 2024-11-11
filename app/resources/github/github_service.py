import httpx
from typing import List, Dict, Optional
from urllib.parse import urlparse 
from utils.logger import logger

class GitHubService:
    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token
        self.base_url = "https://api.github.com"
        self.headers = {"Authorization": f"token {self.github_token}"} if self.github_token else {}

    def extract_repo_details(self, repo_url: str) -> Dict[str, str]:
        """
        Extract owner and repository name from the GitHub repository URL.
        """
        parsed_url = urlparse(repo_url)
        repo_path = parsed_url.path.strip("/").split("/")
        if len(repo_path) < 2:
            raise ValueError("Invalid GitHub repository URL.")
        return {"owner": repo_path[0], "repo": repo_path[1]} 
    
    async def fetch_pr_files(self, repo_url: str, pr_number: int) -> List[Dict[str, str]]:
        """
        Fetch the list of files changed in the given pull request.
        
        :param repo_url: GitHub repository URL
        :param pr_number: Pull request number
        :return: List of files with file names and URLs to raw content
        """
        repo_details = self.extract_repo_details(repo_url)
        pr_files_url = f"{self.base_url}/repos/{repo_details['owner']}/{repo_details['repo']}/pulls/{pr_number}/files"

        async with httpx.AsyncClient() as client:
            response = await client.get(pr_files_url, headers=self.headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            files = response.json()

        return [{"filename": file["filename"], "raw_url": file["raw_url"]} for file in files]

    async def fetch_file_content(self, raw_url: str) -> str:
        """
        Fetch the raw content of a file from GitHub, following redirects if necessary.
        
        :param raw_url: URL to the raw file content
        :return: File content as a string
        """
        async with httpx.AsyncClient() as client:
            try:
                # Attempt to fetch file content, with automatic redirect following
                response = await client.get(raw_url, headers=self.headers, follow_redirects=True)
                response.raise_for_status()
                return response.text
            
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 302:
                    # Handle manual redirect in case follow_redirects doesn't work
                    redirect_url = e.response.headers.get("Location")
                    # logger.error(f"Redirected to {redirect_url}. Retrying with new URL.")
                    
                    # Retry fetching the content with the new redirected URL
                    response = await client.get(redirect_url, headers=self.headers)
                    response.raise_for_status()
                    return response.text
                else:
                    logger.error(f"Failed to fetch content for {raw_url}: {e}")
                    raise

    async def fetch_pr_code_files(self, repo_url: str, pr_number: int) -> List[Dict[str, str]]:
        """
        Fetches and returns the content of all code files in a given pull request.
        
        :param repo_url: GitHub repository URL
        :param pr_number: Pull request number
        :return: List of dictionaries containing file names and file contents
        """
        files = await self.fetch_pr_files(repo_url, pr_number)
        code_files = []

        for file in files:
            try:
                content = await self.fetch_file_content(file["raw_url"])
                code_files.append({"name": file["filename"], "content": content})
            except Exception as e:
                logger.error(f"Failed to fetch content for {file['filename']}: {e}") 
                

        return code_files
