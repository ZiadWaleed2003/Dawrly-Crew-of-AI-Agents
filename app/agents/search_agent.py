from datetime import datetime
import json
from crewai import Task, Agent
from pydantic import BaseModel, Field
from typing import List
import os

from app.clients import get_llm_search
from app.tools.search_tools import tavily_search_engine_tool


class SingleJobSearchResult(BaseModel):
    title: str
    url: str = Field(..., title="the job posting page url") 
    score: float
    search_query: str
    platform: str = Field(..., description="LinkedIn/Indeed/Wuzzuf/RemoteOK/Glassdoor/Other")
    relevance_notes: str = Field(..., description="Why this result matches the criteria")

class AllJobSearchResults(BaseModel):
    results: List[SingleJobSearchResult]

class SearchAgent:
    def __init__(self, score_threshold=0):
        self.llm = get_llm_search()
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


        description = "".join([
                    "You have the following context objects available:\n",
                    "- search_queries: List of search query strings to run (with or without site: operator).\n",
                    "- job_titles, required_skills, locations, remote_preference from the previous task.\n\n",
                    "Instruction:\n",
                    "1. For each string in `search_queries`, call the `tavily_search_engine_tool` exactly once to execute it.\n",
                    "   - Use the search_queries directly from input if available, otherwise use the ones from the previous task.\n",
                    "2. From the tool output, extract raw results; for each result:\n",
                    "- Determine `platform` based on URL domain.\n",
                    "- Visit or use the provided `content` snippet to verify presence of required skills and location.\n",
                    "- Score each result (0-10) according to:\n",
                    "    * Title match (3)\n",
                    "    * Required skills presence (3)\n",
                    "    * Location/remote alignment (2)\n",
                    "    * Platform credibility (2)\n",
                    "- Only include results with `score` >= ", str(self.score_threshold), ".\n",
                    "- Populate `relevance_notes` explaining the score.\n",
                    f"3. Collect all valid ```json{SingleJobSearchResult.model_json_schema()} items into a list.\n",
                    f"4. After processing *all* queries, output exactly one pure JSON object matching this `{AllJobSearchResults.model_json_schema()}` schema:\n",
                    "{\"results\": [ ... ]}\n",
                    "5. Do NOT output any additional text, markdown, Thought/Action logs, or make any further tool calls after emitting the JSON.\n",
                    "Use the previous agent search_queries to get the URLs",
                    f"- Consider relevancy within the last 3 months (current date: ", datetime.today().strftime('%Y-%m-%d'), ")."
                ])
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