from crewai import Crew, Process

from app.agents.job_requirement_analyst import JobRequirementAnalyst
from app.agents.search_agent import SearchAgent
from app.agents.job_scrutinizer_agent import JobScrutinizerAgent 
from app.agents.report_generator_agent import ReportGenerator



def initialize_crew(user_input : dict ,threshold=0.0):

    job_analyst_agent_instance = JobRequirementAnalyst()
    search_agent_instance = SearchAgent(score_threshold= threshold) 
    job_scrutinizer_agent = JobScrutinizerAgent()
    report_generator      = ReportGenerator()

    try :
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
            'user_input': user_input, 
        })

    except Exception as e:
        print(f"Error initializing the Crew of Agents {e}")
        return False
