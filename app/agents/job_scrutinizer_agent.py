from crewai import Agent, Task

from typing import List
import os

from app.clients import get_llm_sec
from app.models import AllExtractedData
from app.tools.scraping_tool import web_scraping_firecrawl, web_scraping_tool

class JobScrutinizerAgent:
    def __init__(self):
        self.llm = get_llm_sec()
        self.agent = self._create_agent()
        self.task = self.create_task()
        self.scrapping_tools = [web_scraping_firecrawl]
    
    def _create_agent(self):
        return Agent(
            role="Job Scrutinizer",
            goal="Analyze job listings to extract detailed information and evaluate their suitability",
            backstory="""You are an expert job scrutinizer with deep knowledge of various industries and job roles. 
            Your task is to analyze job listings, extract key information, and provide insightful evaluations 
            to help job seekers find the most suitable opportunities.""",
            llm=self.llm,
            verbose=True,
            tools=[web_scraping_firecrawl]
        )
    
    def create_task(self, output_dir="./results/"):
        description = """
        Analyze the job URLs provided from the previous agent's search results.
        
        For each URL:
        1. First try to scrape the job information using the web_scraping_firecrawl.
        3. If the tool failed, just save the URL with minimal information.
        
        For each job listing, extract:
        - Job title
        - Full job description
        - Job URL
        
        Then evaluate each job based on the requirements from the {user_input} and provide:
        - A recommendation rank (out of 5, higher is better)
        - Detailed notes explaining your recommendation
        - if the job opposite the specified skills from the user input mentioned you have to neglect this job and don't include it to your answer
        - eg if the user looking for a NodeJS developer role and the specified skills had nodejs in it and the result had C# .Net you have to neglect this result
        
        Format the results into a JSON object following the AllExtractedData schema:
        {"jobs": [
          {
            "job_title": "...",
            "job_description": "...",
            "job_url": "...",
            "agent_recommendation_rank": 5,
            "agent_recommendation_notes": ["...", "..."]
          },
          ...
        ]}
        
        Do NOT output any additional text, markdown, <think> tag , or logs after emitting the JSON all i need is just a pure json response!.
        """
        
        self.task = Task(
            description=description,
            expected_output="A JSON object containing job data entries with detailed analysis.",
            output_json=AllExtractedData,
            output_file=os.path.join(output_dir, "step_3_job_scrutinizer_results.json"),
            agent=self.agent
        )
        return self.task
    
    def scrutinize_jobs(self, output_dir="./results/"):
        return self.create_task(output_dir) 