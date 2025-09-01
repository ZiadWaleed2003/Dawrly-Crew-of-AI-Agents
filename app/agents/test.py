from crewai import Crew, Process

from app.agents.job_requirement_analyst import JobRequirementAnalyst
from app.agents.search_agent import SearchAgent
from app.agents.job_scrutinizer_agent import JobScrutinizerAgent 
from app.agents.report_generator_agent import ReportGenerator



user_input_data = {
    'job_title': 'NlP engineer',
    'preferred_skills' : ['NLP' , 'LLM' , "python"],
    'experience_level' : "fresh",
    'min_years_experience' : '0',
    'locations': ['Egypt','remote']
}

job_analyst_agent_instance = JobRequirementAnalyst(input= user_input_data)
search_agent_instance = SearchAgent(score_threshold=0)
job_scrutinizer_agent = JobScrutinizerAgent(input=user_input_data)
report_generator      = ReportGenerator()




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
    "user_input" : user_input_data
})

