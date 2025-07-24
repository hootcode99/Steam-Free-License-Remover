from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import logging

# Constants
BATCH_SIZE = 10 

# Webdriver Setup
logging.getLogger("selenium").setLevel(logging.CRITICAL)
chrome_options = Options()
chrome_options.add_argument("--disable-logging")
chrome_options.add_argument("--log-level=3")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome(service=Service(log_path="nul"), options=chrome_options)
driver.get("https://store.steampowered.com/account/licenses/")
time.sleep(2)

# Wait for Login
print("Waiting for login to complete...")
login_present = driver.find_elements(By.XPATH, "//div[text()='Password']")
while login_present:
    time.sleep(3)
    login_present = driver.find_elements(By.XPATH, "//div[text()='Password']")
print("Login detected, proceeding...")

# Count Free Licenses
print("Searching for free licenses to remove...")
license_remove_links = driver.find_elements(By.XPATH, "//a[starts-with(@href, 'javascript:RemoveFreeLicense')]")
initial_total = len(license_remove_links)
time.sleep(1)

# Remove Free Licenses
if initial_total == 0:
    print("Sorry, no free licenses found to remove. Make sure you are logged in to your Steam account.")
    print("Exiting script")
    time.sleep(5)
else: 
    try:
        removed_total = 0
        removed_batch_count = 0
        total_batch_count = initial_total // BATCH_SIZE + (1 if initial_total % BATCH_SIZE > 0 else 0)
        print(f"Found {initial_total} free licenses to remove. {total_batch_count} batches to remove.")

        while len(license_remove_links) > 0:
            # Get the next batch of remove links
            current_batch = [link.get_attribute("href") for link in license_remove_links[:BATCH_SIZE]]
            for reference in current_batch:
                # Click the remove link
                remove_link = driver.find_element(By.XPATH, f'//a[@href="{reference}"]')
                remove_link.click()
                time.sleep(1)

                # Find and click confirmation button
                confirm_button = driver.find_element(By.XPATH, "//div[contains(@class, 'btn_green_steamui') and .//span[text()='OK']]")
                if confirm_button:
                    confirm_button.click()
                    removed_total += 1
                time.sleep(1)
            
            # Wait 10 minutes to avoid Steam's rate limiting (or finish if no more licenses)
            removed_batch_count += 1
            print(f"Batch ({removed_batch_count}/{total_batch_count}) Complete.") 
            if removed_batch_count == total_batch_count:
                break
            else:
                print("Waiting for 10 minutes before next batch...")
                for i in range(10, 0, -1):
                    print(f"{i} minutes remaining...", end="\r")
                    time.sleep(120)
                license_remove_links = driver.find_elements(By.XPATH, "//a[starts-with(@href, 'javascript:RemoveFreeLicense')]")

        print("Completed removing licenses.")
        print(f"Removed {removed_total} out of {initial_total} free licenses in {removed_batch_count} batches.")
        print("Exiting script.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

driver.quit()
