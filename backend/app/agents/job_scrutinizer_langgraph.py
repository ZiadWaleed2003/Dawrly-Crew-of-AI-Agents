import json
import logging
import os
from typing import Optional, TypedDict , List
from langgraph.graph import StateGraph , START , END
from langgraph.prebuilt import create_react_agent


from app.clients import get_LangGraph_model
from app.tools.scraping_tool import web_scraping_firecrawl
from app.models import ExtractedJob , SingleJobData , AllExtractedData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Graph State
class GraphState(TypedDict):

    urls : List[str]
    user_req : dict
    current_job : Optional[ExtractedJob]
    analyzed_job : Optional[SingleJobData]
    current_url : str
    

    scraping_status : bool
    filtering_status : bool
    analysis_status : bool




class JobScrutinizerLangGraph():


    def __init__(self , user_id , user_input):
        
        self.user_id = user_id
        self.user_input = user_input
        self.model = get_LangGraph_model()
        self.sys_prompt = self._sys_prompt()
        # self.agent = self._create_agent()
        self.saved_jobs = []
        self.scrapped_urls = []
        self.graph = self.build_graph()

    # Start

    def build_graph(self):

        builder = StateGraph(GraphState)

        # just building the nodes here
        builder.add_node("scraping_node",self.scraping_node)
        builder.add_node("filtering_node" , self.filtering_node)
        builder.add_node("skip_node" , self.skip_node)
        builder.add_node("llm_analysis_node",self.llm_analysis_node)
        builder.add_node("collect_valid_jobs",self.collect_valid_jobs)
        


        # linking the scraping node with the post scraping condtional node
        builder.add_conditional_edges(
            "scraping_node",
            self.post_scraping_conditional_node,
            {
                "scraping_succedded" : "filtering_node",
                "skip_url" : "skip_node"
            }
        )

        # another one my G
        builder.add_conditional_edges(
            "filtering_node",
            self.post_filtering_conditional_node,
            {
                "filtering_succedded" : "llm_analysis_node",
                "skip_url" : "skip_node"
            }
        )

        # anotherrrrr onneee
        builder.add_conditional_edges(
            "llm_analysis_node",
            self.post_llm_analysis_conditional_node,
            {
                "llm_analysis_succedded" : "collect_valid_jobs",
                "skip_url" : "skip_node"
            }
        )

        # Edges
        builder.add_edge(START , "scraping_node")
        builder.add_edge("collect_valid_jobs",END)
        builder.add_edge("skip_node",END)
        
        return builder.compile()
  


    def _sys_prompt(self):

        sys_prompt = "".join([
                        "You are an expert Job Scrutinizer with deep knowledge of job markets and technical roles.\n\n",
                        
                        "## YOUR ROLE\n",
                        "- You receive job data in the ExtractedJob schema.\n",
                        "- You must evaluate whether it matches the user's requirements.\n\n",
                        
                        "## INPUT FORMAT\n",
                        "You will receive data in this schema:\n",
                        "- job_title: string\n",
                        "- job_description: string\n",
                        "- job_url: string\n",
                        "- posting_date: string\n",
                        "- required_years_of_experience: string\n\n",
                        
                        "## RULES\n",
                        "- If the provided data is literally the string 'none', you must return a valid SingleJobData object with matches_user_req=false.\n",
                        "- If the job data does not meet user requirements, set matches_user_req=false.\n",
                        "- If it meets user requirements, set matches_user_req=true.\n",
                        "- Always use the job_url from the provided ExtractedJob.\n",
                        "- If job_title or description is missing or invalid, treat it as not matching user requirements.\n\n",
                        
                        "## ANALYSIS CRITERIA\n",
                        f"- Compare job description, posting date, required experience, and technologies against user requirements: {self.user_input}\n",
                        "- If job is older than 3 months, it does not match.\n",
                        "- If required years of experience exceed user background, it does not match.\n",
                        "- If technology/domain does not align, it does not match.\n\n",
                        
                        "## OUTPUT FORMAT\n",
                        "- You must return a valid JSON object following this schema:\n",
                        "  {\n",
                        "    'matches_user_req': bool,\n",
                        "    'job_title': str,\n",
                        "    'job_description': str,\n",
                        "    'job_url': str,\n",
                        "    'agent_recommendation_rank': int (1–5),\n",
                        "    'agent_recommendation_notes': list of strings\n",
                        "  }\n\n",
                        "- Do not output a list. Return only a single JSON object.\n",
                        "- Do not include markdown, code blocks, or extra text.\n\n",
                        
                        "## RANKING GUIDELINES\n",
                        "- 5: Excellent match, strong alignment\n",
                        "- 4: Very good, minor gaps\n",
                        "- 3: Good, some gaps\n",
                        "- 2: Fair, significant gaps\n",
                        "- 1: Poor, major mismatch\n\n",
                        
                        "## CRITICAL NOTES\n",
                        "- If input == 'none', output must still follow SingleJobData with matches_user_req=false.\n",
                        "- Double-check JSON validity before responding.\n",
                        "- Never include commentary or explanations outside the JSON object.\n"
                    ])
        
        return sys_prompt

    # def _create_agent(self):
    #     # Create the agent with system prompt
    #     agent = create_react_agent(
    #         model=self.model,
    #         prompt=self._sys_prompt(),
    #         response_format=SingleJobData
    #     )
        
    #     return agent




    # get_urls node
    def get_urls(self):

        """
        Read job URLs from step 2 results JSON file
        
        Returns:
            List[str]: List of job URLs extracted from step 2 results
        """
        step2_file = os.path.join(f"./results/{self.user_id}/", "step_2_job_search_results.json")
        
        try:
            with open(step2_file, 'r') as f:
                step2_data = json.load(f)
            
            # Extract URLs from the step 2 results
            # Assuming the structure has job URLs in the data
            urls = []
            if isinstance(step2_data, dict):
                
                if 'results' in step2_data:
                    for result in step2_data['results']:
                        if 'url' in result:
                            urls.append(result['url'])
                        elif 'link' in result:
                            urls.append(result['link'])
            
            return urls
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Step 2 results file not found: {step2_file}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in step 2 results file: {step2_file}")

    # scraping node

    def scraping_node(self , state : GraphState):
        " a node used for scraping the URLs provided by the prev agent"
        url = state.get("current_url")
        if not url:
            logger.info("Couldn't find the URL Scraping failed.")
            return {"scraping_status" : False}

    
        result = web_scraping_firecrawl(tool_input=url)
        # to avoid duplicates
        if result.get("job_url") in self.scrapped_urls:
            logger.info("skipping a duplicate URL")
            return {"scraping_status" : False}
        
        
        if result:
            logger.info("Scraping successful.")
            self.scrapped_urls.append(result.get("job_url"))
            return {"current_job": result, "scraping_status": True}
        else:
            logger.info("Scraping failed.")
            return {"scraping_status" : False}
        
        


    # Conditional node for scraping
    def post_scraping_conditional_node(self , state : GraphState):
        "a conditional node to check the scraped results"
        logger.info("--- Entering the Post scraping conditional node ---")
        if state.get('scraping_status'):
            return "scraping_succedded"
        else:
            return "skip_url"
        
    def skip_node(self, state: GraphState):
        """This node does nothing and just allows the graph to terminate."""
        logger.info("--- Skipping URL ---")
        return {}
        

    # filtering node
    def filtering_node(self , state : GraphState):

        logger.info("--- Entering the filtering Node ---")

        try:
            if state.get("current_job") is not None:
                curr_job = state.get("current_job")
                filtering = ExtractedJob(**curr_job)
                return {'filtering_status' : True}
                

        except Exception as e:
            logger.exception(f"Failed to filter the scraped results in the filtering node : {e}")
            return {
                'filtering_status' : False
            }


    def post_filtering_conditional_node(self, state : GraphState):
        "a conditional node to check the filtered results"
        logger.info("--- Entering the Post filtering conditional node ---")
        if state.get('filtering_status'):
            return "filtering_succedded"
        else:
            return "skip_url"
        

    def llm_analysis_node(self , state : GraphState):
        "a node to get the analysis of the LLM"
        
        logger.info("--- Entering the LLM Analysis Node ---")
        
        try:
            current_job = state.get("current_job")
            if not current_job:
                logger.error("No current job data available for analysis")
                return {"analysis_status": False}
            
            # Prepare the job data for analysis
            job_data_str = json.dumps(current_job, indent=2)
            
            # Create the prompt for analysis
            prompt = f"""
            {self.sys_prompt}
            
            Job Data to Analyze:
            {job_data_str}
            """
            
            # Use the ChatNVIDIA model
            response = self.model.invoke(prompt)
            
            # Extract the content from the response
            if hasattr(response, 'content'):
                analysis_result = response.content
            else:
                analysis_result = str(response)
            
            logger.info(f"LLM Analysis completed: {analysis_result[:100]}...")
            
            # Try to parse the JSON response
            try:
                analyzed_job = json.loads(analysis_result)
                if analyzed_job['matches_user_req']:

                    logger.info(f"extracted job :{analyzed_job}")
                    return {
                        "analyzed_job": analyzed_job,
                        "analysis_status": True
                    }
                else:
                    logger.error("The Job was invalid as per the LLM analysis")
                    return {
                        "analyzed_job" : None,
                        "analysis_status" : False
                    }
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response as JSON: {e}")
                logger.error(f"Raw response: {analysis_result}")
                return {"analysis_status": False}
                
        except Exception as e:
            logger.exception(f"Failed in LLM analysis node: {e}")
            return {"analysis_status": False}

    # Conditional Node for the user reqs

    def post_llm_analysis_conditional_node(self , state : GraphState):
        "a node to check if the the schema is valid or not and then decide based on it"
        if state.get("analysis_status"):
            return "llm_analysis_succedded"
        else :
            return "skip_url"
    

    # Collect Valid Jobs

    def collect_valid_jobs(self , state : GraphState):
        job = state.get("analyzed_job")
        return self.saved_jobs.append(job)

    # Save results

    def _save_results(self, jobs_list):
        """
        Save the list of job results to a JSON file
        
        Args:
            jobs_list: List of job dictionaries to save
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        output_dir = f"./results/{self.user_id}/"
        os.makedirs(output_dir, exist_ok=True)

        output_file = os.path.join(output_dir, "step_3_job_scrutinizer_results.json")

        try:
            
            final_result = {
                "jobs": jobs_list
            }
            
            # Save to file
            with open(output_file, 'w') as f:
                json.dump(final_result, f, indent=2)
            
            # # Validate the saved data by creating AllExtractedData instance
            # validated_data = AllExtractedData(**final_result)
            print(f"Successfully saved {len(jobs_list)} jobs to {output_file}")
            return True
            
        except Exception as e:
            print(f"Error saving results: {str(e)}")
            # Save raw data for debugging
            debug_file = output_file.replace('.json', '_debug.json')
            try:
                with open(debug_file, 'w') as f:
                    json.dump({"error": str(e), "jobs_list": jobs_list}, f, indent=2)
                print(f"Debug data saved to {debug_file}")
            except Exception as debug_e:
                print(f"Could not save debug file: {debug_e}")
            return False


    
    def scrutinize_jobs(self):
        

        job_urls = self.get_urls()
        # loop over these urls and then enter it in the flow
        if job_urls:

            for url in job_urls:

                logger.info(f"Processing URL : {url}")

                initial_state = {"current_url": url}
                final_state = self.graph.invoke(initial_state)

        if len(self.saved_jobs) > 0:
            logger.info("saving jobs")
            self._save_results(self.saved_jobs)
            return True

        return False
