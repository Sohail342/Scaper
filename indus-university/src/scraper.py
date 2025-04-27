from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging
from typing import Dict, Any, Optional, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

dev_mode = False

class IndusLMSScraper:
    """A Selenium-based scraper for the Indus University LMS portal."""
    
    def __init__(self):
        """Initialize the scraper with a headless Chrome browser."""
        self.base_url = "http://lms.induscms.com:81/ords/r/erasoft/student-app1400450"
        self.login_url = f"{self.base_url}/login"
        self.driver = None
        self.session_id = None
    
    def setup_driver(self):
        """Set up the Selenium WebDriver with Chrome in headless mode."""
        try:
            chrome_options = Options()
            if not dev_mode:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("WebDriver set up successfully")
            return True
        except Exception as e:
            logger.error(f"Error setting up WebDriver: {str(e)}")
            return False
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Log in to the Indus University LMS portal.
        
        Args:
            username: The username for login
            password: The password for login
            
        Returns:
            A dictionary with login status and session information
        """
        if not self.driver:
            if not self.setup_driver():
                return {"status": "error", "message": "Failed to set up WebDriver"}
        
        try:
            # Navigate to the login page
            logger.info(f"Navigating to {self.login_url}")
            self.driver.get(self.login_url)
            
            # Wait for the page to load completely
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Save a screenshot for debugging
            try:
                screenshot_path = "login_page_screenshot.png"
                self.driver.save_screenshot(screenshot_path)
                logger.info(f"Saved login page screenshot to {screenshot_path}")
            except Exception as e:
                logger.warning(f"Could not save screenshot: {str(e)}")
            
            # Log the page title and URL for debugging
            logger.info(f"Page title: {self.driver.title}")
            logger.info(f"Current URL: {self.driver.current_url}")
            
            # Log the HTML structure for debugging
            page_source = self.driver.page_source
            logger.info(f"Page source length: {len(page_source)} characters")
            logger.info(f"Page source preview: {page_source[:500]}...")
           


            # Directly target the username and password fields by their IDs
            logger.info("Directly targeting username and password fields by their IDs")
            
            try:
                # Find username and password fields directly by their IDs
                username_field = self.driver.find_element(By.ID, "P9999_USERNAME")
                password_field = self.driver.find_element(By.ID, "P9999_PASSWORD")
                logger.info("Successfully found username and password fields by their IDs")
            except Exception as e:
                error_msg = f"Could not find username and password fields by their IDs: {str(e)}"
                logger.error(error_msg)
                return {"status": "error", "message": error_msg}
            
            # Log the found fields for debugging
            logger.info(f"Username field: {username_field.get_attribute('outerHTML')}")
            logger.info(f"Password field: {password_field.get_attribute('outerHTML')}")

            
            # Enter credentials
            logger.info("Entering credentials")
            username_field.clear()
            username_field.send_keys(username)
            password_field.clear()
            password_field.send_keys(password)
            
            # Set the p_request parameter to LOGIN
            try:
                # Try to find the p_request hidden input field
                p_request_field = self.driver.find_element(By.ID, "pRequest")
                self.driver.execute_script("arguments[0].value = 'LOGIN';", p_request_field)
                logger.info("Set p_request field to LOGIN")
            except Exception as e:
                logger.info(f"Could not find p_request field: {str(e)}")
                # If we can't find the field, we'll try to add it via JavaScript
                try:
                    self.driver.execute_script("var input = document.createElement('input'); input.type = 'hidden'; input.name = 'p_request'; input.value = 'LOGIN'; document.forms[0].appendChild(input);")
                    logger.info("Added p_request field via JavaScript")
                except Exception as e:
                    logger.warning(f"Could not add p_request field: {str(e)}")
            
            # Based on the HTML structure, we need a different approach to submit the login form
            logger.info("Using improved approach for Oracle APEX login form")
            
            try:
                # First, try to find the form element directly
                form_elements = self.driver.find_elements(By.TAG_NAME, "form")
                form_id = None
                
                if form_elements:
                    logger.info(f"Found {len(form_elements)} form elements")
                    for form in form_elements:
                        form_id = form.get_attribute("id")
                        form_action = form.get_attribute("action")
                        logger.info(f"Form ID: {form_id}, Action: {form_action}")
                else:
                    logger.warning("No form elements found on the page")
                
                # Find the Sign In button - first try with the specific ID, then try other methods
                submit_button = None
                
                # Take a screenshot before searching for the button
                try:
                    screenshot_path = "login_button_search_screenshot.png"
                    self.driver.save_screenshot(screenshot_path)
                    logger.info(f"Saved screenshot before searching for button to {screenshot_path}")
                except Exception as screenshot_error:
                    logger.warning(f"Could not save button search screenshot: {str(screenshot_error)}")
                
                # Log all buttons on the page to help identify the correct one
                try:
                    all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    logger.info(f"Found {len(all_buttons)} buttons on the page")
                    for i, button in enumerate(all_buttons):
                        button_id = button.get_attribute("id")
                        button_text = button.text
                        button_class = button.get_attribute("class")
                        button_type = button.get_attribute("type")
                        logger.info(f"Button {i+1}: ID={button_id}, Text='{button_text}', Class='{button_class}', Type='{button_type}'")
                        
                        # If we find a button with ID B325920686219386643, use it
                        if button_id == "B325920686219386643":
                            submit_button = button
                            logger.info(f"Found Sign In button with ID B325920686219386643")
                            break
                        
                        # Look for buttons with text containing 'Sign In' or 'Login'
                        if button_text and ('sign in' in button_text.lower() or 'login' in button_text.lower()):
                            submit_button = button
                            logger.info(f"Found button with Sign In/Login text: '{button_text}'")
                            break
                except Exception as button_error:
                    logger.warning(f"Error listing buttons: {str(button_error)}")
                
                # If we still haven't found a button, try other elements that might be the login button
                if not submit_button:
                    # Try to find elements that might be the login button
                    selectors = [
                        "//button[@type='submit']",
                        "//input[@type='submit']",
                        "//button[contains(@class, 'login') or contains(@class, 'submit')]",
                        "//button[contains(text(), 'Login') or contains(text(), 'Sign In')]",
                        "//a[contains(@class, 'login') or contains(@class, 'submit')]",
                        "//a[contains(text(), 'Login') or contains(text(), 'Sign In')]",
                        "//div[contains(@class, 'login') or contains(@class, 'submit')]",
                        "//span[contains(text(), 'Login') or contains(text(), 'Sign In')]"
                    ]
                    
                    for selector in selectors:
                        try:
                            elements = self.driver.find_elements(By.XPATH, selector)
                            if elements:
                                submit_button = elements[0]
                                logger.info(f"Found submit button using selector: {selector}")
                                logger.info(f"Submit button HTML: {submit_button.get_attribute('outerHTML')}")
                                break
                        except Exception as e:
                            logger.info(f"Error finding submit button with selector {selector}: {str(e)}")
                
                # Add the p_request parameter to the form
                try:
                    # Try to find the p_request hidden input field
                    p_request_field = None
                    try:
                        p_request_field = self.driver.find_element(By.ID, "pRequest")
                    except:
                        try:
                            p_request_field = self.driver.find_element(By.NAME, "p_request")
                        except:
                            pass
                    
                    if p_request_field:
                        self.driver.execute_script("arguments[0].value = 'LOGIN';", p_request_field)
                        logger.info("Set existing p_request field to LOGIN")
                    else:
                        # If we can't find the field, add it via JavaScript
                        self.driver.execute_script("""
                            var input = document.createElement('input');
                            input.type = 'hidden';
                            input.name = 'p_request';
                            input.value = 'LOGIN';
                            document.querySelector('form').appendChild(input);
                        """)
                        logger.info("Added p_request field via JavaScript")
                except Exception as e:
                    logger.warning(f"Error setting p_request field: {str(e)}")
                
                # Try to click the Sign In button or use alternative methods
                try:
                    logger.info("Attempting to click the Sign In button")
                    if submit_button:
                        # Try multiple ways to click the button
                        click_methods = [
                            # Method 1: Standard click
                            lambda: submit_button.click(),
                            # Method 2: JavaScript click
                            lambda: self.driver.execute_script("arguments[0].click();", submit_button),
                            # Method 3: JavaScript click with event simulation
                            lambda: self.driver.execute_script("""
                                var evt = document.createEvent('MouseEvents');
                                evt.initMouseEvent('click', true, true, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);
                                arguments[0].dispatchEvent(evt);
                            """, submit_button)
                        ]
                        
                        for i, click_method in enumerate(click_methods):
                            try:
                                logger.info(f"Trying click method {i+1}")
                                click_method()
                                logger.info(f"Click method {i+1} executed without errors")
                                
                                # Take a screenshot after clicking
                                try:
                                    screenshot_path = f"after_click_method_{i+1}_screenshot.png"
                                    self.driver.save_screenshot(screenshot_path)
                                    logger.info(f"Saved screenshot after click method {i+1} to {screenshot_path}")
                                except Exception as screenshot_error:
                                    logger.warning(f"Could not save after-click screenshot: {str(screenshot_error)}")
                                
                                # Wait a moment to see if the form submission worked
                                time.sleep(5)  # Increased wait time to ensure page loads
                                
                                # Check if we're still on the login page
                                if "login" not in self.driver.current_url.lower():
                                    logger.info(f"Successfully logged in using click method {i+1}")
                                    break
                            except Exception as e:
                                logger.warning(f"Click method {i+1} failed: {str(e)}")
                    else:
                        logger.warning("Submit button not found, trying alternative methods")
                        
                        # Try one more direct approach - find button by ID and click it directly
                        try:
                            # Try to find the button directly by ID and click it
                            direct_button = self.driver.find_element(By.ID, "B325920686219386643")
                            logger.info("Found button directly by ID B325920686219386643")
                            direct_button.click()
                            logger.info("Clicked button directly by ID")
                            time.sleep(5)
                        except Exception as direct_error:
                            logger.warning(f"Direct button click failed: {str(direct_error)}")
                        
                        # Fallback methods if button click fails
                        fallback_methods = [
                            # Method 1: Submit the form using JavaScript with form ID
                            lambda: form_id and self.driver.execute_script(f"document.getElementById('{form_id}').submit();"),
                            
                            # Method 2: Submit the first form using JavaScript
                            lambda: self.driver.execute_script("document.querySelector('form').submit();"),
                            
                            # Method 3: Press Enter in the password field
                            lambda: password_field.send_keys("\n")
                        ]
                        
                        # Try each fallback method until one works
                        for i, method in enumerate(fallback_methods):
                            try:
                                logger.info(f"Trying fallback method {i+1}")
                                method()
                                logger.info(f"Fallback method {i+1} executed without errors")
                                
                                # Wait a moment to see if the form submission worked
                                time.sleep(3)
                                
                                # Check if we're still on the login page
                                if "login" not in self.driver.current_url.lower():
                                    logger.info(f"Successfully logged in using fallback method {i+1}")
                                    break
                            except Exception as e:
                                logger.warning(f"Fallback method {i+1} failed: {str(e)}")
                except Exception as e:
                    logger.error(f"Error clicking Sign In button: {str(e)}")
                
                # If we're still on the login page after trying all methods, try a direct POST
                if "login" in self.driver.current_url.lower():
                    logger.info("Still on login page, trying direct form submission with specific APEX parameters")
                    
                    # Get any additional form fields that might be needed
                    form_data = {}
                    try:
                        hidden_fields = self.driver.find_elements(By.XPATH, "//input[@type='hidden']")
                        for field in hidden_fields:
                            name = field.get_attribute("name")
                            value = field.get_attribute("value")
                            if name and value:
                                form_data[name] = value
                                logger.info(f"Found hidden field: {name} = {value}")
                    except Exception as e:
                        logger.warning(f"Error getting hidden fields: {str(e)}")
                    
                    # Add our known required fields
                    form_data["p_request"] = "LOGIN"
                    form_data["p_flow_id"] = self.driver.execute_script("return $v('pFlowId') || $v('pFlowID') || '';")
                    form_data["p_flow_step_id"] = self.driver.execute_script("return $v('pFlowStepId') || '';")
                    form_data["p_instance"] = self.driver.execute_script("return $v('pInstance') || '';")
                    
                    # Construct and execute the form submission
                    js_code = """
                    var formData = arguments[0];
                    var formStr = '';
                    for (var key in formData) {
                        if (formData.hasOwnProperty(key)) {
                            formStr += '&' + encodeURIComponent(key) + '=' + encodeURIComponent(formData[key]);
                        }
                    }
                    formStr = formStr.substring(1); // Remove the leading &
                    
                    var xhr = new XMLHttpRequest();
                    xhr.open('POST', '/ords/wwv_flow.accept', false);
                    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
                    xhr.send(formStr);
                    
                    if (xhr.status === 200) {
                        window.location.href = xhr.responseURL || xhr.getResponseHeader('Location') || window.location.href;
                        return true;
                    }
                    return false;
                    """
                    
                    result = self.driver.execute_script(js_code, form_data)
                    logger.info(f"Direct form submission result: {result}")
            except Exception as e:
                logger.error(f"Failed to submit login form: {str(e)}")
                raise Exception(f"Could not submit login form: {str(e)}")
            
            # Wait for redirect after login
            time.sleep(5)  # Give it more time to process and handle redirects
            
            # Check if login was successful by looking for session in URL or cookies
            current_url = self.driver.current_url
            
            if "session=" in current_url:
                # Extract session ID from URL
                session_id = current_url.split("session=")[1].split("&")[0] if "&" in current_url.split("session=")[1] else current_url.split("session=")[1]
                self.session_id = session_id
                logger.info(f"Extracted session ID from URL: {session_id}")
                return {
                    "status": "success", 
                    "session_id": session_id,
                    "home_url": current_url
                }
            
            # Check if we're on a dashboard or home page
            if "dashboard" in current_url.lower() or "home" in current_url.lower():
                # Try to extract session ID from the URL even if not in the standard format
                if "session" in current_url:
                    try:
                        session_parts = current_url.split("session")
                        if len(session_parts) > 1:
                            # Try to extract the session ID after the "session" keyword
                            session_part = session_parts[1]
                            if session_part.startswith("="):
                                session_id = session_part[1:].split("&")[0] if "&" in session_part[1:] else session_part[1:]
                                self.session_id = session_id
                                logger.info(f"Extracted session ID from dashboard URL: {session_id}")
                                return {
                                    "status": "success", 
                                    "session_id": session_id,
                                    "redirect_url": current_url
                                }
                    except Exception as e:
                        logger.warning(f"Failed to extract session ID from URL: {str(e)}")
                
                # If we couldn't extract a session ID, use a placeholder
                self.session_id = "active_session"  # Just a placeholder
                return {
                    "status": "success", 
                    "message": "Login successful, redirected to dashboard", 
                    "redirect_url": current_url
                }
            
            # Check cookies for session
            cookies = self.driver.get_cookies()
            for cookie in cookies:
                if "session" in cookie['name'].lower():
                    self.session_id = cookie['value']
                    return {"status": "success", "session_id": cookie['value']}
            
            # If we get here, login probably failed
            return {"status": "error", "message": "Login failed. Could not find session information."}
            
        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            return {"status": "error", "message": f"An error occurred during login: {str(e)}"}
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Scrape dashboard data after successful login.
        
        Returns:
            A dictionary containing dashboard data
        """
        if not self.driver or not self.session_id:
            return {"status": "error", "message": "Not logged in"}
        
        try:
            # Wait for dashboard elements to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Extract page title
            page_title = self.driver.title
            
            # Extract announcements (this is a placeholder - adjust selectors based on actual page structure)
            announcements = []
            try:
                announcement_elements = self.driver.find_elements(By.CSS_SELECTOR, ".announcement-item")
                for element in announcement_elements:
                    announcements.append({
                        "title": element.find_element(By.CSS_SELECTOR, ".title").text,
                        "date": element.find_element(By.CSS_SELECTOR, ".date").text,
                        "content": element.find_element(By.CSS_SELECTOR, ".content").text
                    })
            except:
                logger.warning("Could not find announcements")
            
            # Extract courses (this is a placeholder - adjust selectors based on actual page structure)
            courses = []
            try:
                course_elements = self.driver.find_elements(By.CSS_SELECTOR, ".course-item")
                for element in course_elements:
                    courses.append({
                        "title": element.find_element(By.CSS_SELECTOR, ".title").text,
                        "instructor": element.find_element(By.CSS_SELECTOR, ".instructor").text,
                        "url": element.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                    })
            except:
                logger.warning("Could not find courses")
            
            # Get page HTML for further processing if needed
            page_html = self.driver.page_source
            
            return {
                "status": "success",
                "page_title": page_title,
                "announcements": announcements,
                "courses": courses,
                "html": page_html  # Include HTML for further processing if needed
            }
            
        except Exception as e:
            logger.error(f"Error scraping dashboard: {str(e)}")
            return {"status": "error", "message": f"An error occurred while scraping dashboard: {str(e)}"}
    
    def get_course_data(self, course_url: str) -> Dict[str, Any]:
        """Scrape data for a specific course.
        
        Args:
            course_url: The URL of the course page
            
        Returns:
            A dictionary containing course data
        """
        if not self.driver or not self.session_id:
            return {"status": "error", "message": "Not logged in"}
        
        try:
            # Navigate to the course page
            self.driver.get(course_url)
            
            # Wait for course page elements to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Extract course title
            course_title = self.driver.title
            
            # Extract course materials (this is a placeholder - adjust selectors based on actual page structure)
            materials = []
            try:
                material_elements = self.driver.find_elements(By.CSS_SELECTOR, ".material-item")
                for element in material_elements:
                    materials.append({
                        "title": element.find_element(By.CSS_SELECTOR, ".title").text,
                        "type": element.find_element(By.CSS_SELECTOR, ".type").text,
                        "url": element.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                    })
            except:
                logger.warning("Could not find course materials")
            
            # Extract assignments (this is a placeholder - adjust selectors based on actual page structure)
            assignments = []
            try:
                assignment_elements = self.driver.find_elements(By.CSS_SELECTOR, ".assignment-item")
                for element in assignment_elements:
                    assignments.append({
                        "title": element.find_element(By.CSS_SELECTOR, ".title").text,
                        "due_date": element.find_element(By.CSS_SELECTOR, ".due-date").text,
                        "status": element.find_element(By.CSS_SELECTOR, ".status").text
                    })
            except:
                logger.warning("Could not find assignments")
            
            # Get page HTML for further processing if needed
            page_html = self.driver.page_source
            
            return {
                "status": "success",
                "course_title": course_title,
                "materials": materials,
                "assignments": assignments,
                "html": page_html  # Include HTML for further processing if needed
            }
            
        except Exception as e:
            logger.error(f"Error scraping course: {str(e)}")
            return {"status": "error", "message": f"An error occurred while scraping course: {str(e)}"}
    
    def parse_contextual_info_html(self, html_content: str) -> Dict[str, Any]:
        """Parse profile data from the contextual info HTML format.
        
        Args:
            html_content: HTML content containing profile information in contextual info format
            
        Returns:
            A dictionary containing extracted profile data
        """
        from bs4 import BeautifulSoup
        import re
        
        profile_data = {}
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find all contextual info items
            info_items = soup.find_all('div', class_='t-ContextualInfo-item')
            
            for item in info_items:
                # Get the label and value elements
                label_elem = item.find('span', class_='t-ContextualInfo-label')
                value_elem = item.find('span', class_='t-ContextualInfo-value')
                
                if not label_elem or not value_elem:
                    continue
                    
                label = label_elem.text.strip()
                value = value_elem.text.strip()
                
                # Extract profile picture URL if present
                if not label and value_elem.find('img'):
                    img = value_elem.find('img')
                    # Get the src attribute which contains the image URL
                    img_src = img.get('src')
                    
                    # Check if the image URL is relative or absolute
                    if img_src and img_src.startswith('apex_util.get_blob_file'):
                        # This is a relative URL, construct the full URL
                        # The base URL for the LMS portal is http://lms.induscms.com:81/ords/
                        img_src = f"http://lms.induscms.com:81/ords/{img_src}"
                    
                    # Store the complete image URL - this is the URL to the profile image in the original portal
                    # The URL format is typically like: apex_util.get_blob_file?a=450&s=15794612790297&p=3&d=329146349552826802&i=329143997861826801&p_pk1=984-2022&p_pk2=&p_ck=...
                    profile_data['profile_picture'] = img_src
                    
                    # Also store the image attributes for reference
                    profile_data['profile_picture_height'] = img.get('height')
                    profile_data['profile_picture_width'] = img.get('width')
                    profile_data['profile_picture_alt'] = img.get('alt')
                    profile_data['profile_picture_title'] = img.get('title')
                    
                    logger.info(f"Extracted profile picture URL: {img_src}")
                    continue
                    
                # Process different types of information based on label
                if 'Name & ID' in label:
                    # Split the value by newlines to get name and ID separately
                    parts = value.split('\n')
                    if len(parts) >= 3:
                        profile_data['name'] = parts[0].strip()
                        profile_data['middle_name'] = parts[1].strip()
                        profile_data['student_id'] = parts[2].strip()
                    elif len(parts) >= 1:
                        profile_data['name'] = parts[0].strip()
                        if len(parts) >= 2:
                            # Check if the second part looks like an ID (contains numbers)
                            if re.search(r'\d', parts[1]):
                                profile_data['student_id'] = parts[1].strip()
                            else:
                                profile_data['middle_name'] = parts[1].strip()
                
                elif 'Campus Info' in label:
                    parts = value.split('\n')
                    if len(parts) >= 1:
                        profile_data['campus'] = parts[0].strip()
                    if len(parts) >= 2:
                        profile_data['faculty'] = parts[1].strip()
                    if len(parts) >= 3:
                        profile_data['program'] = parts[2].strip()
                    if len(parts) >= 4:
                        # Extract semester information from the format BS(SE)-22B (6th)
                        semester_info = parts[3].strip()
                        profile_data['batch'] = semester_info
                        
                        # Try to extract just the semester number
                        semester_match = re.search(r'\((\d+)(?:st|nd|rd|th)\)', semester_info)
                        if semester_match:
                            profile_data['semester'] = semester_match.group(1)
                
                elif 'Contact Info' in label:
                    parts = value.split('\n')
                    if len(parts) >= 1:
                        profile_data['phone'] = parts[0].strip()
                    if len(parts) >= 2:
                        profile_data['email'] = parts[1].strip()
                    if len(parts) >= 3:
                        profile_data['institutional_email'] = parts[2].strip()
                
                elif 'DOB, CNIC & Blood Group' in label:
                    parts = value.split('\n')
                    if len(parts) >= 1:
                        profile_data['dob'] = parts[0].strip()
                    if len(parts) >= 2:
                        profile_data['age'] = parts[1].strip()
                    if len(parts) >= 3:
                        profile_data['cnic'] = parts[2].strip()
                    if len(parts) >= 4 and parts[3].strip():
                        profile_data['blood_group'] = parts[3].strip()
                
                elif 'Permanent Address' in label:
                    profile_data['address'] = value
                
                elif 'Admission Status' in label:
                    profile_data['status'] = value
                
                # Store any other labeled values
                elif label and value:
                    key = label.lower().replace(' ', '_').replace(',', '').replace('&', 'and')
                    profile_data[key] = value
            
            logger.info(f"Extracted profile data from contextual info HTML: {list(profile_data.keys())}")
            return profile_data
            
        except Exception as e:
            logger.error(f"Error parsing contextual info HTML: {str(e)}")
            return {}
    
    def get_profile_data(self) -> Dict[str, Any]:
        """Scrape profile data using the session ID.
        
        Returns:
            A dictionary containing profile data
        """
        if not self.driver or not self.session_id:
            return {"status": "error", "message": "Not logged in"}
        
        try:
            # Construct the profile URL with the session ID
            profile_url = f"{self.base_url}/my-profile1?session={self.session_id}"
            logger.info(f"Navigating to profile page: {profile_url}")
            
            # Navigate to the profile page
            self.driver.get(profile_url)
            
            # Wait for profile page elements to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Save a screenshot for debugging
            try:
                screenshot_path = "profile_page_screenshot.png"
                self.driver.save_screenshot(screenshot_path)
                logger.info(f"Saved profile page screenshot to {screenshot_path}")
            except Exception as e:
                logger.warning(f"Could not save profile screenshot: {str(e)}")
            
            # Log the current URL to verify we're on the profile page
            current_url = self.driver.current_url
            logger.info(f"Current URL after navigation: {current_url}")
            
            # Get page HTML for processing
            page_html = self.driver.page_source
            
            # Extract profile information using a more dynamic approach
            profile_data = {}
            
            # First, try to find contextual info items which is the format we're looking for
            try:
                contextual_items = self.driver.find_elements(By.CSS_SELECTOR, ".t-ContextualInfo-item")
                if contextual_items and len(contextual_items) > 0:
                    logger.info(f"Found {len(contextual_items)} contextual info items")
                    
                    # If we found contextual info items, extract the HTML and parse it
                    contextual_html = ""
                    for item in contextual_items:
                        contextual_html += item.get_attribute("outerHTML")
                    
                    if contextual_html:
                        profile_data = self.parse_contextual_info_html(contextual_html)
                        logger.info("Successfully parsed contextual info HTML")
            except Exception as e:
                logger.warning(f"Error extracting contextual info items: {str(e)}")
            
            # If we couldn't extract data from contextual info, try other approaches
            if not profile_data:
                # Try to find profile data in the page HTML directly
                try:
                    # Check if the page contains contextual info structure
                    if "t-ContextualInfo-item" in page_html:
                        profile_data = self.parse_contextual_info_html(page_html)
                        logger.info("Parsed contextual info from page HTML")
                except Exception as e:
                    logger.warning(f"Error parsing contextual info from page HTML: {str(e)}")
                
                # If still no data, try the original approaches
                if not profile_data:
                    # 1. Look for common profile field labels and their adjacent values
                    try:
                        # Find all label elements that might contain profile field names
                        labels = self.driver.find_elements(By.XPATH, "//label | //div[contains(@class, 'label')] | //span[contains(@class, 'label')]")
                        
                        for label in labels:
                            label_text = label.text.strip().lower()
                            if not label_text:
                                continue
                                
                            # Try to find the associated value based on common patterns
                            value = None
                            
                            # Pattern 1: Value is in the next sibling element
                            try:
                                value_elem = self.driver.execute_script("return arguments[0].nextElementSibling", label)
                                if value_elem and value_elem.text.strip():
                                    value = value_elem.text.strip()
                            except:
                                pass
                                
                            # Pattern 2: Value is in a child element with a specific class
                            if not value:
                                try:
                                    value_elem = label.find_element(By.XPATH, "./following-sibling::*[1] | ./following::input[1] | ./following::div[contains(@class, 'value')][1]")
                                    if value_elem:
                                        value = value_elem.text.strip() or value_elem.get_attribute("value")
                                except:
                                    pass
                            
                            # Map common profile field labels to standardized keys
                            if "name" in label_text or "full name" in label_text:
                                profile_data["name"] = value
                            elif "id" in label_text or "student id" in label_text or "enrollment" in label_text:
                                profile_data["student_id"] = value
                            elif "email" in label_text:
                                profile_data["email"] = value
                            elif "phone" in label_text or "mobile" in label_text:
                                profile_data["phone"] = value
                            elif "department" in label_text:
                                profile_data["department"] = value
                            elif "program" in label_text or "course" in label_text:
                                profile_data["program"] = value
                            elif "semester" in label_text or "term" in label_text:
                                profile_data["semester"] = value
                            elif "batch" in label_text or "year" in label_text:
                                profile_data["batch"] = value
                            elif value:  # Store other labeled values with their label as key
                                profile_data[label_text.replace(" ", "_")] = value
                                
                        logger.info(f"Extracted profile data using label approach: {list(profile_data.keys())}")
                    except Exception as e:
                        logger.warning(f"Error extracting profile data using labels: {str(e)}")
                    
                    # 2. Try to find profile data in table rows
                    if not profile_data:
                        try:
                            rows = self.driver.find_elements(By.XPATH, "//tr")
                            for row in rows:
                                cells = row.find_elements(By.XPATH, "./td | ./th")
                                if len(cells) >= 2:
                                    key = cells[0].text.strip().lower().replace(" ", "_")
                                    value = cells[1].text.strip()
                                    if key and value:
                                        profile_data[key] = value
                            
                            logger.info(f"Extracted profile data using table approach: {list(profile_data.keys())}")
                        except Exception as e:
                            logger.warning(f"Error extracting profile data from tables: {str(e)}")
            
            # For testing purposes, if we're in development mode and couldn't extract data,
            # use the sample data provided by the user
            if dev_mode and (not profile_data or len(profile_data) < 3):
                sample_html = """<div class="t-ContextualInfo-item">
  <span class="t-ContextualInfo-label"> </span>
  <span class="t-ContextualInfo-value"><img style="border: 4px solid #CCC; -moz-border-radius:50%; -webkit-border-radius:50%;" src="apex_util.get_blob_file?a=450&s=14599668922173&p=3&d=329146349552826802&i=329143997861826801&p_pk1=984-2022&p_pk2=&p_ck=9Y6djO-Ljt0Y2uOlYA6PQkgeGl_H05kP2jFxdMpDUvKwD5d6YQZyv5jWLqxK3xtplp8wWwy5ZgTJ80klSOm1DQ" height="80" width="80" alt=" " title="Pic" /></span>
</div><div class="t-ContextualInfo-item">
  <span class="t-ContextualInfo-label">Name & ID</span>
  <span class="t-ContextualInfo-value">Sohail Ahmad<br>Shah Makeen<br>984-2022</span>
</div><div class="t-ContextualInfo-item">
  <span class="t-ContextualInfo-label">Campus Info</span>
  <span class="t-ContextualInfo-value">Main Campus<br>Faculty of Computing & Information Technology<br>Bachelor of Science in Software Engineering<br>BS(SE)-22B (6th)</span>
</div><div class="t-ContextualInfo-item">
  <span class="t-ContextualInfo-label">Contact Info</span>
  <span class="t-ContextualInfo-value">03428041928<br>sohailshoail48@gmail.com<br>984-2022@lms.indus.edu.pk</span>
</div><div class="t-ContextualInfo-item">
  <span class="t-ContextualInfo-label">DOB, CNIC & Blood Group</span>
  <span class="t-ContextualInfo-value">07-JUN-04<br>20 Years, 10 Months, 19 Days<br>71502-9324518-3<br></span>
</div><div class="t-ContextualInfo-item">
  <span class="t-ContextualInfo-label">Permanent Address</span>
  <span class="t-ContextualInfo-value">H9 prime garden, east garden karachi near diamond super market east garden karachi</span>
</div><div class="t-ContextualInfo-item">
  <span class="t-ContextualInfo-label">Admission Status</span>
  <span class="t-ContextualInfo-value">Verified</span>
</div>"""
                profile_data = self.parse_contextual_info_html(sample_html)
                logger.info("Using sample profile data for development")
            
            # Create the response with all collected data
            response = {
                "status": "success",
                "profile_data": profile_data,
                "current_url": current_url
            }
            
            # Include HTML only if we couldn't extract structured data
            if not profile_data or len(profile_data) < 3:
                response["html"] = page_html
                logger.warning("Including HTML in response due to limited structured data extraction")
            
            return response
            
        except Exception as e:
            logger.error(f"Error scraping profile: {str(e)}")
            return {"status": "error", "message": f"An error occurred while scraping profile: {str(e)}"}
    
    def close(self):
        """Close the WebDriver and clean up resources."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.session_id = None
            logger.info("WebDriver closed")