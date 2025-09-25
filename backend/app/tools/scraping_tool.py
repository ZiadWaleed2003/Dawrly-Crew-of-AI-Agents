import time
from langchain_core.tools import tool
from firecrawl import JsonConfig
from app.clients import  get_fire_crawl_client
from app.models import ExtractedJob
import json


# If you are reading this u probably not so happy from the scraped results
# (istg I was planning to create my own custom scraping tool to avoid this but unfortunately I don't have the time )
# If u want to help open a PR dude the repo is yours (mi casa es su casa)




# Global counter for web_scraping_firecrawl function
cnt = 0


json_config = JsonConfig(
    prompt= "Extract ```json\n" + json.dumps(ExtractedJob.model_json_schema()) + "```\n From the web page"
)

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
    try:
        print(f"processing url : {page_url}")
        # Perform the scraping (same logic regardless of rate limiting)
        results = scraper.scrape_url(
            url=page_url,
            formats=['json'],
            json_options=json_config.model_dump(exclude_none=True),
            only_main_content=False,
            remove_base64_images=True,
            block_ads=True
        )

        if results and results.json:
            print(results.json)
            return str(results.json)
        
        else : 

            error_message = f"Scraping succeeded for {page_url}, but no JSON content was extracted."
            print(f"⚠️  {error_message}")
            return False
    
    except Exception as e:

        error_message = f"A critical error occurred while scraping {page_url}: {e}"
        print(f"❌ {error_message}")
        return False


    


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

#     extracted_data_list = scraper.extract(
#         urls=[page_url],
#         schema=SingleJobData.model_json_schema(),
#         prompt="Extract the job information from the webpage."
#     )

#     details = extracted_data_list[0]['data'] if extracted_data_list else None

#     return details