import os
import uuid
from crewai import Crew, Process
import logging
from pathlib import Path

from app.agents.job_requirement_analyst import JobRequirementAnalyst
from app.agents.search_agent import SearchAgent
from app.agents.job_scrutinizer_agent import JobScrutinizerLangGraph
from app.agents.report_generator_agent import json_to_html_table
from app.tools.mail_sender import send_email


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent



async def initialize_crew(user_input_data : dict):

    logger.info("Initializing crew with user input data")
    email = user_input_data['email_address']
    user_input_data.pop('email_address')
    logger.info(f"Processing request for email: {email}")

    id = str(uuid.uuid4()) + f"_{email}"


    job_analyst_agent_instance = JobRequirementAnalyst(input= user_input_data , user_id= id)
    search_agent_instance = SearchAgent(user_id= id)
    job_scrutinizer_agent   = JobScrutinizerLangGraph(user_id=id , user_input= user_input_data)

    logger.info("All agents initialized successfully")

    
    logs_dir = BASE_DIR / "logs"
    logs_dir.mkdir(exist_ok=True)
    logs = str(logs_dir / f"{email}.txt")

    crew = Crew(
                agents=[
                    job_analyst_agent_instance.agent,
                    search_agent_instance.agent,
                ],
                tasks=[
                    job_analyst_agent_instance.task,
                    search_agent_instance.task,
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
        results = await crew.kickoff_async(inputs={
            "user_input" : user_input_data
        })

        if results.raw:

            agent_3_result = await job_scrutinizer_agent.scrutinize_jobs()

        logger.info("Crew execution completed")

        if agent_3_result:
            logger.info("Generating HTML report from results")
            res = json_to_html_table(user_id= id)

            if res:
                logger.info("HTML report generated successfully, sending email")
                send_email(to_email=email , user_id=id , error=False)
                logger.info(f"Email sent successfully to {email}")
            else:
                logging.error("Failed to generate the email bruhh")  
                raise Exception

        else:
            logging.error("Crew execution failed - no results returned")
            raise Exception

    except Exception as e:

        logging.error(f"The crew Failed miserably bruhhhh : {e}")
        

        # If we never found jobs or the process crashed before completion,
        # or we had partial jobs but the workflow failed — send general error.
        if not job_scrutinizer_agent.final_status :
            logger.info(f"Sending general error notification email to {email}")
            send_email(to_email=email, user_id=id, error=True)
            logger.info(f"General Error Email sent successfully to {email}")
            return False

        # If the list exists but is empty (workflow finished, no jobs found)
        logger.info(f"Sending 0-jobs email to {email}")
        send_email(to_email=email, user_id=id, error=True, jobs=0)
        logger.info(f"0 Jobs Email sent successfully to {email}")
        return False
           