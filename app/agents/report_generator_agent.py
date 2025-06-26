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
              "The task is to generate a professional HTML page for the job report that is EMAIL-READY with inline CSS styling.",
                "Do NOT use any js or external CSS  frameworks. Instead, use inline CSS styles directly in HTML elements.",
                "All styling must be applied using inline 'style' attributes on each HTML element to ensure email client compatibility.",
                "Use these inline CSS patterns for consistent styling:",
                "- Body background: style='background-color: #f9fafb; font-family: Arial, sans-serif; margin: 0; padding: 0;'",
                "- Headers: style='background-color: #ffffff; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);'",
                "- Main container: style='max-width: 1200px; margin: 0 auto; padding: 1rem;'",
                "- Section titles: style='font-size: 1.5rem; font-weight: 600; color: #374151; margin-bottom: 1rem;'",
                "- Tables: style='width: 100%; background-color: #ffffff; border-collapse: collapse; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);'",
                "- Table headers: style='background-color: #f3f4f6; padding: 0.75rem 1rem; text-align: left; font-size: 0.875rem; font-weight: 600; color: #4b5563;'",
                "- Table cells: style='padding: 0.75rem 1rem; font-size: 0.875rem; color: #374151; border-bottom: 1px solid #e5e7eb;'",
                "- Links: style='color: #3b82f6; text-decoration: underline;'",
                "- Cards/sections: style='background-color: #ffffff; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1); margin-bottom: 3rem;'",
                "The report should be structured with the following sections:",
                "1. Include all the found jobs from the previous agent results in a well formatted table",
                "2. Job Requirements Analysis: Details from the job requirements analysis phase.",
                "3. Job Search Results: Comprehensive list of job opportunities found from the previous agent results",
                "4. Order the jobs descendingly in the table based on the agent_recommendation_rank",
                "5. Include a simple <style> block in the <head> with basic email-safe CSS for table borders and list formatting",
                "IMPORTANT: Do NOT output any additional intros, explanation, text, markdown, ```html , or logs just output pure HTML code response with inline CSS styling."
            ]),
            expected_output="A professional HTML page for the job report.",
            output_file=os.path.join(output_dir, "final_result.html"),
            agent=self.agent
        )
