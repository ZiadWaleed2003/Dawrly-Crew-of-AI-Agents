import json
import logging
import os
from typing import Optional, TypedDict , List
from langgraph.graph import StateGraph , START

from app.clients import get_LangGraph_model
from app.tools.scraping_tool import web_scraping_firecrawl
from app.models import ExtractedJob , SingleJobData , AllExtractedData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Graph State
class GraphState(TypedDict):

    urls : List[str]
    scraped_urls : List[str]
    user_req : dict
    current_job : Optional[SingleJobData]



class JobScrutinizerLangGraph():


    def __init__(self , user_id , user_input):
        
        self.user_id = user_id
        self.user_input = user_input
        self.model = get_LangGraph_model()
        self.scraping_tool = web_scraping_firecrawl()
        self.saved_jobs = []
        self.state = GraphState()

    # Start

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

    def scraping_node(self):
        " a node used for scraping the URLs provided by the prev agent"


    # Conditional node for scraping
    def post_scraping_conditional_node(self):
        "a conditional node to check the scraped results"
        

    # filtering node
    def filtering_node(self):

        try:
            if self.state.get("current_job") is not None:
                curr_job = self.state.get("current_job")
                filtering = ExtractedJob(**curr_job)

        except Exception as e:
            self.state['current_job'] = None
            logger.exception(f"Failed to filter the scraped results in the filtering node : {e}")






    # validation node

    def validation_node(self):
        "a node to validate the scraped results if it was successful and follows the user reqs or not"



    # Conditional Node for the user reqs

    def post_validation_conditional_node(self):
        "a node to check if the the schema is valid or not and then decide based on it"

    


    # Skip URL node

    # LLM analysis node

    # schema conversion node

    # Collect Valid Jobs

    def collect_valid_jobs(self , job):
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
            # Create the final structure that matches AllExtractedData schema
            # jobs_list already contains dictionaries from job_data.model_dump()
            final_result = {
                "jobs": jobs_list
            }
            
            # Save to file
            with open(output_file, 'w') as f:
                json.dump(final_result, f, indent=2)
            
            # Validate the saved data by creating AllExtractedData instance
            validated_data = AllExtractedData(**final_result)
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


    # End
    def scrutinize_jobs(self):
        # read URls 
        # loop over these urls and then enter it in the flow 
        # always check if this URL is exist in the GraphState[scraped_urls] before doing it cause u can skip it