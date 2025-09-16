from crewai import Task, Agent
from pydantic import BaseModel, Field
from typing import List, Optional
import os

from app.clients import get_llm_main
from datetime import datetime


class JobSearchCriteria(BaseModel):
    job_title: List[str] = Field(..., description="Primary job titles/roles")
    preferred_skills: Optional[List[str]] = Field(default=[], description="Nice-to-have skills")
    experience_level: str = Field(..., description="Fresh/Junior/Mid/Senior/Lead")
    min_years_experience: Optional[int] = Field(default=None)
    locations: List[str] = Field(default=[], description="Preferred locations")
    remote_preference: str = Field(default="any", description="remote/hybrid/onsite/any")
    specified_websites: List[str] = Field(default=[], description="User-specified websites to prioritize")
    search_queries: List[str] = Field(..., description="Optimized search queries for job platforms", min_length=1)


class JobRequirementAnalyst:
    def __init__(self, user_id, input=None ,max_queries=8):
        self.llm = get_llm_main()
        self.max_queries = max_queries
        self.user_input = input
        self.user_id = user_id
        self.agent = self._create_agent()
        self.task = self.create_task()

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
                "A job seeker is looking for opportunities with the following requirements: {user_input}",
                "",
                "Extract structured job search criteria and generate 8 optimized search queries using a multi-tier strategy.",
                "",
                "CRITICAL: ALL queries must include job-specific keywords to ensure they return actual job postings, not courses, profiles, or articles.",
                "",
                "Generate two types of queries:",
                "",
                "BROAD QUERIES (3-4 total): Simple but job-focused",
                "- Must include job indicator words: 'jobs', 'careers', 'hiring', 'vacancy', 'opening', 'position'",
                "- Use core job title provided by the user like {user_input['job_title']} + location like user_input['locations'] + job indicator",
                "- Example: 'data scientist jobs New York', 'software engineer hiring San Francisco'",
                "- NOT like this: 'NLP Cairo' (too vague, will return non-job results)",
                "",
                "PRECISE QUERIES (4-5 total): Detailed with all requirements",
                "- Include specific skills, experience level, and multiple criteria",
                "- Use site: operator for platforms mentioned by user",
                "- Include phrases like 'years experience', specific technologies, seniority level",
                "- Example: 'senior data scientist Python machine learning \"5+ years\" remote jobs'",
                "",
                "MANDATORY RULES:",
                "1. EVERY query must be job-focused - include words like: jobs, hiring, careers, vacancy, opening, position",
                "2. Even broad queries must be clearly about job postings",
                "3. Do NOT prefix queries with tier labels or numbers",
                "4. Mix query order naturally - don't group all broad or all precise together",
                f"5. Add recency hints where relevant: 'hiring 2024', 'new opening', etc. (current: {datetime.today().strftime('%Y-%m-%d')})",
                "6. For specific platforms use: site:linkedin.com/jobs , site:indeed.com , site:remoteok.com ,site:arc.dev/remote-jobs ,site:wellfound.com",
                "",
                "OUTPUT: Return exactly 10 search query strings, one per line, no labels or categories."
            ])
        
        self.task = Task(
            description=description,
            expected_output="A JSON object containing structured job requirements and optimized search queries.",
            output_json=JobSearchCriteria,
            output_file=os.path.join(f"./results/{self.user_id}/", "step_1_job_requirements_analysis.json"),
            agent=self.agent,
        )
        return self.task

    def analyze_requirements(self):
        return self.create_task()
