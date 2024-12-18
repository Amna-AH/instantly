import time
import os
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import json
import requests
import threading

# Instantly API Key (Replace this with your actual API key)
api_key = '5teaj69ednmbepp7148cwe2ya4gf'

# Function to authenticate using Instantly API (check if account exists)
def authenticate_instantly_account_via_api(email, password):
    url = "https://api.instantly.ai/api/v1/authenticate?api_key=5teaj69ednmbepp7148cwe2ya4gf"  # Replace with correct API endpoint
    
    data = {
        'email': email,
        'password': password,
        'api_key': api_key
    }

    response = requests.post(url, data=data)

    if response.status_code == 200:
        print(f"Account authenticated successfully for {email}")
        return response.json()  # Return authentication data
    else:
        print(f"Failed to authenticate account for {email}: {response.text}")
        return None
    
def check_account_status(email, api_key):
    url = "https://api.instantly.ai/api/v1/account/status"
    
    # Payload with the email and API key
    payload = json.dumps({
        "api_key": api_key,
        "accounts": [email]
    })
    
    # Headers to specify the content type
    headers = {
        'Content-Type': 'application/json'
    }
    
    # Sending the POST request
    response = requests.post(url, headers=headers, data=payload)
    
    # Check the status code and handle accordingly
    if response.status_code == 200:
        print(f"Account for {email} connected successfully.")
        return response.json()  # Optionally process the JSON response
    elif response.status_code == 400:
        print(f"Failed to connect account for {email}. Error: {response.text}")
        return None
    else:
        print(f"Unexpected error for {email}: {response.status_code}, Response: {response.text}")
        return None


