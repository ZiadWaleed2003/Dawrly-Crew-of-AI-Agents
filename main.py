from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from app.crew import initialize_crew
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Job Search API",
    description="API for finding and managing job searches",
    version="1.0.0",
)

# Pydantic models for request/response validation
class UserJobSearchRequest(BaseModel):
    """Request model for job search parameters"""
    Job_title : str
    skills: List[str] = Field(..., description="List of user skills", min_length=1)
    experience_level: str = Field(..., description="Experience level (entry, mid, senior)")
    location: Optional[str] = Field(None, description="Preferred job location")
    job_type: Optional[str] = Field(None, description="Job type (full-time, part-time, contract)")
    salary_min: Optional[int] = Field(None, description="Minimum salary expectation", ge=0)
    
    class Config:
        schema_extra = {
            "example": {
                "skills": ["Python", "FastAPI", "Machine Learning"],
                "experience_level": "mid",
                "location": "Remote",
                "job_type": "full-time",
                "salary_min": 50000
            }
        }

class JobSearchResponse(BaseModel):
    """Response model for successful job search"""
    success: bool
    message: str

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: str
    status_code: int

# Health check endpoint
@app.get(
    "/health",
    summary="Health Check",
    description="Check if the API is running",
    response_model=Dict[str, str]
)
async def health_check():
    """Health check endpoint to verify API status"""
    return {"status": "healthy", "service": "Job Search API"}

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
    }
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
        user_dict = user_data.dict()
        
        # Initialize crew with user data
        crew_result = initialize_crew(user_dict)
        
        if crew_result is False:
            logger.error("Crew initialization failed")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process job search request. Please try again later."
            )
        
        logger.info("Job search completed successfully")
        return JobSearchResponse(
            success=True,
            message="Job search completed successfully",
            search_id=f"search_{hash(str(user_dict))}"  # Simple search ID generation
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