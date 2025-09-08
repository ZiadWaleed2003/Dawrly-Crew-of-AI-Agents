from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import Depends, FastAPI, HTTPException, Request, status 
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from app.crew import initialize_crew
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="Job Search API",
    description="API for finding job searches",
    version="1.0.0",
)



# yeah the time window is 1 day so 3 RPD (I'm broke as hell broski fa credits FireCrawl btroh mny)
RATE_LIMIT_PER_DAY = 3
TIME_WINDOW = timedelta(days=1)


ip_request_store: Dict[str, List[datetime]] = defaultdict(list)

app = FastAPI(
    title="FastAPI Rate Limiter",
    description="An example of a simple IP-based rate limiter for a FastAPI application."
)

# The Rate limiter
def rate_limiter(request: Request):
    """
    This dependency function checks and enforces the rate limit.
    """
    
    # Ik anyone can get easily over it with a proxy but come on man who does this with a side project 
    client_ip = request.client.host
    
    current_time = datetime.now()
    request_timestamps = ip_request_store[client_ip]
    
    relevant_timestamps = [timestamp for timestamp in request_timestamps if current_time - timestamp < TIME_WINDOW]
    
    # If the number of requests in the time window is already at the limit,
    # raise an HTTP exception.
    if len(relevant_timestamps) >= RATE_LIMIT_PER_DAY:
        raise HTTPException(
            status_code=429, 
            detail=f"Too many requests. Rate limit is {RATE_LIMIT_PER_DAY} requests per day."
        )
    
    # The request is allowed. Record the new request timestamp.
    relevant_timestamps.append(current_time)
    ip_request_store[client_ip] = relevant_timestamps
    
    return True

# Pydantic models for request/response validation
class UserJobSearchRequest(BaseModel):
    """Request model for job search parameters"""
    Job_title : str
    email_address : str
    job_type: Optional[str] = Field(None, description="Job type (full-time, part-time, contract)")
    preferred_skills: Optional[List[str]] = Field(default=[], description="List of user's skills")
    experience_level: str = Field(..., description="Fresh/Junior/Mid/Senior/Lead")
    min_years_experience: Optional[int] = Field(default=0)
    locations: List[str] = Field(default=[], description="Preferred locations")
    remote_preference: List[str] = Field(default="any", description="remote/hybrid/onsite/any")
    job_type : list[str] = Field(default=["Full-Time"] , description="Full-Time/Part-Time/Internship")
    

class JobSearchResponse(BaseModel):
    """Response model for successful job search"""
    success: bool
    status_code : int

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
    response_model=Dict[str, str],
)
def health_check():
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
def search_jobs(user_data: UserJobSearchRequest):
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
        logger.info(f"Processing job search request for user with skills: {user_data.preferred_skills}")
        
        # Convert Pydantic model to dict for crew initialization
        user_dict = user_data.model_dump()
        
        # Initialize crew with user data
        crew_result = initialize_crew(user_dict)
        
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
            search_id=f"search_{hash(str(user_dict))}" 
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