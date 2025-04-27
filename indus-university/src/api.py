from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from src.scraper import IndusLMSScraper

router = APIRouter(prefix="/api", tags=["api"])

# Dependency to get the scraper
def get_scraper():
    from src.main import scraper
    return scraper

@router.get("/dashboard")
async def get_dashboard_data(scraper: IndusLMSScraper = Depends(get_scraper)):
    """Get dashboard data from the LMS portal."""
    # Check if user is logged in
    if not scraper.session_id:
        raise HTTPException(status_code=401, detail="Not logged in")
    
    # Get dashboard data
    dashboard_data = scraper.get_dashboard_data()
    
    # Return the dashboard data
    return dashboard_data

@router.get("/profile")
async def get_profile_data(scraper: IndusLMSScraper = Depends(get_scraper)):
    """Get profile data from the LMS portal using the session ID."""
    # Check if user is logged in
    if not scraper.session_id:
        raise HTTPException(status_code=401, detail="Not logged in")
    
    # Get profile data
    profile_data = scraper.get_profile_data()
    
    # Return the profile data
    return profile_data

@router.get("/course/{course_url:path}")
async def get_course_data(course_url: str, scraper: IndusLMSScraper = Depends(get_scraper)):
    """Get course data from the LMS portal."""
    # Check if user is logged in
    if not scraper.session_id:
        raise HTTPException(status_code=401, detail="Not logged in")
    
    # Get course data
    course_data = scraper.get_course_data(course_url)
    
    # Return the course data
    return course_data