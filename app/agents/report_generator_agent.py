from crewai import Agent , Task
import os

from app.clients import get_llm_sec


class ReportGenerator:

    def __init__(self):
        
        self.llm   = get_llm_sec()
        self.agent = self._create_agent()
        self.task  = self._create_task()


    def _create_agent(self):

        return Agent(
            role="Jobs Report Author Agent",
            goal="To generate a professional HTML page for the Jobs report",
            backstory="The agent is designed to assist in generating a professional HTML page for the Job report after looking into a list of Jobs.",
            llm= self.llm,
            verbose=True,
        )


    def _create_task(self , output_dir = "./results/"):
        
        return Task(
            description="\n".join([
                "The task is to generate a professional HTML page for the job report.",
                "You have to use Tailwind CSS framework for a better UI use internal CDN no external CSS or JS files or code needed",
                "The report will include the search results and analysis of job listings from the previous agent results (the job scruntinizer)",
                "The report should be structured with the following sections:",
                "1. Include all the found jobs from the previous agent results in a well formatted table"
                "2. Job Requirements Analysis: Details from the job requirements analysis phase. ",
                "3. Job Search Results: Comprehensive list of job opportunities found from the previous agent results",
                "4. Order the jobs descendingly in the table based on the agent_recommendation_rank"
                "IMPORTANT : Do NOT output any additional intros , explanation , text, markdown, or logs just output pure Code response."
            ]),
            expected_output="A professional HTML page for the job report.",
            output_file=os.path.join(output_dir, "final_result.html"),
            agent=self.agent
        )
