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
    
    # Search queries
    universal_query: str = Field(..., description="General search query usable on any platform")
    platform_queries: Optional[Dict[str, List[str]]] = Field(
        default=None,
        description="Platform-specific optimized search queries (LinkedIn/Indeed/RemoteOK/Wuzzuf)"
    )


class JobRequirementAnalyst:
    def __init__(self, max_queries=8, search_mode="general"):
        """
        Args:
            llm: The language model to use
            max_queries: Maximum number of queries to generate
            search_mode: "general" or "platform_specific"
        """
        self.llm = get_llm()
        self.max_queries = max_queries
        self.search_mode = search_mode
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
    
    def create_task(self, user_input):
        if self.search_mode == "general":
            description = "\n".join([
                "A job seeker is looking for opportunities with the following requirements: {user_input}",
                f"Extract structured job search criteria and generate up to {self.max_queries} universal search queries.",
                "Focus on creating general queries that will work across all job platforms:",
                "- Combine job titles, required skills, and location preferences into concise search terms",
                "- Avoid platform-specific syntax",
                "- Include variations that cover different ways the job might be described",
                "- Prioritize clarity and broad compatibility over platform optimization"
            ])
        else:  # platform_specific
            description = "\n".join([
                "A job seeker is looking for opportunities with the following requirements: {user_input}",
                f"Extract structured job search criteria and generate:",
                f"1. A universal search query (works everywhere)",
                f"2. Up to {self.max_queries} platform-specific optimized search queries for LinkedIn/Indeed/RemoteOK/Wuzzuf",
                "For platform-specific queries:",
                "- LinkedIn: Use Boolean operators (AND/OR), quotes for exact terms",
                "- Indeed: Focus on keywords + location, use title:() syntax",
                "- RemoteOK: Short, remote-focused keywords",
                "- Wuzzuf: Include Arabic/English variations if relevant",
                "Ensure all queries maintain the core requirements while optimizing for each platform's search algorithm."
            ])

        self.task = Task(
            description=description,
            expected_output="A JSON object containing structured job requirements and optimized search queries.",
            output_json=JobSearchCriteria,
            output_file=os.path.join("./results/", "step_1_job_requirements_analysis.json"),
            agent=self.agent,
            context_variables={"user_input": user_input}
        )
        return self.task
    
    def analyze_requirements(self, user_input):
        """Main method to analyze job requirements"""
        task = self.create_task(user_input)
        return task