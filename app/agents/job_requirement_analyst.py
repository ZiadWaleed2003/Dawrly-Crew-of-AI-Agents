from crewai import Task, Agent
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import os

from app.clients import get_llm




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
            role="Job Requirement Analyst",
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
            "",
            "Generate search queries optimized for these top job platforms:",
            "- LinkedIn: Use Boolean operators (AND/OR), quotes for exact terms, location filters",
            "- Indeed: Focus on keywords + location, use title:() syntax for job titles",
            "- Wuzzuf: Include Arabic/English variations, local market focus",
            "- RemoteOK: Short, remote-focused keywords, tech stack emphasis",
            "",
            "If user specifies particular websites, prioritize those platforms in query generation.",
            "If no specific websites mentioned, create general queries that work across all four platforms.",
            "",
            "IMPORTANT: Search queries must lead directly to actual job posting pages, not career advice blogs, job search tips, or company overview pages.",
            "Focus on queries that will return individual job listings that can be scraped for detailed information.",
            "",
            "Focus on:",
            "- Job titles and role variations",
            "- Required skills and technologies",
            "- Location preferences (including remote options)",
            "- Experience level indicators",
            "- Industry-specific terms",
            "",
            "Ensure queries are specific enough to avoid irrelevant results but broad enough to capture all relevant opportunities.",
            "Ensure that the job is still available not an old one and closed"
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