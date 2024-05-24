import csv
import time
import getpass
import keyring
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException


def login_with_manual_security_check(username, password):
    driver = webdriver.Chrome()
    driver.get('https://www.linkedin.com/login')

    try:
        username_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
        username_field.send_keys(username)
        password_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password")))
        password_field.send_keys(password)

        password_field.send_keys(Keys.RETURN)

        # Wait until redirected to the main LinkedIn page
        WebDriverWait(driver, 300).until(EC.url_contains("linkedin.com/feed"))
        print("Login successful.")
        return driver
    except Exception as e:
        print("Error during login:", str(e))
        driver.quit()
        return None

def scroll_to_bottom(driver):
    # Scroll to the bottom of the page to ensure "Next" button becomes visible
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

def initiate_infinite_scroll(driver):
    SCROLL_PAUSE_TIME = 2

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def get_pagination_info_and_click_next_page(driver):
    try:
        # Wait for pagination element to be present
        pagination = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'artdeco-pagination__pages--number'))
        )

        # Get current page number
        current_page = pagination.find_element(By.CSS_SELECTOR, '.artdeco-pagination__indicator--number.active.selected').text.strip()

        # Get total pages number
        total_pages_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//button[@aria-label="Page 100"]/span'))
        )
        total_pages = total_pages_element.text.strip()

        # Calculate pages left
        pages_left = int(total_pages) - int(current_page)

        # Scroll to bottom before attempting to click "Next" button
        scroll_to_bottom(driver)

        # Click next page button if available
        try:
            next_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Next"]'))
            )
            next_button.click()
            time.sleep(2)  # Wait for the next page to load
            initiate_infinite_scroll(driver)  # Initiate infinite scroll
        except TimeoutException:
            print("Next page button not clickable within timeout.")

        return {
            "current_page": current_page,
            "total_pages": total_pages,
            "pages_left": pages_left
        }
    except TimeoutException:
        print("Pagination info not found within timeout.")
        return None




def generate_email(first_name, last_name, domain='@att.com'):
    # Format the email address using the provided first and last names
    return f"{first_name.lower()}.{last_name.lower()}@{domain}"
    



def scrape_linkedin(driver, url, filename, domain='att.com'):
    driver.get(url)
    time.sleep(2)  # Let the page load

    try:
        while True:
            names = []  # Reset names list for each page
            occupations = []  # Reset occupations list for each page
            profile_links = []  # Reset profile links list for each page
            first_names = []  # Reset first names list for each page
            last_names = []  # Reset last names list for each page
            emails = []  # Reset emails list for each page

            # Find all profile containers
            profile_containers = driver.find_elements(By.CLASS_NAME, 'reusable-search__result-container')

            print("Number of profile containers found:", len(profile_containers))  # Debug print

            for container in profile_containers:
                try:
                    # Find the element containing the name information
                    name_element = container.find_element(By.XPATH, './/span[contains(@class, "entity-result__title-text")]')
                    # Get the text content of the name element and remove leading/trailing whitespaces
                    name_string = name_element.text.strip()
                    print("Name string:", name_string)

                    # Split the name before '\n' and take the first part as the full name
                    full_name = name_string.split('\n')[0]

                    # Split the full name into first and last names at the first space
                    parts = full_name.split(' ', maxsplit=1)
                    lastnamepart = full_name.split(',', maxsplit=1)

                    # Initialize first name as 'Not found'
                    first_name = 'Not found'

                    # If there's a space, take the left part as the first name and the right part as the last name
                    if len(parts) == 2:
                        first_name = parts[0].strip()  # Get the first name
                        last_name = parts[1].strip()   # Get the last name
                        
                        if len(lastnamepart) > 1:  # Check if there's a comma in the name
                            # Split the left part at the last space and take it as the last name
                            last_name_parts = lastnamepart[0].strip().rsplit(' ', 1)
                            last_name = last_name_parts[-1].strip() if len(last_name_parts) > 1 else lastnamepart[0].strip()
                    else:
                        # If there are no spaces or commas, treat the entire name as the first name
                        first_name = full_name.strip()   # Take the entire name as the first name
                        last_name = 'Not found'          # Since there's no space or comma, mark last name as 'Not found'

                    # Append first and last names to their respective lists
                    first_names.append(first_name)
                    last_names.append(last_name)

                    # Extract the profile link
                    profile_link_element = container.find_element(By.XPATH, './/a[contains(@class, "app-aware-link")]')
                    profile_link = profile_link_element.get_attribute('href')
                    profile_links.append(profile_link)

                    # Generate email
                    email = generate_email(first_name, last_name, domain)
                    print("Generated email:", email)  # Debug print to check the generated email
                    emails.append(email)
                except NoSuchElementException:
                    # Handle the case where the name element or profile link element is not found
                    first_name = 'Not found'
                    last_name = 'Not found'
                    first_names.append(first_name)
                    last_names.append(last_name)
                    profile_links.append('Not found')
                    emails.append('Not found')

                try:
                    occupation_element = container.find_element(By.CLASS_NAME, 'entity-result__primary-subtitle').text.strip()
                    occupation = occupation_element if occupation_element else 'Not found'
                except NoSuchElementException:
                    occupation = 'Not found'

                occupations.append(occupation)

                # Append the extracted name to the names list
                names.append(full_name)

            # Debug print statements
            print("Occupations:", occupations)
            print("Profile Links:", profile_links)
            print("Names:", names)
            print("First Names:", first_names)
            print("Last Names:", last_names)
            print("Emails:", emails)  # Print the emails list for debugging

            # Write data to CSV after scraping from each page
            write_to_csv(names, occupations, profile_links, first_names, last_names, emails, filename)

            # Scroll to the bottom
            scroll_to_bottom(driver)

            # Check if there is a next page
            pagination_info = get_pagination_info_and_click_next_page(driver)
            if pagination_info is None or pagination_info['pages_left'] <= 0:
                print("No more pages left.")
                break
            else:
                print(f"Page {pagination_info['current_page']} out of {pagination_info['total_pages']}, {pagination_info['pages_left']} pages left.")
    except Exception as e:
        print("Error occurred while scraping LinkedIn:", str(e))

def write_to_csv(names, occupations, profile_links, first_names, last_names, emails, filename):
    try:
        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            for first_name, last_name, email, occupation, profile_link in zip(first_names, last_names, emails, occupations, profile_links):
                writer.writerow([first_name, last_name, email, occupation, profile_link])
        print("Data has been successfully written to", filename)
    except Exception as e:
        print("Error occurred while writing to CSV:", str(e))




def main():
    username = keyring.get_password("linkedin_scraper", "username")
    password = keyring.get_password("linkedin_scraper", "password")

    if not (username and password):
        username = input("Enter your LinkedIn username: ")
        password = getpass.getpass("Enter your LinkedIn password: ")
        remember = input("Do you want to save your credentials securely? (yes/no): ").lower()
        if remember == "yes":
            keyring.set_password("linkedin_scraper", "username", username)
            keyring.set_password("linkedin_scraper", "password", password)

    driver = login_with_manual_security_check(username, password)
    if not driver:
        return

    # Continue with LinkedIn scraping
    url = input("Enter LinkedIn search results URL: ")

    if not url.startswith("https://www.linkedin.com/search/results/"):
        print("Invalid LinkedIn search results URL.")
        driver.quit()
        return

    filename = input("Enter CSV filename to save data: ")

    scrape_linkedin(driver, url, filename)

    driver.quit()

if __name__ == "__main__":
    main()
