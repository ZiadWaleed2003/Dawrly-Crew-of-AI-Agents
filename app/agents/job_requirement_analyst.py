from crewai import Task, Agent
from pydantic import BaseModel, Field
from typing import List, Optional
import os

from app.clients import get_llm
from datetime import datetime


class JobSearchCriteria(BaseModel):
    job_titles: List[str] = Field(..., description="Primary job titles/roles")
    required_skills: List[str] = Field(..., description="Must-have skills")
    preferred_skills: List[str] = Field(default=[], description="Nice-to-have skills")
    experience_level: str = Field(..., description="Fresh/Junior/Mid/Senior/Lead")
    min_years_experience: Optional[int] = Field(default=None)
    locations: List[str] = Field(default=[], description="Preferred locations")
    remote_preference: str = Field(default="any", description="remote/hybrid/onsite/any")
    specified_websites: List[str] = Field(default=[], description="User-specified websites to prioritize")
    search_queries: List[str] = Field(..., description="Optimized search queries for job platforms", min_items=1)


class JobRequirementAnalyst:
    def __init__(self, max_queries=8):
        self.llm = get_llm()
        self.max_queries = max_queries
        self.agent = self._create_agent()
        self.task = None

    def _create_agent(self):
        return Agent(
            role="Senior Job Search Query Optimizer specializing in converting natural language job requirements into highly effective search queries and keywords for various job boards.",
            goal="".join([
                "To analyze user job search requirements and extract structured criteria.\n",
                "Generate optimized search queries for job boards and platforms.\n",
                "Ensure all important requirements are captured and translated into actionable search terms."
            ]),
            backstory="".join([
                "You are an expert career counselor and job search specialist with deep understanding of how job seekers express their needs and how to translate those into effective search strategies. ",
                "You excel at identifying both explicit and implicit requirements from natural language descriptions and know how different job platforms work."
            ]),
            llm=self.llm,
            verbose=True,
        )

    def create_task(self):
        description = "".join([
                    f"A job seeker is looking for opportunities with the following requirements: {{user_input}}",
                    "Extract structured job search criteria and generate up to {self.max_queries} optimized search queries.",
                    "Generate search queries optimized for these top job platforms and a general Google query:",
                    "- For each specified platform in `specified_websites`, generate a separate query using `site:` to target that site.",
                    "- Additionally generate one broad, general Google query without `site:` to capture cross-platform results.",
                    "- Ensure queries cover job titles, skills (required + preferred), and location criteria.",
                    "- IMPORTANT: The generated search queries should be designed to effectively locate actual job posting pages when executed by a search tool. Do NOT include actual URLs or expired posts.",
                    "- Focus on generating queries that when used will return individual job listings for scraping.",
                    f"- Consider relevancy within the last 3 months (current date: {datetime.today().strftime('%Y-%m-%d')})."
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
        return self.create_task()

# # Post-processing example (to be used after LLM response):
# def construct_queries(criteria: JobSearchCriteria) -> List[str]:
#     titles = " OR ".join(f'\"{t}\"' for t in criteria.job_titles)
#     skills = " OR ".join(criteria.required_skills + criteria.preferred_skills)
#     locations = " OR ".join(criteria.locations)
#     # General Google query
#     general = f"({titles}) ({skills}) ({locations})"
#     queries = [general]
#     # Site-specific queries
#     for site in criteria.specified_websites:
#         queries.append(f"site:{site} ({titles}) ({skills}) ({locations})")
#     return queries
