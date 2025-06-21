from crewai import Crew, Process

from app.agents.job_requirement_analyst import JobRequirementAnalyst
from app.agents.search_agent import SearchAgent



job_analyst_agent_instance = JobRequirementAnalyst()
search_agent_instance = SearchAgent(score_threshold=4.0)

# 1. Define the task for the JobRequirementAnalyst

user_input_data = {
    'role': 'Machine Learning Intern',
    'years_experience': '0-1',
    'preferred_stack': 'Python, LLM, AWS',
    'locations': ['Egypt', 'Remote'],
    'remote_preference': 'any',
    'specified_websites': ['indeed.com', 'linkedin.com']
}

job_analyst_task = job_analyst_agent_instance.create_task()

# 2. Define the task for the SearchAgent
# Now relying on implicit context passing. The SearchAgent's create_task no longer takes job_requirements_output as an explicit argument.
search_jobs_task = search_agent_instance.create_task()

# Instantiate the crew
crew = Crew(
    agents=[
        job_analyst_agent_instance.agent, # Access the agent attribute from the instance
        search_agent_instance.agent      # Access the agent attribute from the instance
    ],
    tasks=[
        job_analyst_task,
        search_jobs_task
    ],
    process=Process.sequential, # Ensures tasks run in order and output is passed implicitly
    verbose=1,
)

# Kickoff the crew
results = crew.kickoff(inputs={
    'user_input': user_input_data # Pass the initial user input to the crew
})
