from crewai import Crew, Process

from app.agents.job_requirement_analyst import JobRequirementAnalyst
from app.agents.search_agent import SearchAgent
from app.agents.job_scrutinizer_agent import JobScrutinizerAgent 



job_analyst_agent_instance = JobRequirementAnalyst()
search_agent_instance = SearchAgent(score_threshold=4.0)
job_scrutinizer_agent = JobScrutinizerAgent()

# 1. Define the task for the JobRequirementAnalyst

user_input_data = {
    'role': 'Machine Learning Intern',
    'years_experience': '0-1',
    'preferred_stack': 'Python, LLM, AWS',
    'locations': ['Egypt', 'Remote'],
    'remote_preference': 'any',
    'specified_websites': ['indeed.com', 'linkedin.com']
}




# Instantiate the crew
crew = Crew(
    agents=[
        job_analyst_agent_instance.agent,
        search_agent_instance.agent,
        job_scrutinizer_agent.agent      
    ],
    tasks=[
        job_analyst_agent_instance.task,
        search_agent_instance.task,
        job_scrutinizer_agent.task
    ],
    process=Process.sequential,
    verbose=True,
)

# Kickoff the crew
results = crew.kickoff(inputs={
    'user_input': user_input_data
})
