import sys
import os
import logging

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the scraper
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'indus-university'))
from src.scraper import IndusLMSScraper

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_login():
    """Test the login functionality of the scraper."""
    try:
        # Create a scraper instance
        logger.info("Creating scraper instance")
        scraper = IndusLMSScraper()
        
        # Attempt to login with test credentials
        logger.info("Attempting to login with test credentials")
        result = scraper.login('test_user', 'test_password')
        
        # Print the result
        logger.info(f"Login result: {result}")
        
        # Close the scraper
        scraper.close()
        
        return result
    except Exception as e:
        logger.error(f"Error during test: {str(e)}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    test_login()