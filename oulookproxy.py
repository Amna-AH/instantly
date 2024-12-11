import threading
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
def handle_single_account(proxy, email, password):
    print(f"Handling account for {email} with proxy {proxy}")

    # Create a new driver with proxy for each thread
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
        

        # # Step 8: Check if "Use another account" option is available and click it
        # use_another_account_button = WebDriverWait(driver, 10).until(
        #     EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Use another account')]"))
        # )
        # use_another_account_button.click()
        # print("Clicked 'Use another account'.")
        # time.sleep(2)  # Wait for the next step to load after clicking

        # Step 9: Loop through the email and password list and log in to Outlook
        for i in range(len(emailList)):
            current_email = emailList[i]
            current_password = pswdList[i]

            print(f"Attempting to log in with: {current_email} / {current_password}")
            
            #email_input = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "i0ll6")))
            email_input = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "loginfmt")))
            email_input.clear()
            email_input.send_keys(current_email)  # Use the email from the list
            email_input.send_keys(Keys.RETURN)
            print(f"Entered email {email} and pressed 'Next'.")
            time.sleep(3)
            
            # Click the "Next" button to proceed
            next_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.ID, "idSIButton9"))  # "Next" button ID for Outlook
            )
            next_button.click()
            print("Clicked 'Next' button.")
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
            
            # Check for the "Accept" button and click if it appears
            accept_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.NAME, "idSIButton9")))
            accept_button.click()
            
            if accept_button:
                accept_button.click()
                print("Clicked on 'Accept' button.")
                time.sleep(3)
            else:
                print("No 'Accept' button found, moving on to the next step.")

                # Continue with the rest of your login logic
                print("Continuing with next steps...")
            
            

            # Step 9.5: Handle "Stay signed in?" prompt (if it appears)
            Yes_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Yes']")))
            Yes_button.click()
            print("Clicked 'Yes' ")
            time.sleep(3)
    

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

proxies = ['residential.pingproxies.com:8129:83137_BWvVe_c_us:8MIVlCsASz']

# Handle all accounts using proxies and threads
def handle_proxy_accounts(proxies, email_password_pairs):
    threads = []
    for i, (email, password) in enumerate(email_password_pairs):
        proxy = proxies[i % len(proxies)]  # Cycle through the proxies
        thread = threading.Thread(target=handle_single_account, args=(proxy, email, password))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

# Create a set to track emails that have already been processed
processed_emails = set()

# Read email and password from the CSV file
emailList = []
pswdList = []
with open('outlookaccounts.csv', mode='r', newline='') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        account = row['accounts']
        if '|' in account:
            email, password = account.split('|')
            emailList.append(email)
            pswdList.append(password)
            # Check if the email has already been processed
        if email not in processed_emails:
            emailList.append(email)
            pswdList.append(password)
            processed_emails.add(email)  # Mark this email as processed

# Combine email and password pairs
email_password_pairs = list(zip(emailList, pswdList))
print(f"Processed {len(email_password_pairs)} unique accounts.")

# Handle proxy accounts in batches (5 accounts per proxy)
for i, proxy in enumerate(proxies):
    start_index = i * 1
    end_index = start_index + 1
    batch = email_password_pairs[start_index:end_index]
    if batch:
        handle_proxy_accounts([proxy], batch)

print("All accounts processed.")