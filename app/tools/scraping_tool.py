from crewai.tools import tool
from app.clients import get_scrape_client


@tool
def web_scraping_tool(page_url : str):
    """
    An AI Tool to help an agent to scrape a web page

    Example:
    web_scraping_tool(
        page_url="https://www.noon.com/egypt-en/15-bar-fully-automatic-espresso-machine-1-8-l-1500"
    )
    """
    scraper = get_scrape_client()

    details = scraper.smartscraper(
        website_url= page_url,
        user_prompt= "Extract all the details from the given URL"
    )

    return {
        "Page URL" : page_url,
        "Details" : details
    }


print(web_scraping_tool(page_url="https://www.indeed.com/viewjob?jk=92ae6351b7b6920d"))