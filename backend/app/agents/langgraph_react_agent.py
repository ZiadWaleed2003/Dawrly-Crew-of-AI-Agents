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
        self.user_requirements = user_input
        self.agent = self._create_agent()

    def _create_agent(self):
        # Create the agent with system prompt
        agent = create_react_agent(
            model=self.llm,
            tools=self.tools,
            state_modifier=self._system_prompt() 
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
            "For each job URL provided:\n",
            "1. Use the web_scraping_firecrawl tool to extract job information from the URL\n",
            "2. The tool will return a JSON object following the ExtractedJob schema containing:\n",
            "   - job_title: The official position title\n",
            "   - job_description: Complete job description and requirements\n",
            "   - job_url: The canonical/final URL (use THIS URL, not your input URL)\n",
            "   - posting_date: When the job was posted\n",
            "   - required_years_of_experience: Experience requirements mentioned\n",
            "3. Analyze the returned data to judge if the job matches user preferences\n",
            "4. If the job is suitable, include it in your final output using the job_url from the tool response\n",
            "5. If scraping fails or job doesn't match criteria, exclude it from final results\n\n",
            
            "## ANALYSIS REQUIREMENTS\n",
            "For each JSON object returned by the web scraping tool:\n",
            "- **Analyze Job Description**: Review requirements, technologies, responsibilities against user preferences\n",
            "- **Check Posting Date**: Ensure the job was posted within the last 3 months\n",
            "- **Evaluate Experience Level**: Match required experience with user's background\n",
            "- **Technology Stack Assessment**: Verify alignment with user's desired tech stack\n",
            "- **Domain Relevance**: Ensure the role fits the user's target domain/industry\n\n",
            
            "## OUTPUT REQUIREMENTS\n",
            "Based on your analysis of the ExtractedJob data returned by the tool:\n",
            "- **ONLY include jobs that match user preferences and criteria**\n",
            "- **Use the job_url field from the tool's response** (not your input URL)\n",
            "- **Transform the data to match SingleJobData schema**:\n",
            "  - job_title: From tool response\n",
            "  - job_description: From tool response\n",
            "  - job_url: FROM TOOL RESPONSE (this is critical!)\n",
            "  - agent_recommendation_rank: Your 1-5 assessment\n",
            "  - agent_recommendation_notes: Your detailed analysis as list of strings\n\n",
            
            "## CRITICAL WORKFLOW NOTES\n",
            f"- The web_scraping_firecrawl tool returns ```json{ExtractedJob.model_dump_json()} schema data\n",
            "- You must analyze this returned data to judge job suitability\n",
            f"- Only include jobs that pass your analysis in the final ```json{AllExtractedData.model_dump_json} output\n",
            "- Always use the job_url from the tool response, NOT the input URL you provided to the tool\n",
            "- The tool response contains the canonical/final URL after any redirects\n\n",
            
            "## FILTERING RULES\n",
            "**EXCLUDE jobs that:**\n",
            "- Use completely different technology stacks or domains from user specifications\n",
            f"- Are older than 3 months from current date  {current_date}\n",
            "- Example: If user wants Node.js full-stack, exclude .NET or Python backend roles\n",
            "- Example: If user wants AI/ML, exclude pure frontend or system admin roles\n\n",
            
            "**INCLUDE jobs that:**\n",
            "- Have similar or related technologies even if not exact matches\n",
            "- Focus on the same DOMAIN and CORE TECHNOLOGY STACK\n",
            "- Example: If user wants LangChain, include LangGraph, LlamaIndex, or similar frameworks\n",
            "- Example: If user wants React, include Vue or Angular positions\n\n",
            
            "## RANKING GUIDELINES\n",
            "**Rank 5 (Excellent Match)**: Perfect alignment with user requirements, great company, competitive package\n",
            "**Rank 4 (Very Good)**: Strong match with minor gaps, good growth opportunities\n",
            "**Rank 3 (Good)**: Decent match with some skill development needed\n",
            "**Rank 2 (Fair)**: Partial match, significant gaps but potential for learning\n",
            "**Rank 1 (Poor)**: Minimal alignment, major skill or domain mismatch\n\n",
            
            "## OUTPUT FORMAT\n",
            "**CRITICAL**: You must return ONLY a valid JSON object that matches the AllExtractedData schema structure.\n",
            f"- Each job in the 'jobs' array must follow the ```json{SingleJobData.model_dump_json} schema\n",
            "- Use job_url from the tool response (ExtractedJob.job_url), NOT your input URL\n",
            "- Only include jobs that passed your analysis and match user criteria\n",
            "- Do NOT include any text before or after the JSON\n",
            "- Do NOT use markdown formatting or code blocks\n",
            "- Do NOT include explanations, thoughts, or commentary\n",
            "- Return ONLY the raw JSON object\n",
            "- Double-check your JSON structure before responding\n\n",
            
            "## QUALITY ASSURANCE\n",
            "Before providing your final response:\n",
            "1. Verify you used job_url from tool responses, NOT input URLs\n",
            "2. Confirm all included jobs passed your analysis criteria\n",
            "3. Ensure recommendation ranks are justified by your notes\n",
            "4. Confirm JSON structure matches AllExtractedData schema exactly\n",
            "5. Validate that only suitable jobs matching user preferences are included\n",
            "6. Double-check that job_url fields contain the URLs returned by the scraping tool\n\n",
            
            "Remember: Your analysis helps job seekers make career-defining decisions. Be thorough, honest, and constructive in your evaluations."
        ])
        
        return sys_prompt
    
    def _read_job_urls_from_step2(self):
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
    
    def scrutinize_jobs(self):
        """
        Execute the job scrutinization task
        
        Reads job URLs from step 2 results file and analyzes them
        
        Returns:
            AllExtractedData: Structured job analysis results
        """
        # Read job URLs from step 2 results
        try:
            job_urls = self._read_job_urls_from_step2()
        except (FileNotFoundError, ValueError) as e:
            raise RuntimeError(f"Failed to read job URLs from step 2: {str(e)}")
        
        if not job_urls:
            raise ValueError("No job URLs found in step 2 results")
        
        # Construct the input message
        message_content = []
        message_content.append("Please analyze the following job URLs and extract detailed information:")
        
        if self.user_requirements:
            message_content.append(f"\nUser Requirements: {self.user_requirements}")
        
        message_content.append("\nJob URLs to analyze:")
        for i, url in enumerate(job_urls, 1):
            message_content.append(f"{i}. {url}")
        
        message_content.append("\nPlease scrape each URL, extract the required information, and provide your analysis following the system instructions.")
        
        # Create input for the agent
        input_data = {
            "messages": [
                {"role": "user", "content": "\n".join(message_content)}
            ]
        }
        
        # Execute the agent
        result = self.agent.invoke(input_data)

        saving_result = self._save_results(results=result)

        if saving_result:

            print("Saved step3 results broski")
            return True
        else:
            print("Ouch something happened check agent num 3")
            return None
    


    def _save_results(self , result ,output_path ):
    

        output_dir = f"./results/{self.user_id}/"
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, "step_3_job_scrutinizer_results.json")
        
        # Extract the final message content
        if result and "messages" in result:
            final_message = result["messages"][-1]["content"]
            
            # Save to file
            try:
                # Try to parse as JSON to validate
                json_data = json.loads(final_message)
                with open(output_file, 'w') as f:
                    json.dump(json_data, f, indent=2)
                
                return AllExtractedData(**json_data)
            except json.JSONDecodeError:
                # If not valid JSON, save as text for debugging
                with open(output_file.replace('.json', '_raw.txt'), 'w') as f:
                    f.write(final_message)
                raise ValueError("Agent did not return valid JSON format")







