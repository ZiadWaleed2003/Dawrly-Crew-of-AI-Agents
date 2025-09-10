from crewai import Agent, Task
import os

from app.clients import get_llm_sec
from app.models import AllExtractedData

class EvaluatorAgent:
    def __init__(self, input=None):
        self.llm = get_llm_sec()
        self.user_input = input
        self.agent = self._create_agent()
        self.task = self.create_task()
    
    def _create_agent(self):
        return Agent(
            role="Response Evaluator and Fixer",
            goal="Validate the job scrutinizer's response and automatically fix it if invalid to ensure it follows the correct JSON schema",
            backstory="""You are an expert data validator and fixer with deep knowledge of JSON schemas and Pydantic models. 
            Your task is to analyze the job scrutinizer's output, validate its structure, and if it's invalid, 
            automatically fix it to match the required AllExtractedData schema. You can extract valid JSON from 
            malformed responses, remove extra content, and ensure the output is always valid.""",
            llm=self.llm,
            verbose=True
        )
    
    def create_task(self, output_dir="./backend/results/"):
        description = "".join([
            "Evaluate and fix the job scrutinizer agent's response from the previous task.\n\n",
            "Your task is to:\n",
            "1. Analyze the job scrutinizer's output from the previous task\n",
            "2. Check if the response is valid JSON format\n",
            "3. If the response is INVALID:\n",
            "   - Extract the JSON content from any extra text or markdown\n",
            "   - Remove explanations, thoughts, or content outside the JSON\n",
            "   - Fix any JSON syntax errors\n",
            "   - Ensure it matches the AllExtractedData schema\n",
            "   - Output the corrected JSON\n",
            "4. If the response is VALID:\n",
            "   - Simply pass through the valid JSON unchanged\n\n",
            f"Required schema structure: {AllExtractedData.model_json_schema()}\n\n",
            "CRITICAL: You must ALWAYS return a valid JSON object that matches the AllExtractedData schema.\n",
            "Do NOT include any text before or after the JSON. Do NOT use markdown formatting.\n",
            "Do NOT include explanations or validation reports.\n",
            "Return ONLY the corrected/validated JSON object that can be parsed directly.\n\n",
            "If the original response was valid, return it as-is.\n",
            "If it was invalid, fix it and return the corrected version.\n",
            "Your output will be used directly by the next agent, so it must be perfect JSON."
        ])
        
        self.task = Task(
            description=description,
            expected_output="A valid JSON object matching the AllExtractedData schema (either corrected or passed through if already valid).",
            output_json=AllExtractedData,
            output_file=os.path.join(output_dir, "step_4_evaluator_fixed_results.json"),
            agent=self.agent
        )
        return self.task
    
    def evaluate_response(self, output_dir="./backend/results/"):
        return self.create_task(output_dir)
    