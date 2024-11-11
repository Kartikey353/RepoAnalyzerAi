from core.settings import get_settings
from typing import List, Dict, Any
import json 
import google.generativeai as genai

# Configure OpenAI with API key 
settings = get_settings()


# class OpenAIService:
#     @staticmethod
#     async def analyze_code(code_files: List[Dict[str, Any]]) -> Dict[str, Any]:
#         """
#         Sends code files to OpenAI for analysis and receives structured feedback.
        
#         :param code_files: List of code files with file names and contents
#         :return: Analysis results in a structured format or a rate limit message if limit is reached
#         """
#         prompt = OpenAIService.construct_prompt(code_files)
#         try:
#             # Make the asynchronous API request to OpenAI's GPT-3.5-turbo model
#             response = await openai.chat.completions.create(
#                 model="gpt-3.5-turbo",
#                 messages=[
#                     {"role": "system", "content": "You are a code review assistant."},
#                     {"role": "user", "content": prompt}
#                 ],
#                 max_tokens=1500,
#                 temperature=0.2
#             ) 

#             print(response) 
#             print(response.choices[0].message)
            
#             # # Parse and return the response from OpenAI
#             # analysis = response['choices'][0]['message']['content'] 
#             # print(analysis)
#             analysis = {
#             "files": [
#                 {
#                     "name": "example.py",
#                     "issues": [
#                         {
#                             "type": "style",
#                             "line": 10,
#                             "description": "Line is too long.",
#                             "suggestion": "Break it into multiple lines."
#                         },
#                         {
#                             "type": "bug",
#                             "line": 20,
#                             "description": "Possible null pointer.",
#                             "suggestion": "Add a null check."
#                         }
#                     ]
#                 },
#                 {
#                     "name": "test.cpp",
#                     "issues": [
#                         {
#                             "type": "performance",
#                             "line": 15,
#                             "description": "Consider using a more efficient sorting algorithm.",
#                             "suggestion": "Use std::sort instead of custom sorting logic."
#                         }
#                     ]
#                 }
#             ],
#             "summary": {
#                 "total_files": 2,
#                 "total_issues": 3,
#                 "critical_issues": 1
#             }
#         } 
#             return analysis
        
#         except openai.error.RateLimitError:
#             # Handle the rate limit error without retrying
#             print("Rate limit exceeded. Returning empty results or a rate limit message.")
#             return {
#                 "files": [],
#                 "summary": {
#                     "total_files": 0,
#                     "total_issues": 0,
#                     "critical_issues": 0
#                 },
#                 "message": "Rate limit exceeded. Please try again later."
#             }

#     @staticmethod
#     def construct_prompt(code_files: List[Dict[str, Any]]) -> str:
#         """
#         Constructs a prompt to send to OpenAI based on code files.
        
#         :param code_files: List of code files with their content
#         :return: A formatted prompt string
#         """
#         prompt = (
#             "Analyze the following code files for style, bugs, performance, and best practices. "
#             "Provide the analysis results in the following JSON format:\n\n"
#             "return {\n"
#             "    \"files\": [\n"
#             "        {\n"
#             "            \"name\": \"example.py\",\n"
#             "            \"issues\": [\n"
#             "                {\n"
#             "                    \"type\": \"style\",\n"
#             "                    \"line\": 10,\n"
#             "                    \"description\": \"Line is too long.\",\n"
#             "                    \"suggestion\": \"Break it into multiple lines.\"\n"
#             "                },\n"
#             "                {\n"
#             "                    \"type\": \"bug\",\n"
#             "                    \"line\": 20,\n"
#             "                    \"description\": \"Possible null pointer.\",\n"
#             "                    \"suggestion\": \"Add a null check.\"\n"
#             "                }\n"
#             "            ]\n"
#             "        }\n"
#             "    ],\n"
#             "    \"summary\": {\n"
#             "        \"total_files\": 1,\n"
#             "        \"total_issues\": 2,\n"
#             "        \"critical_issues\": 1\n"
#             "    }\n"
#             "}\n\n"
#             "Here are the code files to analyze:\n\n"
#         )
#         for file in code_files:
#             prompt += f"File: {file['name']}\nContent:\n{file['content']}\n\n"
#         return prompt

#     @staticmethod
#     def parse_analysis(analysis_text: str) -> Dict[str, Any]:
#         """
#         Parses the raw analysis text from OpenAI into structured output.
        
