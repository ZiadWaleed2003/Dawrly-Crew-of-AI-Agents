from datetime import datetime
from crewai import Agent, Task
import json
import os

from app.clients import get_llm_with_tool_use
from app.models import AllExtractedData
from app.tools.scraping_tool import web_scraping_firecrawl

class JobScrutinizerAgent:
    def __init__(self , input = None):
        self.llm = get_llm_with_tool_use()
        self.user_input = input
        self.scrapping_tools = [web_scraping_firecrawl]
        self.agent = self._create_agent()
        self.task = self.create_task()
        
        
    
    def _create_agent(self):
        return Agent(
            role="Job Scrutinizer",
            goal="Analyze job listings to extract detailed information and evaluate their suitability",
            backstory="""You are an expert job scrutinizer with deep knowledge of various industries and job roles. 
            Your task is to analyze job listings, extract key information, and provide insightful evaluations 
            to help job seekers find the most suitable opportunities.""",
            llm=self.llm,
            verbose=True,
            tools=self.scrapping_tools
        )
    
    def create_task(self, output_dir="./results/"):


        description = "".join([
                    "Analyze the job URLs provided from the previous agent's search results.\n\n",
                    "For each URL:\n",
                    "1. First try to scrape the job information using the web_scraping_firecrawl tool.\n",
                    "2. If the tool failed, just save the URL\n\n",
                    "For each job listing, extract:\n",
                    "- Job title\n",
                    "- Full job description\n",
                    "- Job URL\n\n",
                    "Then evaluate each job based on the requirements from the user input: ""\n\n",
                    "Provide:\n",
                    "- A recommendation rank (out of 5, higher is better)\n",
                    "- Detailed notes explaining your recommendation\n",
                    "- EXCLUDE jobs that use completely different technology stacks or domains from what the user specified (e.g., if user wants Node.js full-stack, exclude .NET or Python backend roles; if user wants AI/ML, exclude pure frontend or system admin roles)\n",
                    "- INCLUDE jobs with similar or related technologies even if not exact matches (e.g., if user wants LangChain, include jobs with LangGraph, LlamaIndex, or similar frameworks; if user wants React, include jobs with Vue or Angular)\n",
                    "- Focus on the DOMAIN and CORE TECHNOLOGY STACK rather than requiring exact tool matches\n\n",
                    "Consider relevancy within the last 3 months (current date: ", datetime.today().strftime('%Y-%m-%d'), ").\n\n",
                    f"CRITICAL: You must return ONLY a valid JSON object that matches this schema {AllExtractedData.model_json_schema()}exact structure:\n",
                    "Do NOT include any text before or after the JSON. Do NOT use markdown formatting. Do NOT include explanations, thoughts, or any other content. Return ONLY the raw JSON object.",
                    "Revise your answer again before sending it as the final answer to ensure that it includes only the results following the schema no additional texts or anything else other than the results!"])
        
        self.task = Task(
            description=description,
            expected_output="A JSON object containing job data entries with detailed analysis.",
            # output_json=AllExtractedData,
            output_file=os.path.join(output_dir, "step_3_job_scrutinizer_results.json"),
            agent=self.agent
        )
        return self.task
    
    def scrutinize_jobs(self, output_dir="./results/"):
        return self.create_task(output_dir) 