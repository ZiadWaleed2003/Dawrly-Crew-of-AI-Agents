from pydantic import BaseModel, Field
from typing import List, Optional

class SingleJobData(BaseModel):

    matches_user_req : bool = Field (... ,title="a bool value to check if the scraped data matches the user requirements or not")
    job_title: str
    job_description: str
    job_url: str

    agent_recommendation_rank: Optional[int] = Field(..., title="The rank of the job to be considered in the final procurement report. (out of 5, Higher is Better) in the recommendation list ordering from the best to the worst")
    agent_recommendation_notes: Optional[List[str]]  = Field(..., description="A set of notes why the agent would recommend or not recommend this job for the user, compared to other jobs.")

class AllExtractedData(BaseModel):
    jobs: List[SingleJobData] 

class ExtractedJob(BaseModel):
    job_title: str
    job_description: str
    job_url: str
    posting_date : str
    required_years_of_experience : str
