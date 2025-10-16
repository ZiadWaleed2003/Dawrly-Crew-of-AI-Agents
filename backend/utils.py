from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import HTTPException, Request 
from typing import List, Dict


def get_client_ip(request: Request):
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host



# yeah the time window is 1 day so 3 RPD (I'm broke as hell broski  FireCrawl credits is going to be out soon)
RATE_LIMIT_PER_DAY = 3
TIME_WINDOW = timedelta(days=1)


ip_request_store: Dict[str, List[datetime]] = defaultdict(list)

# The Rate limiter
def rate_limiter(request: Request):
    """
    This dependency function checks and enforces the rate limit.
    """
    
    # Ik anyone can get easily over it with a proxy but come on man who does this with a side project 
    client_ip = get_client_ip(request)
    
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