# Function to create a Chrome driver with proxy
def create_driver_with_proxy(proxy):
    chrome_options = Options()
    # Directory setup for Chrome extension
    extension_path = './proxy_auth_plugin'
    os.makedirs(extension_path, exist_ok=True)

    # Check if the proxy contains authentication information (username:password@host:port)
    try:
        # Split the proxy into the host, port, username, and password
        proxy_parts = proxy.split(':')
        
        # The proxy string is expected to have 4 parts: host, port, username, and password
        if len(proxy_parts) == 4:
            proxy_host = proxy_parts[0]
            proxy_port = proxy_parts[1]
            username = proxy_parts[2]
            password = proxy_parts[3]
        else:
            # If the format doesn't match, handle it as a basic host:port proxy without authentication
            proxy_host = proxy_parts[0]
            proxy_port = proxy_parts[1]
            username = None
            password = None

    except Exception as e:
        print(f"Error parsing proxy {proxy}: {e}")
        return None

    # Manifest JSON for the Chrome extension
    manifest_json = '''
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    '''

    # JavaScript for handling proxy authentication (only if credentials are provided)
    if username and password:
        background_js = f'''
        var config = {{
                mode: "fixed_servers",
                rules: {{
                  singleProxy: {{
                    scheme: "http",
                    host: "{proxy_host}",
                    port: parseInt({proxy_port})
                  }},
                  bypassList: ["localhost"]
                }}
              }}; 

        chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

        function callbackFn(details) {{
            return {{
                authCredentials: {{
                    username: "{username}",
                    password: "{password}"
                }}
            }};
        }}

        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {{urls: ["<all_urls>"]}},
                    ['blocking']
        );
        '''
    else:
        # No authentication required
        background_js = f'''
        var config = {{
                mode: "fixed_servers",
                rules: {{
                  singleProxy: {{
                    scheme: "http",
                    host: "{proxy_host}",
                    port: parseInt({proxy_port})
                  }},
                  bypassList: ["localhost"]
                }}
              }};  

        chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});  
        '''

    # Write the manifest and background JS to files
    with open(os.path.join(extension_path, 'manifest.json'), 'w') as f:
        f.write(manifest_json)
    with open(os.path.join(extension_path, 'background.js'), 'w') as f:
        f.write(background_js)

    # Set Chrome options to load the proxy extension
    chrome_options.add_argument(f'--load-extension={os.path.abspath(extension_path)}')

    # Optional: Set up additional proxy arguments if you need to use the proxy for requests
    chrome_options.add_argument(f'--proxy-server=http://{proxy_host}:{proxy_port}')
    
    # Set path to ChromeDriver in the Service object (adjust your chromedriver path here)
    service = Service('chromeDriver131/chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.maximize_window()

    return driver

# Function to handle a single account login with proxy
def handle_account(proxy, email, password):
    print(f"Handling account for {email} with proxy {proxy}")
    
    # Step 1: Authenticate account via Instantly API (to skip email verification)
    authenticate_response = authenticate_instantly_account_via_api(email, password)
    if not authenticate_response:
        print(f"Failed to authenticate account for {email}. Skipping...")
        return

    # Step 2: Create a new driver with proxy for each thread
    driver = create_driver_with_proxy(proxy)
    
    try:
        # Step 1: Open the login page
        driver.get("https://app.instantly.ai/auth/login")
        time.sleep(5)  # Allow page to load
                
        # Step 2: Enter email
        wait = WebDriverWait(driver, 10)
        email_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='email']")))
        email_input.clear()
        email_input.send_keys("mianfaizan@voltic.agency")  # Use the passed email argument
        email_input.send_keys(Keys.TAB)  # Move focus to trigger validation
        print(f"Entered email: {email}")
        time.sleep(2)
                
        # Optional: Check for error messages after entering email
        error_messages = driver.find_elements(By.CSS_SELECTOR, ".error-message-selector")  # Adjust selector as needed
        for message in error_messages:
            print(f"Error message on page: {message.text}")
                    
        # Step 3: Enter password
        password_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='password']")))
        password_input.clear()
        password_input.send_keys("Faizan1888")  # Use the passed password argument
        print(f"Entered password.")
        time.sleep(2)
                
        # Step 4: Click "Log In" button
        log_in_button = driver.find_element(By.XPATH, "/html/body/div[1]/section/div[2]/div/div/div[2]/div/div/form/div/div[2]/div/button")
        log_in_button.click()
        print(f"Clicked on 'Log In' button.")
        time.sleep(3)  # Wait for the page to load after login
        WebDriverWait(driver, 30).until(lambda driver: driver.execute_script("return document.readyState") == "complete")
                
        # # Step 5: Wait until the specific anchor element with class 'CampaignEditor_actionButton__FziHQ' is present and clickable
        time.sleep(15)
        # Wait for the specific element to become clickable
        WebDriverWait(driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH, "(//a[@class='CampaignEditor_actionButton__FziHQ'])[1] ")))
        Add_new_button = wait.until(EC.element_to_be_clickable((By.XPATH, "(//span[contains(.,'Add new')])[1]")))
        # Perform the click using JavaScript once it's clickable
        driver.execute_script("arguments[0].click();", Add_new_button)
        print("Clicked on 'Add new' button")
        time.sleep(5)  # Add a delay after clicking
        # Exit the loop after successfully clicking
        print("Waiting for 'Add new' button to become clickable...")
        time.sleep(1)  # Wait briefly before retrying
                
        # Step 6: Wait until the "Office 365 / Outlook" button is clickable and then click it
        try:
            # Wait for the 'Office 365 / Outlook' button to be clickable
            Google_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
            (By.XPATH, "/html/body/div[1]/div[2]/div/div/div/div[3]/div[2]/div[2]/div[2]/div[2]/h6"))
            )
            Google_button.click()
            print("Clicked on 'Office 365 / Outlook' button")
            time.sleep(3)  # Wait for the next page to load after clicking
        except Exception as e:
                print(f"Error clicking on 'Office 365 / Outlook' button: {e}")
                    
        # Step 7: Click on "Yes, SMTP has been enabled"
        SMTP_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Yes, SMTP has been enabled')]")))
        SMTP_button.click()
        print("Clicked on 'Yes, SMTP has been enabled' button")
        # time.sleep(50)
                
        windows = driver.window_handles
        if len(windows) > 1:
            driver.switch_to.window(windows[1])  # Switch to the newly opened window
            print("Switched to the new browser window for sign-in.")
        else:
            print("New browser window not found.")
                
        # Step 9: Loop through the email and password list and log in to Outlook
        for i in range(len(emailList)):
            current_email = emailList[i]
            current_password = pswdList[i]
            print(f"Attempting to log in with: {current_email} / {current_password}")
                    
            email_input = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME, "loginfmt")))
            email_input.clear()
            email_input.send_keys(current_email)  # Use the email from the list
            email_input.send_keys(Keys.RETURN)
            print(f"Entered email {email} and pressed 'Next'.")
            time.sleep(3)
                    
            # Step 9.4: Enter the password in the new window
            password_input = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.NAME, "passwd"))  # Match the password field's name
                )
            password_input.clear()
            password_input.send_keys(current_password)
            print(f"Entered password for: {current_email}")
            
            # Click the "Sign In" button
            sign_in_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.ID, "idSIButton9"))  # "Sign In" button ID
                )
            sign_in_button.click()
            print("Clicked 'Sign In' button.")
            time.sleep(3)
                        
            try:
                # Check for the "Accept" button and click if it appears
                accept_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.NAME, "idSIButton9")))
                accept_button.click()
                        
                if accept_button:
                    accept_button.click()
                    print("Clicked on 'Accept' button.")
                    time.sleep(3)
                else:
                        print("No 'Accept' button found, moving on to the next step.")
            except Exception as e:
                        # Continue with the rest of your login logic
                        print("Continuing with next steps...")
                        
                        
            # Step 9.5: Handle "Stay signed in?" prompt (if it appears)
            button_xpath = "//*[@id='idSIButton9']"
            driver.execute_script(f"document.evaluate(\"{button_xpath}\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click();")

                        

            # Step 9.6: Close the new browser window and switch back to the main window
            #driver.close()
            WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(1))  # Wait until only one window remains
            driver.switch_to.window(windows[0])
            print("Closed the new window and switched back to the main window.")
                        
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "(//a[@class='CampaignEditor_actionButton__FziHQ'])[1] ")))
            print("Account displayed on the dashboard.")
                    
            # Loop through the list of emails and check each account status
            for email in emailList:
                status = check_account_status(email, api_key)
                print(status)

    except Exception as e:
        print(f"Error with {email}: {e}")
    
