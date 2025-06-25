from crewai import Task, Agent
from pydantic import BaseModel, Field
from typing import List
import os

from app.clients import get_llm_qwen
from app.tools.search_tools import tavily_search_engine_tool


class SingleJobSearchResult(BaseModel):
    title: str
    url: str = Field(..., title="the job posting page url")
    content: str  
    score: float
    search_query: str
    platform: str = Field(..., description="LinkedIn/Indeed/Wuzzuf/RemoteOK/Glassdoor/Other")
    relevance_notes: str = Field(..., description="Why this result matches the criteria")

class AllJobSearchResults(BaseModel):
    results: List[SingleJobSearchResult]

class SearchAgent:
    def __init__(self, score_threshold):
        self.llm = get_llm_qwen()
        self.search_tool = [tavily_search_engine_tool]
        self.score_threshold = score_threshold
        self.agent = self._create_agent()
        self.task = self.create_task()
    
    def _create_agent(self):
        return Agent(
            role="Job Search Specialist",
            goal="To execute structured search queries, retrieve job posting URLs, filter and score them precisely, then output a single JSON with all results.",
            backstory="You are an expert job search specialist who knows how to effectively search for job opportunities across different platforms, filter out irrelevant pages, score relevance, and format results as JSON.",
            llm=self.llm,
            verbose=True,
            tools=self.search_tool
        )
    
    def create_task(self, output_dir="./results/"):
        description = f"""
                        You have the following context objects available:
                        - search_queries: List of search query strings to run (with or without site: operator).
                        - job_titles, required_skills, locations, remote_preference from the previous task.

                        Instruction:
                        1. For each string in `search_queries`, call the `tavily_search_engine_tool` exactly once to execute it.
                           - Use the search_queries directly from input if available, otherwise use the ones from the previous task.
                        2. From the tool output, extract raw results; for each result:
                        - Determine `platform` based on URL domain.
                        - Visit or use the provided `content` snippet to verify presence of required skills and location.
                        - Score each result (0-10) according to:
                            * Title match (3)
                            * Required skills presence (3)
                            * Location/remote alignment (2)
                            * Platform credibility (2)
                        - Only include results with `score` >= {self.score_threshold}.
                        - Populate `relevance_notes` explaining the score.
                        3. Collect all valid `SingleJobSearchResult` items into a list.
                        4. After processing *all* queries, output exactly one pure JSON object matching `AllJobSearchResults` schema:
                        {{"results": [ ... ]}}
                        5. Do NOT output any additional text, markdown, Thought/Action logs, or make any further tool calls after emitting the JSON.
                        """
        self.task = Task(
            description=description,
            expected_output="A pure JSON object matching AllJobSearchResults.",
            output_json=AllJobSearchResults,
            output_file=os.path.join(output_dir, "step_2_job_search_results.json"),
            agent=self.agent,
        )
        return self.task
    
    def search_jobs(self, output_dir="./results/"):
        return self.create_task(output_dir)

