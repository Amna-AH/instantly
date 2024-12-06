import threading
import time
import os
import csv
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException


# Instantly API Key (Replace this with your actual API key)
api_key = '5teaj69ednmbepp7148cwe2ya4gf'

# Example function to authenticate using Instantly API (check if account exists)
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
    
    
# Function to create a Chrome driver with proxy
def create_driver_with_proxy(proxy):
    chrome_options = Options()
    # Directory setup for Chrome extension
    extension_path = './proxy_auth_plugin'
    os.makedirs(extension_path, exist_ok=True)

    # Proxy Format: username:password@host:port
    proxy_details = proxy.split('@')
    credentials = proxy_details[0].split(':')
    proxy_host = proxy_details[1].split(':')[0]
    proxy_port = proxy_details[1].split(':')[1]

    username = credentials[0]
    password = credentials[1]

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

    # JavaScript for handling proxy authentication
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

    with open(os.path.join(extension_path, 'manifest.json'), 'w') as f:
        f.write(manifest_json)
    with open(os.path.join(extension_path, 'background.js'), 'w') as f:
        f.write(background_js)

    # Load the Chrome extension
    chrome_options.add_argument(f'--load-extension={os.path.abspath(extension_path)}')

    # Set path to ChromeDriver in the Service object
    service = Service('chromeDriver131/chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.maximize_window()
    return driver

proxies = ['a0eb0153016a00854c80__cr.us:5e4ccc95cab4dd89@gw.dataimpulse.com:823',

# 'a0eb0153016a00854c80__cr.us:5e4ccc95cab4dd89@gw.dataimpulse.com:823',

# 'a0eb0153016a00854c80__cr.us:5e4ccc95cab4dd89@gw.dataimpulse.com:823',
 
# 'a0eb0153016a00854c80__cr.us:5e4ccc95cab4dd89@gw.dataimpulse.com:823',

# 'a0eb0153016a00854c80__cr.us:5e4ccc95cab4dd89@gw.dataimpulse.com:823',

# 'a0eb0153016a00854c80__cr.us:5e4ccc95cab4dd89@gw.dataimpulse.com:823'
]



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
        while True:
            try:
              time.sleep(15)
              # Wait for the specific element to become clickable
              WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "(//a[@class='CampaignEditor_actionButton__FziHQ'])[1] ")))
              Add_new_button = wait.until(EC.element_to_be_clickable((By.XPATH, "(//span[contains(.,'Add new')])[1]")))
        
              # Perform the click using JavaScript once it's clickable
              driver.execute_script("arguments[0].click();", Add_new_button)
              print("Clicked on 'Add new' button")
              time.sleep(5)  # Add a delay after clicking
              break  # Exit the loop after successfully clicking

            except Exception as e:
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
            i_understand_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'I Understand')]")))
            i_understand_button.click()
            print("Clicked 'I Understand' button.")
            
            # # Handle "I Understand" button
            # i_understand_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[@id='confirm']")))
            # i_understand_button.click()
            # print("Clicked 'I Understand' button.")
            
            # Click 'Continue'
            continue_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Continue')]")))
            continue_button.click()
            print("Clicked 'Continue' button to allow access.")

            # Click 'Allow'
            allow_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Allow')]")))
            allow_button.click()
            print("Clicked 'Allow' to give access.")

    except Exception as e:
        print(f"Error with {email}: {e}")
    finally:
        driver.quit()

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

# Read email and password from the CSV file
emailList = []
pswdList = []
with open('gmailaccounts.csv', mode='r', newline='') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        account = row['accounts']
        if '|' in account:
            email, password = account.split('|')
            emailList.append(email)
            pswdList.append(password)

# Combine email and password pairs
email_password_pairs = list(zip(emailList, pswdList))

# Handle proxy accounts in batches (5 accounts per proxy)
for i, proxy in enumerate(proxies):
    start_index = i * 1
    end_index = start_index + 1
    batch = email_password_pairs[start_index:end_index]
    if batch:
        handle_proxy_accounts_with_api([proxy], batch)

print("All accounts processed.")
