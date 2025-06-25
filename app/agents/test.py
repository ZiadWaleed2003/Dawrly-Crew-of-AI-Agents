from crewai import Crew, Process

from app.agents.job_requirement_analyst import JobRequirementAnalyst
from app.agents.search_agent import SearchAgent
from app.agents.job_scrutinizer_agent import JobScrutinizerAgent 
from app.agents.report_generator_agent import ReportGenerator



job_analyst_agent_instance = JobRequirementAnalyst()
search_agent_instance = SearchAgent(score_threshold=0)  # Lower threshold to capture more results
job_scrutinizer_agent = JobScrutinizerAgent()
report_generator      = ReportGenerator()

# 1. Define the task for the JobRequirementAnalyst

user_input_data = {
    'role': 'Machine Learning Intern',
    'years_experience': '0-1',
    'locations': ['Egypt', 'Remote'],
    'remote_preference': 'any'
}

# # Define custom search queries that are less restrictive
# custom_search_queries = [
#     "Machine Learning Intern Remote",
#     "ML Intern Egypt",
#     "Entry Level Machine Learning Jobs Remote",
#     "Junior AI Developer Egypt"
# ]



crew = Crew(
    agents=[
        job_analyst_agent_instance.agent,
        search_agent_instance.agent,
        job_scrutinizer_agent.agent,
        report_generator.agent     
    ],
    tasks=[
        job_analyst_agent_instance.task,
        search_agent_instance.task,
        job_scrutinizer_agent.task,
        report_generator.task
    ],
    process=Process.sequential,
    verbose=True,
)

# Kickoff the crew
results = crew.kickoff(inputs={
    'user_input': user_input_data, # Pass custom search queries directly
})
