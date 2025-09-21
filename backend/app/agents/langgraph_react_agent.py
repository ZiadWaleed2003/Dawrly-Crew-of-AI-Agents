from langgraph.prebuilt import create_react_agent
from datetime import datetime
import json
import os

from app.clients import get_LangGraph_model
from app.tools.scraping_tool import web_scraping_firecrawl
from app.models import AllExtractedData, SingleJobData, ExtractedJob


class JobScrutinizerLangGraphAgent:

    def __init__(self, user_id ,user_input=None):
        self.llm = get_LangGraph_model()
        self.tools = [web_scraping_firecrawl]
        self.user_id = user_id
        self.user_requirements : dict = user_input
        self.agent = self._create_agent()
        self.job_urls = None

    def _create_agent(self):
        # Create the agent with system prompt
        agent = create_react_agent(
            model=self.llm,
            tools=self.tools,
            prompt=self._system_prompt(),
            response_format=SingleJobData
        )
        
        return agent
    

    def _system_prompt(self):
        current_date = datetime.today().strftime('%Y-%m-%d')
        
        sys_prompt = "".join([
            "You are an expert Job Scrutinizer with deep knowledge of various industries and job roles. ",
            "Your mission is to analyze job listings from URLs, extract detailed information, and evaluate their suitability for job seekers.\n\n",
            
            "## YOUR ROLE AND EXPERTISE\n",
            "- You are a seasoned professional with comprehensive understanding of job markets across different industries\n",
            "- You excel at identifying key job requirements, technologies, and organizational fit factors\n",
            "- You provide honest, insightful evaluations that help job seekers make informed decisions\n\n",
            
            "## TASK WORKFLOW\n",
            "You will be given a SINGLE job URL to analyze:\n",
            "1. Use the web_scraping_firecrawl tool to extract job information from the provided URL\n",
            "2. The tool will return a JSON object following the ExtractedJob schema containing:\n",
            "   - job_title: The official position title\n",
            "   - job_description: Complete job description and requirements\n",
            "   - job_url: The canonical/final URL (use THIS URL, not your input URL)\n",
            "   - posting_date: When the job was posted\n",
            "   - required_years_of_experience: Experience requirements mentioned\n",
            "3. Analyze the returned data to judge if the job matches user preferences\n",
            f"4. If the job matches the user requirements : {self.user_requirements}, transform it into {SingleJobData.model_json_schema()} format for your response\n",
            "5. If scraping fails or job doesn't match criteria, return null or indicate no match\n\n",
            
            "## ANALYSIS REQUIREMENTS\n",
            "For each JSON object returned by the web scraping tool:\n",
            "- **Analyze Job Description**: Review requirements, technologies, responsibilities against user preferences\n",
            "- **Check Posting Date**: Ensure the job was posted within the last 3 months\n",
            "- **Evaluate Experience Level**: Match required experience with user's background\n",
            "- **Technology Stack Assessment**: Verify alignment with user's desired tech stack\n",
            "- **Domain Relevance**: Ensure the role fits the user's target domain/industry\n\n",
            
            "## OUTPUT REQUIREMENTS\n",
            "Based on your analysis of the ExtractedJob data returned by the tool:\n",
            "- **ONLY return the job if it matches user preferences and criteria**\n",
            "- **Use the job_url field from the tool's response** (not your input URL)\n",
            "- **Transform the data to match SingleJobData schema**:\n",
            "  - job_title: From tool response\n",
            "  - job_description: From tool response\n",
            "  - job_url: FROM TOOL RESPONSE (this is critical!)\n",
            "  - agent_recommendation_rank: Your 1-5 assessment\n",
            "  - agent_recommendation_notes: Your detailed analysis as list of strings\n",
            "- **Return a single job object, not a list**\n\n",
            
            "## CRITICAL WORKFLOW NOTES\n",
            f"- The web_scraping_firecrawl tool returns ```json{ExtractedJob.model_json_schema()} schema data\n",
            "- You must analyze this returned data to judge job suitability\n",
            f"- Only return the job if it passes your analysis in the ```json{SingleJobData.model_json_schema()} format\n",
            "- Always use the job_url from the tool response, NOT the input URL you provided to the tool\n",
            "- The tool response contains the canonical/final URL after any redirects\n",
            "- You are processing ONE URL at a time, not multiple URLs\n\n",
            
            "## FILTERING RULES\n",
            "**EXCLUDE the job if it:**\n",
            "- Uses completely different technology stacks or domains from user specifications\n",
            f"- Is older than 3 months from current date  {current_date}\n",
            "- Example: If user wants Node.js full-stack, exclude .NET or Python backend roles\n",
            "- Example: If user wants AI/ML, exclude pure frontend or system admin roles\n\n",
            
            "**INCLUDE the job if it:**\n",
            "- Has similar or related technologies even if not exact matches\n",
            "- Focuses on the same DOMAIN and CORE TECHNOLOGY STACK\n",
            "- Example: If user wants LangChain, include LangGraph, LlamaIndex, or similar frameworks\n",
            "- Example: If user wants React, include Vue or Angular positions\n\n",
            
            "## RANKING GUIDELINES\n",
            "**Rank 5 (Excellent Match)**: Perfect alignment with user requirements, great company, competitive package\n",
            "**Rank 4 (Very Good)**: Strong match with minor gaps, good growth opportunities\n",
            "**Rank 3 (Good)**: Decent match with some skill development needed\n",
            "**Rank 2 (Fair)**: Partial match, significant gaps but potential for learning\n",
            "**Rank 1 (Poor)**: Minimal alignment, major skill or domain mismatch\n\n",
            
            "## OUTPUT FORMAT\n",
            "**CRITICAL**: You must return ONLY a valid JSON object that matches the SingleJobData schema structure.\n",
            f"- The output must follow the ```json{SingleJobData.model_json_schema()} schema\n",
            "- Use job_url from the tool response (ExtractedJob.job_url), NOT your input URL\n",
            "- Only return the job if it passed your analysis and matches user criteria\n",
            "- If the job doesn't match, return false as a job_title placeholder\n",
            "- Do NOT include any text before or after the JSON\n",
            "- Do NOT use markdown formatting or code blocks\n",
            "- Do NOT include explanations, thoughts, or commentary\n",
            "- Return ONLY the raw JSON object for the single job\n",
            "- Double-check your JSON structure before responding\n\n",
            
            "## QUALITY ASSURANCE\n",
            "Before providing your final response:\n",
            "1. Verify you used job_url from tool response, NOT input URL\n",
            "2. Confirm the job passed your analysis criteria\n",
            "3. Ensure recommendation rank is justified by your notes\n",
            "4. Confirm JSON structure matches SingleJobData schema exactly\n",
            "5. Validate that the job matches user preferences\n",
            "6. Double-check that job_url field contains the URL returned by the scraping tool\n",
            "7. Return null or indicate no match if the job doesn't meet criteria\n\n",
            
            "Remember: Your analysis helps job seekers make career-defining decisions. Be thorough, honest, and constructive in your evaluations."
        ])
        
        return sys_prompt
    
    async def _read_job_urls_from_step2(self):
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
    
    async def scrutinize_jobs(self):
        """
        Execute the job scrutinization task
        
        Reads job URLs from step 2 results file and analyzes them one by one
        
        Returns:
            bool: if it managed to extract and save the results
        """
        # Read job URLs from step 2 results
        try:
            job_urls = await self._read_job_urls_from_step2()
        except (FileNotFoundError, ValueError) as e:
            raise RuntimeError(f"Failed to read job URLs from step 2: {str(e)}")
        
        if not job_urls or job_urls == 0:
            self.job_urls = 0
            return False


        jobs = []

        for url in job_urls:

            user_message = "".join([
                "Please analyze the following job URL and extract detailed information:\n",
                f"{url}\n",
                "Please scrape this URL, extract the required information, and provide your analysis following the system instructions. ",
                f"User requirements: {self.user_requirements}"
            ])
            
            # Create input for the agent
            input_data = {
                "messages": [
                    {"role": "user", "content": user_message}
                ]
            }
            
            try:
                # Execute the agent for this single URL
                result = await self.agent.ainvoke(input_data)
                
                if result and "structured_response" in result:
                    job_data  = result["structured_response"]
                    # Only add the job if it's not null and has the required fields
                    if job_data is not None:
                        jobs.append(job_data.model_dump())
                        print(f"Successfully processed job of a type: {type(job_data)}")
                    else:
                        print(f"Job from URL {url} was filtered out or invalid")
                else:
                    print(f"No valid result for URL: {url}")
                    
            except Exception as e:
                print(f"Error processing URL {url}: {str(e)}")
                continue

        # Save all collected jobs
        saving_result = await self._save_results(jobs)

        if saving_result:
            print(f"Saved step3 results with {len(jobs)} jobs")
            return True
        else:
            print("Error occurred while saving step 3 results")
            return False
    


    async def _save_results(self, jobs_list):
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







