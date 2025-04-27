import requests
from bs4 import BeautifulSoup
import json

# For debugging purposes
def debug_login():
    try:
        # First, get the login page to retrieve any necessary cookies or tokens
        login_url = "http://lms.induscms.com:81/ords/r/erasoft/student-app1400450/login"
        session = requests.Session()
        response = session.get(login_url)
        
        print(f"Initial GET response status: {response.status_code}")
        print(f"Initial cookies: {session.cookies.get_dict()}")
        
        # Parse the HTML to find any hidden form fields if needed
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Print all form fields to see what's available
        print("\nForm fields found:")
        for form in soup.find_all('form'):
            print(f"Form action: {form.get('action')}")
            print(f"Form method: {form.get('method')}")
            for input_tag in form.find_all(['input', 'button']):
                print(f"  {input_tag.get('name', 'No name')}: {input_tag.get('value', 'No value')} (type: {input_tag.get('type', 'No type')})")
        
        # Prepare login data with test credentials
        # Note: Using dummy credentials for debugging
        login_data = {
            'P9999_USERNAME': 'test_user',
            'P9999_PASSWORD': 'test_password',
            'p_request': 'LOGIN'
        }
        
        # Find any additional form fields that might be required
        for input_tag in soup.find_all('input', type='hidden'):
            if input_tag.get('name') and input_tag.get('value'):
                login_data[input_tag['name']] = input_tag['value']
                print(f"Added hidden field: {input_tag['name']} = {input_tag['value']}")
        
        print(f"\nFinal login data: {login_data}")
        
        # Submit the login form
        print("\nSubmitting login form...")
        response = session.post(login_url, data=login_data, allow_redirects=True)
        
        print(f"POST response status: {response.status_code}")
        print(f"Final URL: {response.url}")
        print(f"Final cookies: {session.cookies.get_dict()}")
        
        # Print response headers to see if there are any redirects or other clues
        print("\nResponse headers:")
        for header, value in response.headers.items():
            print(f"{header}: {value}")
        
        # Check if we can find any session information in the response
        print("\nLooking for session information in response...")
        if "session" in response.text.lower():
            print("Found 'session' in response text")
        
        # Print a small part of the response text to see what we're getting
        print("\nResponse preview:")
        print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
        
    except Exception as e:
        print(f"Error during debugging: {str(e)}")

# Run the debug function
debug_login()