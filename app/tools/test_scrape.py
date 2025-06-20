from firecrawl import FirecrawlApp

app = FirecrawlApp(api_key="fc-4fb6a6ba9cf04f5fbc467a2329669a2c")


url = "https://www.indeed.com/viewjob?jk=92ae6351b7b6920d"


# For basic scraping
result = app.scrape_url(url, formats=["markdown"])

# # For structured data extraction
# result = app.scrape_url(url, 
#     formats=["markdown"], 
#     json_options={"prompt": "Extract key information from this page"}
# )

print(result)