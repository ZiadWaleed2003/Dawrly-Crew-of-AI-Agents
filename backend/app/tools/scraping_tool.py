import time
from crewai.tools import tool
from firecrawl import JsonConfig
from app.clients import  get_fire_crawl_client
from app.models import SingleJobData
import json


# TODO : I need to look into this tool more tomorrow (we can make it more useful) 

# Global counter for web_scraping_firecrawl function
cnt = 0


json_config = JsonConfig(
    prompt= "Extract ```json\n" + json.dumps(SingleJobData.model_json_schema()) + "```\n From the web page"
)

# @tool
# def web_scraping_firecrawl(page_url : str):
#     """
#     An AI Tool using FireCrawl to help an agent to scrape a web page

#     Example:
#     web_scraping_firecrawl(
#         page_url="https://www.indeed.com/viewjob?jk=013dfb26c48a8ecd"
#     )
#     """
#     global cnt
#     cnt += 1 
    
#     scraper = get_fire_crawl_client()
#     print("="*50)
#     print("Visited Firecrawl tool")
#     print(f"Function call count: {cnt}")
    
#     # Check if we need to rate limit (every 10 calls)
#     if cnt % 10 == 0:
#         print(f"Rate limit reached after {cnt} calls. Waiting 60 seconds...")
#         time.sleep(60)
#         print("Rate limit wait completed. Continuing...")
    
#     # Perform the scraping (same logic regardless of rate limiting)
#     results = scraper.scrape_url(
#         url=page_url,
#         formats=['json'],
#         json_options=json_config.model_dump(exclude_none=True),
#         only_main_content=False   
#     )

#     return{
#         "Page URL" : page_url,
#         "Details"  : results.json
#     }


@tool
def web_scraping_firecrawl(page_url : str):
    """
    An AI Tool using FireCrawl to help an agent to scrape a web page

    Example:
    web_scraping_firecrawl(
        page_url="https://www.indeed.com/viewjob?jk=013dfb26c48a8ecd"
    )
    """

    global cnt
    cnt += 1 
    
    scraper = get_fire_crawl_client()
    print("="*50)
    print("Visited Firecrawl tool")
    print(f"Function call count: {cnt}")
    
    # Check if we need to rate limit (every 10 calls)
    if cnt % 10 == 0:
        print(f"Rate limit reached after {cnt} calls. Waiting 60 seconds...")
        time.sleep(60)
        print("Rate limit wait completed. Continuing...")

    extracted_data_list = scraper.extract(
        urls=[page_url],
        schema=SingleJobData.model_json_schema(),
        prompt="Extract the job information from the webpage."
    )

    details = extracted_data_list[0]['data'] if extracted_data_list else None

    return {
        "Page URL": page_url,
        "Details": details
    }