import re
from lxml import html
import pandas as pd
import os
import logging
from datetime import datetime
import argparse

# Define a unique batch ID based on the current date and time
batch_id = datetime.now().strftime("%Y%m%d_%H%M%S")

# Setting up the log directory
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)

# Setting up logging
log_filename = f'{log_dir}/processing_batch_{batch_id}.log'
logging.basicConfig(filename=log_filename, level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

# Define a function to clean text data
def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

# Define a function to extract the conference information from the string
def extract_conference(info_string):
    # Remove all non-alphabetic characters from the beginning of the string
    conference = re.sub(r'^[^a-zA-Z]*', '', info_string)
    return conference

# Define a function to process a single week for a given division
def process_week(week_number, division):
    # Construct file path based on division and week number
    file_path = f'inputs/{division}-week{week_number}.txt'
    if not os.path.exists(file_path):
        logging.warning(f"File not found: {file_path}")
        return None
    
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Parse the HTML content
    tree = html.fromstring(html_content)

    # Locate the element with the specified XPath
    list_table_view = tree.xpath('//*[@id="listTableView"]')
    if not list_table_view:
        logging.warning(f"Element with id 'listTableView' not found in {file_path}")
        return None

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
            scores = columns[1].xpath('.//a//span/text()')
            if len(scores) == 2:
                home_goals, away_goals = map(int, scores)
            else:
                # Log a warning if the scores are not found
                logging.warning(f"Scores not found for game between {home_team} and {away_team} in {file_path}")
                continue
            data.append([home_team, away_team, home_goals, away_goals, home_conference, away_conference, week_number, division])

    # Convert the extracted data to a DataFrame
    return pd.DataFrame(data, columns=['Home Team', 'Away Team', 'Home Goals', 'Away Goals', 'Home Team Conference', 'Away Team Conference', 'Week', 'Division'])

# Set up command-line argument parsing
parser = argparse.ArgumentParser(description='Process soccer game data.')
parser.add_argument('division', type=str, help='The division to process (d1, d2, d3, naia, njcaa, or all)')
parser.add_argument('batched', type=str, help='Whether the output should be batched (True or False)')

# Parse command-line arguments
args = parser.parse_args()

# Validate batched argument
if args.batched.lower() not in ['true', 'false']:
    print("Invalid argument for batched. Please choose True or False.")
    exit()

# Convert batched argument to boolean
args.batched = args.batched.lower() == 'true'

# List of all possible divisions
divisions = ['d2', 'd3', 'naia', 'njcaa', 'd1']

# Initialize a DataFrame to store all data if not batching
all_data = pd.DataFrame()

# Loop through all the weeks and divisions based on user input
for week in range(1, 14):
    if args.division.lower() == 'all':
        for division in divisions:
            df = process_week(week, division)
            if df is not None:
                if args.batched:
                    csv_file_path = f'outputs/{division}_week{week}_data_batch_{batch_id}.csv'
                    df.to_csv(csv_file_path, index=False)
                    print(f"Data for {division} division, week {week} has been saved to {csv_file_path}")
                else:
                    all_data = pd.concat([all_data, df], ignore_index=True)
    elif args.division.lower() in divisions:
        df = process_week(week, args.division.lower())
        if df is not None:
            if args.batched:
                csv_file_path = f'outputs/{args.division.lower()}_week{week}_data_batch_{batch_id}.csv'
                df.to_csv(csv_file_path, index=False)
                print(f"Data for {args.division.lower()} division, week {week} has been saved to {csv_file_path}")
            else:
                all_data = pd.concat([all_data, df], ignore_index=True)
    else:
        print("Invalid division specified. Please choose from d1, d2, d3, naia, njcaa, or all.")
        exit()

if not args.batched:
    if args.division.lower() == 'all':
        csv_file_path = f'outputs/all_unbatched_{batch_id}.csv'
    else:
        csv_file_path = f'outputs/{args.division.lower()}_unbatched_{batch_id}.csv'
    all_data.to_csv(csv_file_path, index=False)
    print(f"All data has been saved to {csv_file_path}")
