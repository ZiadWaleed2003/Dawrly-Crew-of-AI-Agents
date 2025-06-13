from crewai import Crew
from job_requirement_analyst import JobRequirementAnalyst  


job_analyst_agent = JobRequirementAnalyst(
    max_queries=8,
)

# 2. Create a Crew
crew = Crew(
    agents=[job_analyst_agent.agent],  # Access the underlying Agent object
    tasks=[job_analyst_agent.create_task()],
    verbose=1
)

# 3. Kick off the process
results = crew.kickoff(
    inputs={
        "user_input" : """I want a .net and C# developer role in Egypt you
                        can use Indeed or Linkedin my experience is 0 years so you must look for fresh rules or juniors!"""
    }
)
