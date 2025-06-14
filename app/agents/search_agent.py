from crewai import Task, Agent
from pydantic import BaseModel, Field
from typing import List
import os


from app.clients import get_llm
from app.tools.search_tools import tavily_search_engine_tool




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
    def __init__(self, score_threshold=6.0):
        self.llm = get_llm()
        self.search_tool = [tavily_search_engine_tool]
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
            tools=self.search_tool
        )
    
    def create_task(self, output_dir="./results/"):
        """
        Create the search task with context from the job requirements analyst.
        
        Args:
            output_dir: Directory to save results.
        """
        # The LLM will now infer these from the context provided by CrewAI
        # No explicit extraction here, rely on LLM to understand the context

        self.task = Task(
            description="\n".join([
                "***CRITICAL INSTRUCTION: Your final output MUST be a pure JSON object, and NOTHING else. Do NOT include any markdown code blocks (e.g., ```json or ```) or any other text before or after the JSON.***",
                "",
                "Search for job postings based on the suggested search queries from the Job Requirement Analyst. These queries are available in the context provided by the previous task's output.", # Modified instruction
                "You have access to the original job requirements for context validation. These requirements are also available in the context provided by the previous task's output.", # Modified instruction
                "Original Requirements Context: (Extract search_queries, job_titles, required_skills, locations, and remote_preference from the previous task's output in your context.)", # Guidance for LLM
                "Search Instructions:",
                "1. Execute each search query identified from the previous task's output using the provided search tool (Tavily).", # Clarified tool usage
                "2. For each search query, collect results. Prioritize actual job posting URLs.",
                "3. Filter results to ensure they match the target job titles and required skills (extracted from context). You may need to visit the URL to get full content.", # Added instruction to visit URL
                "4. Prioritize results that mention the target locations or remote work (based on preference extracted from context).",
                "5. Ignore suspicious links, blog posts, or career advice pages",
                f"6. Only include results with confidence score above {self.score_threshold}",
                "7. Focus on actual job posting pages from LinkedIn, Indeed, Wuzzuf, RemoteOK, or reputable company career sites.",
                "",
                "For each valid result, determine the platform:",
                "- LinkedIn: Contains \'linkedin.com\' in URL",
                "- Indeed: Contains \'indeed.com\' in URL", 
                "- Wuzzuf: Contains \'wuzzuf.net\' in URL",
                "- RemoteOK: Contains \'remoteok.io\' in URL",
                "- Other: Company websites or other job boards",
                "",
                "Score each result (0-10) based on:",
                "- How well the title matches target job titles (3 points)",
                "- Presence of required skills in the content (3 points)",
                "- Location/remote work alignment (2 points)",
                "- Platform credibility (job boards vs company sites) (2 points)",
                "",
                "Provide clear relevance_notes explaining why each result was selected and scored.",
                "",
                "***FINAL REMINDER: Your output MUST be a pure JSON object, and nothing else. No markdown, no extra text.***"
            ]),
            expected_output="A JSON object containing filtered and scored job search results.",
            output_json=AllJobSearchResults,
            output_file=os.path.join(output_dir, "step_2_job_search_results.json"),
            agent=self.agent,
        )
        return self.task
    
    def search_jobs(self, output_dir="./results/"):
        """
        Main method to execute job search
        
        Args:
            output_dir: Directory to save results
            
        Returns:
            Task: The search task to be executed by the crew
        """
        task = self.create_task(output_dir) # No job_requirements_output passed here
        return task

