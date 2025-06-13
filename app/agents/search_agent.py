from crewai import Task, Agent
from pydantic import BaseModel, Field
from typing import List
import os
import json

from app.clients import get_llm


class SingleJobSearchResult(BaseModel):
    title: str
    url: str = Field(..., title="the job posting page url")
    content: str  
    score: float
    search_query: str
    platform: str = Field(..., description="LinkedIn/Indeed/Wuzzuf/RemoteOK/Other")
    relevance_notes: str = Field(..., description="Why this result matches the criteria")

class AllJobSearchResults(BaseModel):
    results: List[SingleJobSearchResult]

class SearchAgent:
    def __init__(self, llm, search_tool, score_threshold=6.0):
        self.llm = get_llm()
        self.search_tool = search_tool
        self.score_threshold = score_threshold
        self.agent = self._create_agent()
        self.task = None
    
    def _create_agent(self):
        return Agent(
            role="Job Search Specialist",
            goal="\n".join([
                "To find relevant job postings based on structured search criteria.",
                "Execute search queries and filter results to ensure high-quality job posting URLs.",
                "Score and validate results against the original job requirements."
            ]),
            backstory="\n".join([
                "You are an expert job search specialist who knows how to effectively search",
                "for job opportunities across different platforms. You excel at identifying",
                "genuine job postings and filtering out irrelevant content like blogs,",
                "career advice, or company overview pages. You understand the nuances",
                "of different job boards and can assess the quality and relevance of search results."
            ]),
            llm=self.llm,
            verbose=True,
            tools=[self.search_tool]
        )
    
    def create_task(self, job_requirements_task, output_dir="./results/"):
        """
        Create the search task with context from the job requirements analyst
        
        Args:
            job_requirements_task: The task output from JobRequirementAnalyst
            output_dir: Directory to save results
        """
        self.task = Task(
            description="\n".join([
                "Search for job postings based on the suggested search queries from the Job Requirement Analyst.",
                "You have access to the original job requirements for context validation.",
                "Original Requirements Context:",
                "- Target Job Titles: {job_titles}",
                "- Required Skills: {required_skills}", 
                "- Locations: {locations}",
                "- Remote Preference: {remote_preference}",
                "Search Instructions:",
                "1. Execute each search query from the search_queries list and collect results",
                "2. Filter results to ensure they match the job titles and required skills",
                "3. Prioritize results that mention the target locations or remote work (based on preference)",
                "4. Ignore suspicious links, blog posts, or career advice pages",
                f"5. Only include results with confidence score above {self.score_threshold}",
                "6. Focus on actual job posting pages from LinkedIn, Indeed, Wuzzuf, RemoteOK",
                "",
                "For each valid result, determine the platform:",
                "- LinkedIn: Contains 'linkedin.com' in URL",
                "- Indeed: Contains 'indeed.com' in URL", 
                "- Wuzzuf: Contains 'wuzzuf.net' in URL",
                "- RemoteOK: Contains 'remoteok.io' in URL",
                "- Other: Company websites or other job boards",
                "",
                "Score each result (0-10) based on:",
                "- How well the title matches target job titles (3 points)",
                "- Presence of required skills in the content (3 points)",
                "- Location/remote work alignment (2 points)",
                "- Platform credibility (job boards vs company sites) (2 points)",
                "",
                "Provide clear relevance_notes explaining why each result was selected and scored."
            ]),
            expected_output="A JSON object containing filtered and scored job search results.",
            output_json=AllJobSearchResults,
            output_file=os.path.join(output_dir, "step_2_job_search_results.json"),
            agent=self.agent,
            context=[job_requirements_task]  # Pass the first agent's output as context
        )
        return self.task
    
    def search_jobs(self, job_requirements_task, output_dir="./results/"):
        """
        Main method to execute job search
        
        Args:
            job_requirements_task: The completed task from JobRequirementAnalyst
            output_dir: Directory to save results
            
        Returns:
            Task: The search task to be executed by the crew
        """
        task = self.create_task(job_requirements_task, output_dir)
        return task
    
