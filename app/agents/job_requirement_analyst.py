from crewai import Task, Agent
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import os

from app.clients import get_llm
from datetime import datetime




class JobSearchCriteria(BaseModel):
    # Core requirements
    job_titles: List[str] = Field(..., description="Primary job titles/roles")
    required_skills: List[str] = Field(..., description="Must-have skills")
    preferred_skills: List[str] = Field(default=[], description="Nice-to-have skills")
   
    # Experience and level
    experience_level: str = Field(..., description="Fresh/Junior/Mid/Senior/Lead")
    min_years_experience: Optional[int] = Field(default=None)
   
    # Location and work setup
    locations: List[str] = Field(default=[], description="Preferred locations")
    remote_preference: str = Field(default="any", description="remote/hybrid/onsite/any")
    
    # Specified websites (new - based on task description)
    specified_websites: List[str] = Field(default=[], description="User-specified websites to prioritize")
   
    # Search queries - SIMPLIFIED based on task logic
    search_queries: List[str] = Field(..., description="Optimized search queries for job platforms", min_items=1)


class JobRequirementAnalyst:
    def __init__(self, max_queries=8):
        """
        Args:
            max_queries: Maximum number of queries to generate
        """
        self.llm = get_llm()
        self.max_queries = max_queries
        self.agent = self._create_agent()
        self.task = None
    
    def _create_agent(self):
        return Agent(
            role="Senior Job Search Query Optimizer specializing in converting natural language job requirements into highly effective search queries and keywords for various job boards.",
            
            goal="\n".join([
                "To analyze user job search requirements and extract structured criteria.",
                "Generate optimized search queries for job boards and platforms.",
                "Ensure all important requirements are captured and translated into actionable search terms."
            ]),
            backstory="\n".join([
                "You are an expert career counselor and job search specialist with deep understanding",
                "of how job seekers express their needs and how to translate those into effective",
                "search strategies. You excel at identifying both explicit and implicit requirements",
                "from natural language descriptions and know how different job platforms work."
            ]),
            llm=self.llm,
            verbose=True,
        )
    
    def create_task(self):
        description = "\n".join([
            "A job seeker is looking for opportunities with the following requirements: {user_input}",
            f"Extract structured job search criteria and generate up to {self.max_queries} optimized search queries.",
            "Generate search queries optimized for these top job platforms. Focus on core job titles, primary skills, and location to maximize the initial search hit rate.",
            "For each specified platform (LinkedIn, Indeed, Wuzzuf, RemoteOK), generate a separate search query using the `site:` operator to target that platform directly.", # NEW INSTRUCTION
            "- LinkedIn: Use core job titles and primary skills. Leverage LinkedIn's built-in filters for location and experience level. Include `site:linkedin.com`.",
            "- Indeed: Focus on core keywords (job title, primary skills) and location. Include `site:indeed.com`.",
            "- Wuzzuf: Include core job titles and location. Consider English variations. Include `site:wuzzuf.net` (or appropriate domain).", # Updated domain example
            "- RemoteOK: Short, remote-focused keywords, emphasizing core tech stack relevant to the role. Include `site:remoteok.com`.",
            "If user specifies particular websites, prioritize those platforms in query generation and ONLY generate queries for those sites.", # Clarified
            "If no specific websites mentioned, create general queries for ALL four platforms listed above, each with its respective `site:` operator.", # Clarified
            "IMPORTANT: The generated search queries should be designed to effectively locate actual job posting pages when executed by a search tool. Do NOT include actual job posting URLs or search results in your output.",
            "Focus on generating queries that, when used by a search agent, will return individual job listings that can be scraped for detailed information.",
            "Focus on:",
            "- Job titles and role variations",
            "- Required skills and technologies (only primary/fundamental ones for initial search)",
            "- Location preferences (including remote options)",
            "- Industry-specific terms",
            "Ensure queries are specific enough to avoid irrelevant results but broad enough to capture all relevant opportunities.",
            "Do NOT include highly specific or niche technical keywords or any skills from the user input these won't be needed here right now (e.g., specific cloud providers like GCP/AWS/Azure, specific LLM frameworks like Hugging Face/fine tuning) in these initial search queries. These will be used by a later agent (Job Scrutinizer Agent) for detailed job description analysis.",
            f"The search queries should aim to find open jobs, excluding expired ones. Consider that a typical maximum job age for relevance is 3 months from now (current date: {datetime.today().strftime('%Y-%m-%d')})."
        ])

        self.task = Task(
            description=description,
            expected_output="A JSON object containing structured job requirements and optimized search queries.",
            output_json=JobSearchCriteria,
            output_file=os.path.join("./results/", "step_1_job_requirements_analysis.json"),
            agent=self.agent,
        )
        return self.task
    
    def analyze_requirements(self):
        """Main method to analyze job requirements"""
        task = self.create_task()
        return task