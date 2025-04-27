# Improved Indus University LMS Portal

This project is an improved version of the Indus University Learning Management System (LMS) portal, featuring a modern UI and using Selenium in headless mode for web scraping.

## Features

- **Selenium-based Scraping**: Uses Selenium WebDriver in headless mode to interact with the original LMS portal, allowing for better handling of JavaScript-rendered content.
- **Modern UI**: Completely redesigned user interface with responsive design using Tailwind CSS.
- **FastAPI Backend**: Robust API endpoints built with FastAPI for efficient data handling.
- **Improved Dashboard**: Enhanced dashboard with better organization of courses, announcements, and upcoming events.
- **Detailed Course Pages**: Comprehensive course pages with materials, assignments, grades, and discussions.

## Project Structure

```
├── indus-university/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py         # FastAPI application
│   │   ├── scraper.py      # Selenium-based scraper
│   │   ├── api.py          # API endpoints
│   │   ├── database.py     # Database connections (placeholder)
│   │   └── models.py       # Data models (placeholder)
│   ├── templates/
│   │   ├── login.html      # Login page template
│   │   ├── dashboard.html  # Dashboard template
│   │   └── course.html     # Course details template
│   └── static/             # Static files (CSS, JS, images)
├── requirements/
│   └── base.txt            # Python dependencies
└── .env                    # Environment variables (create this file)
```

## Setup Instructions

1. **Clone the repository**

2. **Create and activate a virtual environment**
   ```
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   source .venv/bin/activate  # On Unix/MacOS
   ```

3. **Install dependencies**
   ```
   pip install -r requirements/base.txt
   ```

4. **Run the application**
   ```
   cd indus-university
   uvicorn src.main:app --reload
   ```

5. **Access the application**
   Open your browser and navigate to `http://localhost:8000`

## Usage

1. **Login**: Use your Indus University LMS credentials to log in.
2. **Dashboard**: After successful login, you'll be redirected to the dashboard showing your courses, announcements, and upcoming events.
3. **Course Details**: Click on any course to view detailed information including materials, assignments, grades, and discussions.

## Technical Details

### Selenium Scraper

The application uses Selenium WebDriver with Chrome in headless mode to interact with the original LMS portal. This approach allows for better handling of JavaScript-rendered content and dynamic elements compared to traditional request-based scraping.

Key components of the scraper:
- **Login**: Authenticates with the original LMS portal using provided credentials.
- **Dashboard Data**: Extracts announcements, courses, and other relevant information from the dashboard.
- **Course Data**: Retrieves course-specific information including materials, assignments, and grades.

### FastAPI Application

The backend is built with FastAPI, providing efficient API endpoints and HTML template rendering:
- **HTML Routes**: Serve the improved UI templates.
- **API Routes**: Provide JSON data endpoints for frontend JavaScript to consume.
- **Authentication**: Manages user sessions through the Selenium scraper.

## Notes

- This application does not store any user credentials or session data persistently.
- The Selenium WebDriver requires Chrome to be installed on the system.
- The application is designed for educational purposes and personal use only.

## Future Improvements

- Add persistent storage for user preferences and settings.
- Implement caching to reduce load on the original LMS portal.
- Add offline mode for accessing previously loaded content.
- Enhance mobile responsiveness for better experience on small screens.