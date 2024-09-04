from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import re
import yaml

# Load configuration from YAML file
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

myits_username = config['myits']['username']
myits_password = config['myits']['password']
google_form_url = config['google_form']['url']

# Initialize WebDriver
driver = webdriver.Chrome()  # Adjust the path to ChromeDriver if needed

try:
    # Open the myITS Internet page
    driver.get("https://myits-app.its.ac.id/internet/index.php")

    # Wait for the "Akses Internet Personal" button to appear and click it
    akses_internet_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.LINK_TEXT, "Akses Internet Personal"))
    )
    akses_internet_button.click()

    # Enter myITS ID
    myits_id_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "username"))  # Adjust the ID of the input field if necessary
    )
    myits_id_input.send_keys(myits_username)
    myits_id_input.send_keys(Keys.RETURN)

    # Enter password
    password_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "password"))  # Adjust the ID of the input field if necessary
    )
    password_input.send_keys(myits_password)
    password_input.send_keys(Keys.RETURN)

    # Find the text containing "Diakses dari" and extract the IP Address from it
    signature_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Diakses dari')]"))
    )
    signature_text = signature_element.text

    # Extract IP Address from the text
    ip_match = re.search(r'Diakses dari ([\d\.]+)', signature_text)
    if ip_match:
        ip_address = ip_match.group(1)
        print(f"Your IP Address: {ip_address}")
    else:
        print("Failed to find IP Address.")
        driver.quit()
        exit()

    print("Internet access has been enabled.")

    # Open Google Form
    driver.get(google_form_url)

    try:
        # Wait for the input field to appear and ensure it is visible
        ip_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='text']"))
        )

        # Scroll the input field into view if necessary
        driver.execute_script("arguments[0].scrollIntoView();", ip_input)

        # Use JavaScript to set the value and ensure the value is set
        driver.execute_script("arguments[0].value = arguments[1];", ip_input, ip_address)
        print("Input field value set to:", ip_input.get_attribute('value'))  # Debug value set

        # Trigger input and change events if needed
        driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", ip_input)
        driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", ip_input)

        # Wait for the submit button to appear and click it
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Kirim']"))
        )
        submit_button.click()

        print("Form has been successfully submitted.")

    except TimeoutException:
        print("Failed to complete form submission, timeout.")

finally:
    # Close the browser
    time.sleep(5)
    driver.quit()
