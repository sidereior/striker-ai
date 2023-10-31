import re
from lxml import html
import pandas as pd
import os
import logging
from datetime import datetime

# Define a unique batch ID based on the current date and time
batch_id = datetime.now().strftime("%Y%m%d_%H%M%S")

# Setting up the log directory
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)

# Setting up logging
log_filename = f'logs/processing_batch_{batch_id}.log'
logging.basicConfig(filename=log_filename, level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

# Define a function to clean text data
def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

# Define a function to extract the conference information from the string
def extract_conference(info_string):
    # Remove all non-alphabetic characters from the beginning of the string
    conference = re.sub(r'^[^a-zA-Z]*', '', info_string)
    return conference

# Define a function to process a single week
def process_week(week_number):
    # Load the HTML content from the text file
    file_path = f'inputs/week{week_number}.txt'
    if not os.path.exists(file_path):
        logging.warning(f"File not found: {file_path}")
        return
    
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Parse the HTML content
    tree = html.fromstring(html_content)

    # Locate the element with the specified XPath
    list_table_view = tree.xpath('//*[@id="listTableView"]')
    if not list_table_view:
        logging.warning(f"Element with id 'listTableView' not found in {file_path}")
        return

    # Initialize a list to store the extracted data
    data = []

    # Loop through the rows and extract data
    rows = list_table_view[0].xpath('.//tr')
    for row in rows:
        # Extract the columns of the current row
        columns = row.xpath('.//td')

        # Check for game rows
        if len(columns) == 3:
            home_team = clean_text(columns[0].xpath('.//a/text()')[0])
            away_team = clean_text(columns[2].xpath('.//a/text()')[0])
            home_team_info = clean_text(columns[0].xpath('.//div[@class="full-name"]//div[@class="aac-rank"]/text()')[0])
            away_team_info = clean_text(columns[2].xpath('.//div[@class="full-name"]//div[@class="aac-rank"]/text()')[0])
            home_conference = extract_conference(home_team_info)
            away_conference = extract_conference(away_team_info)
            home_conference = home_conference.replace('(','').replace(')','')
            away_conference = away_conference.replace('(','').replace(')','')
            home_goals = columns[1].xpath('.//span[@class="score-min"]/text()')
            away_goals = columns[1].xpath('.//span[@class="score-max"]/text()')
            if home_goals and away_goals:
                home_goals, away_goals = map(int, (home_goals[0], away_goals[0]))
            else:
                # Log a warning if the scores are not found
                logging.warning(f"Scores not found for game between {home_team} and {away_team} in {file_path}")
                continue
            data.append([home_team, away_team, home_goals, away_goals, home_conference, away_conference])

    # Convert the extracted data to a DataFrame
    df = pd.DataFrame(data, columns=['Home Team', 'Away Team', 'Home Goals', 'Away Goals', 'Home Team Conference', 'Away Team Conference'])

    # Save the DataFrame to a CSV file
    csv_file_path = f'outputs/week{week_number}_data_batch_{batch_id}.csv'
    df.to_csv(csv_file_path, index=False)
    print(f"Data for week {week_number} has been saved to {csv_file_path}")

# Loop through all the weeks
for week in range(1, 13):
    process_week(week)
