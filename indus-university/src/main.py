from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import urlparse, parse_qs
import sys
import os
from typing import Dict, Any, Optional

# Add the project root to the Python path to enable imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.scraper import IndusLMSScraper
from src.api import router as api_router

app = FastAPI(title="Indus University LMS Portal", 
              description="An improved version of the Indus University LMS portal")

# Include the API router
app.include_router(api_router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a directory for static files if it doesn't exist
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
os.makedirs(static_dir, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=static_dir), name="static")

templates = Jinja2Templates(directory="d:\\Projects dir\\Indus University\\indus-university\\templates")

# Create a global scraper instance
scraper = IndusLMSScraper()

# Dependency to get the scraper
def get_scraper():
    return scraper

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    # Close any existing session
    if scraper.driver:
        scraper.close()
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...), scraper: IndusLMSScraper = Depends(get_scraper)):
    try:
        # Use the Selenium-based scraper to log in
        result = scraper.login(username, password)
        
        # Add session_id to the result if login was successful
        if result.get("status") == "success" and scraper.session_id:
            result["session_id"] = scraper.session_id
            result["redirect_url"] = f"/dashboard?session={scraper.session_id}"
        
        # Return the result directly
        return result
        
    except Exception as e:
        return {"status": "error", "message": f"An error occurred during login: {str(e)}"}

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, scraper: IndusLMSScraper = Depends(get_scraper)):
    # Check if user is logged in
    if not scraper.session_id:
        return RedirectResponse(url="/")
    
    # Get dashboard data
    dashboard_data = scraper.get_dashboard_data()
    
    if dashboard_data["status"] == "error":
        return JSONResponse(content=dashboard_data)
    
    # Return the dashboard template with data and session_id
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "dashboard_data": dashboard_data,
        "session_id": scraper.session_id
    })

@app.get("/course/{course_url:path}", response_class=HTMLResponse)
async def course(request: Request, course_url: str, scraper: IndusLMSScraper = Depends(get_scraper)):
    # Check if user is logged in
    if not scraper.session_id:
        return RedirectResponse(url="/")
    
    # Get course data
    course_data = scraper.get_course_data(course_url)
    
    if course_data["status"] == "error":
        return JSONResponse(content=course_data)
    
    # Return the course template with data and session_id
    return templates.TemplateResponse("course.html", {
        "request": request,
        "course_data": course_data,
        "session_id": scraper.session_id
    })

@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request, scraper: IndusLMSScraper = Depends(get_scraper)):
    # Check if user is logged in
    if not scraper.session_id:
        return RedirectResponse(url="/")
    
    # Get profile data
    profile_data = scraper.get_profile_data()
    
    if profile_data["status"] == "error":
        return JSONResponse(content=profile_data)
    
    # Return the profile template with data and session_id
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "profile_data": profile_data.get("profile_data", {}),
        "session_id": scraper.session_id
    })

@app.on_event("shutdown")
def shutdown_event():
    # Close the scraper when the application shuts down
    scraper.close()