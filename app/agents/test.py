from crewai import Crew, Process

from app.agents.job_requirement_analyst import JobRequirementAnalyst
from app.agents.search_agent import SearchAgent
from app.agents.job_scrutinizer_agent import JobScrutinizerAgent 
from app.agents.evaluator import EvaluatorAgent
from app.agents.report_generator_agent import json_to_html_table
from app.tools.mail_sender import send_email

user_input_data = {
    'job_title': 'Junior Software Engineer',
    'preferred_skills' : ["Nodejs" , "js"],
    'years_experience': '0',
    'locations': ['Egypt'],
    'remote_preference' : "any"
}

job_analyst_agent_instance = JobRequirementAnalyst(input= user_input_data)
search_agent_instance = SearchAgent(score_threshold=0)
job_scrutinizer_agent = JobScrutinizerAgent(input=user_input_data)
evaluator_agent = EvaluatorAgent()





crew = Crew(
            agents=[
                job_analyst_agent_instance.agent,
                search_agent_instance.agent,
                job_scrutinizer_agent.agent,
                evaluator_agent.agent
            ],
            tasks=[
                job_analyst_agent_instance.task,
                search_agent_instance.task,
                job_scrutinizer_agent.task,
                evaluator_agent.task
            ],
            process=Process.sequential,
            verbose=True,
            cache=False
        )

# Kickoff the crew
results , success = crew.kickoff(inputs={
    "user_input" : user_input_data
})


if results.raw:

    res = json_to_html_table()

    if res:

        send_email(to_email="sohilaibrahim555@gmail.com")

else:

    print("error happened couln't make the HTML file")

