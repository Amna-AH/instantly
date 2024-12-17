import threading
import time
import os
import csv
import requests
import multiprocessing
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

#integrate gmail accounts in instantly.ai 

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

# Function to handle a single account login with proxy and API integration
def handle_single_account_with_api(proxy, email, password):
    print(f"Handling account for {email} with proxy {proxy}")

    # Step 1: Authenticate account via Instantly API (to skip email verification)
    authenticate_response = authenticate_instantly_account_via_api(email, password)
    if not authenticate_response:
        print(f"Failed to authenticate account for {email}. Skipping...")
        return

    # Step 2: Create a new driver with proxy for Selenium
    driver = create_driver_with_proxy(proxy)
    
    try:
        # driver = create_driver_with_proxy(proxy)
        
        # Login logic for each account
        driver.get("https://app.instantly.ai/auth/login")
        time.sleep(5)

        # Step 1: Enter email
        wait = WebDriverWait(driver, 10)
        email_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='email']")))
        email_input.clear()
        email_input.send_keys("mianfaizan@voltic.agency")
        email_input.send_keys(Keys.TAB)  # Move focus to trigger validation
        print(f"Entered email {email}")
        time.sleep(2)

        # Step 2: Enter password
        password_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='password']")))
        password_input.clear()
        password_input.send_keys("Faizan1888")
        print(f"Entered password for {email}")
        time.sleep(2)

        # Step 3: Click the "Log In" button
        log_in_button = driver.find_element(By.XPATH, "/html/body/div[1]/section/div[2]/div/div/div[2]/div/div/form/div/div[2]/div/button")
        log_in_button.click()
        print(f"Clicked on 'Log In' button for {email}")
        time.sleep(3)

        # Step 4: Wait until the specific anchor element with class 'CampaignEditor_actionButton__FziHQ' is present and clickable
        
        time.sleep(15)
              # Wait for the specific element to become clickable
        # WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "(//a[@class='CampaignEditor_actionButton__FziHQ'])[1] ")))
        WebDriverWait(driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH, "(//a[@class='CampaignEditor_actionButton__FziHQ'])[1] ")))
        Add_new_button = wait.until(EC.element_to_be_clickable((By.XPATH, "(//span[contains(.,'Add new')])[1]")))

              # Perform the click using JavaScript once it's clickable
        driver.execute_script("arguments[0].click();", Add_new_button)
        print("Clicked on 'Add new' button")
        time.sleep(5)  # Add a delay after clicking
               # Exit the loop after successfully clicking

            
        print("Waiting for 'Add new' button to become clickable...")
        time.sleep(1)  # Wait briefly before retrying

        # Step 5: Click on "Google Gmail / G-Suite"
        Google_button = wait.until(EC.element_to_be_clickable((By.XPATH, "(//h6[text()='Gmail / G-Suite']/parent::div)[2]")))
        Google_button.click()
        print("Clicked on 'Google Gmail / G-Suite' button")
        time.sleep(3)

        # Step 6: Click on "Yes, IMAP has been enabled"
        IMAP_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Yes, IMAP has been enabled')]")))
        IMAP_button.click()
        print("Clicked on 'Yes, IMAP has been enabled' button")
        time.sleep(3)

        # Step 7: Click on "OAuth"
        oauth_button = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[2]/div/div[3]/div[1]/button")))
        oauth_button.click()
        print("Clicked on 'OAuth' button")
        time.sleep(3)

        # Step 8: Click on "Login" button
        log_in_button = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/div[3]/div/div/button/h6")
        log_in_button.click()
        print("Clicked on 'Log In' button.")
        time.sleep(3)

        # Step 9: Switch to Gmail login window if opened
        windows = driver.window_handles
        if len(windows) > 1:
            driver.switch_to.window(windows[1])
            print("Switched to the Gmail login window.")
            email_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "identifierId")))
            email_input.clear()
            email_input.send_keys(email)  # Use the email from the list
            email_input.send_keys(Keys.RETURN)
            print(f"Entered email {email} and pressed 'Next'.")
            time.sleep(3)

            # Step 9b: Enter the Gmail password
            password_input = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.NAME, "Passwd")))
            password_input.clear()
            password_input.send_keys(password)
            print(f"Entered password for Gmail: {password}")
            time.sleep(2)

            # Click 'Next' button
            password_next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@id='passwordNext']//button")))
            password_next_button.click()
            print("Clicked 'Next' after entering password.")
            time.sleep(3)

            # Handle "I Understand" button
            
            # when the account is new it will ask for this 
            try:
                i_understand_button = WebDriverWait(driver, 10).until( EC.element_to_be_clickable((By.NAME, "confirm")))
                i_understand_button.click()
                print("Clicked 'I Understand' button.")
            except:
                print("not present")
           
            
            # Wait for the 'Continue' button to be clickable
            continue_button = WebDriverWait(driver, 10).until( EC.element_to_be_clickable((By.XPATH, "//button/span[text()='Continue']")))
            continue_button.click()
            print("Clicked 'Continue' button.")
            
            

            # Click 'Allow'
            allow_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Allow')]")))
            allow_button.click()
            print("Clicked 'Allow' to give access.")
            
    
            
            # Step 9.6: Close the new browser window and switch back to the main window
            #driver.close()
            WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(1))  # Wait until only one window remains
            driver.switch_to.window(windows[0])
            print("Closed the new window and switched back to the main window.")
            
            back_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/header/div/div/div/div/span/h6 ")))
            back_button.click()
            print("Clicked the 'Back' button.")
            
            WebDriverWait(driver, 20).until(EC.visibility_of_any_elements_located((By.XPATH, "(//a[@class='CampaignEditor_actionButton__FziHQ'])[1] ")))
            print("Account displayed on the dashboard.")


    except Exception as e:
        print(f"Error with {email}: {e}")
    finally:
        driver.quit()

proxies = ['residential.pingproxies.com:8193:83137_BWvVe_c_us:8MIVlCsASz']  # Add more proxies here
 
# Handle all accounts using proxies and threads with API integration
def handle_proxy_accounts_with_api(proxies, email_password_pairs):
    threads = []
    for i, (email, password) in enumerate(email_password_pairs):
        proxy = proxies[i % len(proxies)]  # Cycle through the proxies
        thread = threading.Thread(target=handle_single_account_with_api, args=(proxy, email, password))
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
with open('gmailaccounts.csv', mode='r', newline='') as file:
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
