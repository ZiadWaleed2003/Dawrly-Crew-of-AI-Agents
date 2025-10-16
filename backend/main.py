from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import Depends, FastAPI, HTTPException, Request, status 
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Union
import logging

from app.crew import initialize_crew
from utils import rate_limiter


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="Job Search API",
    description="API for finding job searches",
    version="1.0.0",
)

origins = [
    "https://dawrly-crew.netlify.app",
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET","POST"],
    allow_headers=["*"],
)



# Pydantic models for request/response validation
class UserJobSearchRequest(BaseModel):
    """Request model for job search parameters"""
    Job_title : str
    email_address : str
    # Accept both 'skills' and 'preferred_skills' for compatibility
    skills: Optional[Union[str, List[str]]] = Field(default=None, description="User's skills (string or list)")
    preferred_skills: Optional[List[str]] = Field(default=None, description="List of user's skills")
    experience_level: str = Field(..., description="Fresh/Junior/Mid/Senior/Lead")
    min_years_experience: Optional[Union[int, str]] = Field(default=0)
    locations: Optional[Union[str, List[str]]] = Field(default=[], description="Preferred locations (string or list)")
    remote_preference: Optional[Union[str, List[str]]] = Field(default="any", description="remote/hybrid/onsite/any")
    job_type : Optional[Union[str, List[str]]] = Field(default=["Full-Time"] , description="Full-Time/Part-Time/Internship")
    
    @field_validator('min_years_experience', mode='before')
    @classmethod
    def convert_years_to_int(cls, v):
        """Convert string years to integer"""
        if isinstance(v, str):
            return int(v) if v.isdigit() else 0
        return v
    
    @field_validator('skills', 'preferred_skills', 'locations', 'remote_preference', 'job_type', mode='before')
    @classmethod
    def convert_to_list(cls, v):
        """Convert string values to list, handle case sensitivity"""
        if v is None:
            return []
        if isinstance(v, str):
            # Split by comma if contains commas, otherwise make it a list
            if ',' in v:
                return [item.strip() for item in v.split(',')]
            return [v] if v else []
        if isinstance(v, list):
            # Normalize case for remote_preference and job_type
            return v
        return []
    
    def model_post_init(self, __context):
        """After validation, merge skills and preferred_skills"""
        # If skills is provided but preferred_skills is not, use skills
        if self.skills and not self.preferred_skills:
            self.preferred_skills = self.skills if isinstance(self.skills, list) else [self.skills]
        # If preferred_skills is empty and skills exists, use skills
        elif not self.preferred_skills and self.skills:
            self.preferred_skills = self.skills if isinstance(self.skills, list) else [self.skills]
    

class JobSearchResponse(BaseModel):
    """Response model for successful job search"""
    success: bool
    status_code : int

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: str
    status_code: int

#root endpoint

@app.get(
        "/"
)
async def main():
    return {"message": "Yeah it's working broski"}


# Health check endpoint
@app.get(
    "/health",
    summary="Health Check",
    description="Check if the API is running",
    response_model=Dict[str, str],
)
async def health_check():
    """Health check endpoint to verify API status"""
    return {"status": "healthy", "service": "Job Search API is working"}

# Job search endpoint
@app.post(
    "/jobs/search",
    summary="Search for Jobs",
    description="Search for jobs based on user criteria",
    response_model=JobSearchResponse,
    responses={
        200: {"description": "Job search completed successfully"},
        400: {"description": "Invalid request data"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    } , dependencies=[Depends(rate_limiter)]
)
async def search_jobs(user_data: UserJobSearchRequest):
    """
    Search for jobs based on user criteria
    
    Args:
        user_data: User job search parameters including skills, experience, etc.
        
    Returns:
        JobSearchResponse: Results of the job search operation
        
    Raises:
        HTTPException: If job search fails or invalid data provided
    """
    try:
        logger.info(f"Processing job search request for user with skills: {user_data.skills}")
        
        # Convert Pydantic model to dict for crew initialization
        user_dict = user_data.model_dump()
        
        # Initialize crew with user data
        crew_result = await initialize_crew(user_dict)
        
        if crew_result is False:
            logger.error("Crew initialization and execution failed")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process job search request. Please try again later."
            )
        
        logger.info("Job search completed successfully")
        return JobSearchResponse(
            success=True,
            message="Job search completed successfully",
            search_id=f"search_{hash(str(user_dict))}" ,
            status_code=200
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request data: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during job search: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later."
        )