from crewai import Crew, Process
import logging


from app.agents.job_requirement_analyst import JobRequirementAnalyst
from app.agents.search_agent import SearchAgent
from app.agents.job_scrutinizer_agent import JobScrutinizerAgent 
from app.agents.evaluator import EvaluatorAgent
from app.agents.report_generator_agent import json_to_html_table
from app.tools.mail_sender import send_email


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def initialize_crew(user_input_data : dict):

    logger.info("Initializing crew with user input data")
    email = user_input_data['email_address']
    user_input_data.pop('email_address')
    logger.info(f"Processing request for email: {email}")



    job_analyst_agent_instance = JobRequirementAnalyst(input= user_input_data)
    search_agent_instance = SearchAgent()
    job_scrutinizer_agent = JobScrutinizerAgent(input=user_input_data)
    evaluator_agent = EvaluatorAgent()

    logger.info("All agents initialized successfully")

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

    logger.info("Crew configured and ready to start")

    try:
        # Kickoff the crew
        logger.info("Starting crew execution")
        results = crew.kickoff(inputs={
            "user_input" : user_input_data
        })

        logger.info("Crew execution completed")
        if results.raw:
            logger.info("Generating HTML report from results")
            res = json_to_html_table()

            if res:
                logger.info("HTML report generated successfully, sending email")
                send_email(to_email=email)
                logger.info(f"Email sent successfully to {email}")
            else:
                logging.error("Failed to generate the email bruhh")
                raise Exception

        else:
            logging.error("Crew execution failed - no results returned")
            raise Exception

    except Exception as e:

        logging.error(f"The crew Failed miserably bruhhhh : {e}")
        logger.info(f"Sending error notification email to {email}")
        send_email(to_email=email , html_file_path="./backend/error_template/error_email_template.html")

