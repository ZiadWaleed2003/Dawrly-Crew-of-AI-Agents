from crewai import Crew
from job_requirement_analyst import JobRequirementAnalyst  # Import your classes


job_analyst_agent = JobRequirementAnalyst(
    max_queries=8,
    search_mode="general"  # or "general"
)

# 2. Create a Crew
crew = Crew(
    agents=[job_analyst_agent.agent],  # Access the underlying Agent object
    tasks=[job_analyst_agent.create_task(
        user_input="I want a senior Python developer role in Berlin or remote",
    )],
    verbose=1
)

# 3. Kick off the process
results = crew.kickoff()

# 4. Process the results (example)
print("Universal Query:", results.universal_query)
if results.platform_queries:
    print("\nPlatform-Specific Queries:")
    for platform, queries in results.platform_queries.items():
        print(f"{platform}:")
        for query in queries:
            print(f" - {query}")