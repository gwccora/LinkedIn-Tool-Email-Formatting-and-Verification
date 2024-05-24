import csv
import shutil
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

def verify_emails_with_google(csv_filename):
    # Set the path to the Chrome webdriver executable
    chrome_driver_path = r"C:\Users\coram\OneDrive\Desktop\chromedriver_win32\chromedriver.exe"  # Replace with actual path to chromedriver.exe
    
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(executable_path=chrome_driver_path, options=options)

    try:
        # Copy the CSV file to create a new file for storing verification results
        verification_filename = csv_filename.replace(".csv", "_verification.csv")
        shutil.copyfile(csv_filename, verification_filename)

        # Open the CSV file and read the emails, starting from the first row
        with open(csv_filename, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            with open(verification_filename, 'w', newline='', encoding='utf-8') as result_file:
                writer = csv.writer(result_file)
                for row in reader:
                    email = row[2]  # Assuming the email is in the third column (index 2)

                    # Perform Google search for the email
                    driver.get("https://www.google.com")
                    search_box = driver.find_element(By.NAME, "q")
                    search_box.send_keys(email)
                    search_box.send_keys(Keys.RETURN)
                    time.sleep(2)  # Let the search results load

                    # Check if the security check page is displayed
                    if "sorry/index" in driver.current_url:
                        print("Manual security check required for:", email)
                        input("Press Enter to continue after verification...")
                        # Refresh the page after the manual verification
                        driver.refresh()
                        time.sleep(2)  # Wait for the page to load after refresh

                    # Extract URLs from the search results
                    search_results = driver.find_elements(By.CSS_SELECTOR, "div.tF2Cxc a")
                    google_urls = [result.get_attribute("href") for result in search_results]

                    # Compare the first three Google search results with the email domain
                    verification_result = "Yes" if any("linkedin.com" in url for url in google_urls[:3]) else "No"
                    print(f"Email: {email}, Verification: {verification_result}")

                    # Add the verification result to the row and write it to the new CSV file
                    row.append(verification_result)
                    writer.writerow(row)

    except Exception as e:
        print("Error occurred:", str(e))
    
    finally:
        # Close the webdriver
        driver.quit()

csv_filename = "attemaillist.csv"
verify_emails_with_google(csv_filename)
