from crewai import Crew, Process

from app.agents.job_requirement_analyst import JobRequirementAnalyst
from app.agents.search_agent import SearchAgent
from app.agents.job_scrutinizer_agent import JobScrutinizerAgent 
from app.agents.evaluator import EvaluatorAgent
from app.agents.report_generator_agent import json_to_html_table
from app.tools.mail_sender import send_email



def initialize_crew(user_input_data : dict):


    email = user_input_data['email_address']
    user_input_data.pop('email_address')



    job_analyst_agent_instance = JobRequirementAnalyst(input= user_input_data)
    search_agent_instance = SearchAgent()
    job_scrutinizer_agent = JobScrutinizerAgent(input=user_input_data)
    evaluator_agent = EvaluatorAgent()



    logs = f"./backend/logs/{email}.txt"

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
                cache=False,
                output_log_file=logs,
            )

    try:
        # Kickoff the crew
        results = crew.kickoff(inputs={
            "user_input" : user_input_data
        })

        if results.raw:
            res = json_to_html_table()

            if res:
                send_email(to_email=email)
            else:
                print("Couldn't send the email bruhh")
                raise Exception

        else:
            print("error happened couln't make the HTML file")
            raise Exception

    except Exception as e:

        print(f"The crew Failed miserably bruhhhh : {e}")
        send_email(to_email=email , html_file_path="./backend/error_template/error_email_template.html")

