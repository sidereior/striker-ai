from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

# Start the Selenium WebDriver
driver = webdriver.Chrome()

# Function to save the current page as HTML
def save_html(division, week):
    # Get the current directory of the script
    current_directory = os.getcwd()
    # Set the subdirectory to '/inputs'
    subdirectory = 'inputs'
    # Create the subdirectory if it doesn't exist
    os.makedirs(os.path.join(current_directory, subdirectory), exist_ok=True)
    # Set the file name
    if division == "1":
        file_name = f"d1-week{week}.txt"
    elif division == "2":
        file_name = f"d2-week{week}.txt"
    elif division == "3":
        file_name = f"d3-week{week}.txt"
    elif division == "4":
        file_name = f"naia-week{week}.txt"
    elif division == "5":
        file_name = f"njcaa-week{week}.txt"

    # Combine everything to get the full file path
    file_path = os.path.join(current_directory, subdirectory, file_name)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(driver.page_source)
    print(f"Saved HTML for Division {division} Week {week}")

# Function to select an option from a dropdown when it is present
def select_option_from_dropdown(dropdown_id, option_value):
    dropdown_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, dropdown_id))
    )
    select = Select(dropdown_element)
    select.select_by_value(option_value)
    # If the dropdown automatically submits the form on change, the next line is not needed
    driver.find_element(By.ID, dropdown_id).submit()

try:
    # Navigate to the website
    driver.get("https://www.topdrawersoccer.com/college-soccer/college-scoreboard/women")

    # Define divisions by the values in the dropdown
    division_values = ["1", "2", "3", "4", "5"]  # These values correspond to DI, DII, DIII, NAIA, NJCAA
    for division_value in division_values:
        # Select the division from the dropdown
        select_option_from_dropdown("divisionId", division_value)

        save_html(division_value, 13)

finally:
    # Close the WebDriver
    driver.quit()