#         :param analysis_text: Raw analysis result from OpenAI
#         :return: A structured dictionary format of the analysis
#         """
#         try:
#             # Attempt to parse the response as JSON directly
#             parsed_analysis = json.loads(analysis_text)
#             # Validate the structure
#             if "files" in parsed_analysis and "summary" in parsed_analysis:
#                 return parsed_analysis
#         except json.JSONDecodeError:
#             # Handle parsing errors and log them
#             print("Failed to parse JSON from OpenAI response. Returning empty result.")
        
#         # If parsing fails, return a default empty structure
#         return {
#             "files": [],
#             "summary": {
#                 "total_files": 0,
#                 "total_issues": 0,
#                 "critical_issues": 0
#             }
#         }




class OpenAIService:
    @staticmethod
    async def analyze_code(code_files: List[Dict[str, Any]]) -> str:
        """
        Sends code files to OpenAI for analysis once, without retries.
        
        :param code_files: List of code files with file names and contents
        :return: Analysis results if successful, or an empty response if rate limited or an error occurs
        """
        prompt = OpenAIService.construct_prompt(code_files)  
        print("prompt", prompt)
        genai.configure(api_key="AIzaSyBSQmmMVLf6Fxekbo3eOwWSdDvx2kkw3Uc")
        model = genai.GenerativeModel("gemini-1.5-flash")

        try:
            # Make the API request to OpenAI's GPT-3.5-turbo model
            response = model.generate_content(
                f'''{prompt}'''
            ) 
            # Parse the response and return structured analysis
            analysis = response.text
            return analysis

        except:
            # Handle the rate limit error without retrying
            print("Rate limit exceeded. Returning empty results or a rate limit message.")
            return {
                "files": [],
                "summary": {
                    "total_files": 0,
                    "total_issues": 0,
                    "critical_issues": 0
                },
                "message": "Rate limit exceeded. Please try again later."
            }
    

    @staticmethod
    def construct_prompt(code_files: List[Dict[str, Any]]) -> str:
        """
        Constructs a prompt to send to OpenAI based on code files.
        
        :param code_files: List of code files with their content
        :return: A formatted prompt string
        """
        prompt = (
            "Analyze the following code files for style, bugs, performance, and best practices. "
            "Provide the analysis results in the following JSON format:\n\n"
            "return {\n"
            "    \"files\": [\n"
            "        {\n"
            "            \"name\": \"example.py\",\n"
            "            \"issues\": [\n"
            "                {\n"
            "                    \"type\": \"style\",\n"
            "                    \"line\": 10,\n"
            "                    \"description\": \"Line is too long.\",\n"
            "                    \"suggestion\": \"Break it into multiple lines.\"\n"
            "                },\n"
            "                {\n"
            "                    \"type\": \"bug\",\n"
            "                    \"line\": 20,\n"
            "                    \"description\": \"Possible null pointer.\",\n"
            "                    \"suggestion\": \"Add a null check.\"\n"
            "                }\n"
            "            ]\n"
            "        }\n"
            "    ],\n"
            "    \"summary\": {\n"
            "        \"total_files\": 1,\n"
            "        \"total_issues\": 2,\n"
            "        \"critical_issues\": 1\n"
            "    }\n"
            "}\n\n" 
            "and dont add any extra thing like explanation or something i need response in above format only\n\n"
            "Here are the code files to analyze:\n\n"
        )
        for file in code_files:
            prompt += f"File: {file['name']}\nContent:\n{file['content']}\n\n"
        return prompt

    @staticmethod
    def parse_analysis(analysis_text: str) -> Dict[str, Any]:
        """
        Parses the raw analysis text from OpenAI into structured output.
        
        :param analysis_text: Raw analysis result from OpenAI
        :return: A structured dictionary format of the analysis
        """
        try:
            # Attempt to parse the response as JSON directly
            parsed_analysis = json.loads(analysis_text)
            # Validate the structure
            if "files" in parsed_analysis and "summary" in parsed_analysis:
                return parsed_analysis
        except json.JSONDecodeError:
            # Handle parsing errors and log them
            print("Failed to parse JSON from OpenAI response. Returning empty result.")
        
        # If parsing fails, return a default empty structure
        return {
            analysis_text
        }
