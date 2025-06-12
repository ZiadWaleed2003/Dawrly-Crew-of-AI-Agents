from crewai import LLM
import os

deepseek_r1 = LLM(
    model="openrouter/deepseek/deepseek-r1-0528:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ['OPENROUTER_API_KEY'],
    temperature=0
)


response = deepseek_r1.call(
    messages="Hello (answer in english)"
)

print(response)