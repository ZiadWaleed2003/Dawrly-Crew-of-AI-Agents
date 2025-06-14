from crewai import Crew
from job_requirement_analyst import JobRequirementAnalyst  


job_analyst_agent = JobRequirementAnalyst(
    max_queries=8,
)

# 2. Create a Crew
crew = Crew(
    agents=[job_analyst_agent.agent],
    tasks=[job_analyst_agent.create_task()],
    verbose=1
)

# 3. Kick off the process
results = crew.kickoff(
    inputs={
        "user_input" : "ML or AI internship based in egypt or remote"
    }
)
