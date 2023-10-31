import re
from lxml import html
import pandas as pd
import os

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
    print(f"Processing data for week {week_number}")
    # Load the HTML content from the text file
    file_path = f'inputs/week{week_number}.txt'
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Parse the HTML content
    tree = html.fromstring(html_content)

    # Locate the element with the specified XPath
    list_table_view = tree.xpath('//*[@id="listTableView"]')
    if not list_table_view:
        print(f"Element with id 'listTableView' not found in {file_path}")
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
            score = clean_text(columns[1].text_content())
            # Remove non-numeric characters from the score
            score = re.sub(r'[^0-9:]', '', score)
            home_goals, away_goals = map(int, score.split(':'))
            home_conference = home_conference.replace('(','').replace(')','')
            away_conference = away_conference.replace('(','').replace(')','')
            data.append([home_team, away_team, home_goals, away_goals, home_conference, away_conference])

    # Convert the extracted data to a DataFrame
    df = pd.DataFrame(data, columns=['Home Team', 'Away Team', 'Home Goals', 'Away Goals', 'Home Team Conference', 'Away Team Conference'])

    # Save the DataFrame to a CSV file
    csv_file_path = f'outputs/week{week_number}_data.csv'
    df.to_csv(csv_file_path, index=False)
    print(f"Data for week {week_number} has been saved to {csv_file_path}")

# Loop through all the weeks
for week in range(1, 13):
    process_week(week)