proxies = ['residential.pingproxies.com:8129:83137_BWvVe_c_us:8MIVlCsASz']

# Handle all accounts using proxies and threads with API integration
def handle_proxy_accounts_with_api(proxies, email_password_pairs):
    threads = []
    for i, (email, password) in enumerate(email_password_pairs):
        proxy = proxies[i % len(proxies)]  # Cycle through the proxies
        thread = threading.Thread(target=handle_account, args=(proxy, email, password))
        threads.append(thread)
        thread.start()
 
    for thread in threads:
        thread.join()
        
# Create a set to track emails that have already been processed
processed_emails = set()
processed_emails_lock = threading.Lock()
 
# Read email and password from the CSV file
emailList = []
pswdList = []
with open('outlookaccounts.csv', mode='r', newline='') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        account = row['accounts']
        if '|' in account:
            email, password = account.split('|')
            # Check if the email has already been processed
            if email not in processed_emails:
                emailList.append(email)
                pswdList.append(password)
                processed_emails.add(email)  # Mark this email as processed
 
#Combine email and password pairs
email_password_pairs = list(zip(emailList, pswdList))
print(f"Processed {len(email_password_pairs)} unique accounts.")
 
# Handle proxy accounts in batches (5 accounts per proxy)
batch_size = 3  # You can adjust this
for i, proxy in enumerate(proxies):
    start_index = i * batch_size
    end_index = min(start_index + batch_size, len(email_password_pairs))  # Ensure we don't exceed the list length
    batch = email_password_pairs[start_index:end_index]
    if batch:
        handle_proxy_accounts_with_api([proxy], batch)
 
print("All accounts processed.")