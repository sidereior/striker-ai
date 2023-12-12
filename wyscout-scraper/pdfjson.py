import pdfplumber
import json

pdf_path = 'test.pdf'

def extract_and_format_data(page_number):
    data_format = ["Min. played", "Forward passes", "Back passes", "Lateral passes", 
                   "Short-med passes", "Long passes", "Prog. passes", "Passes final 3rd", 
                   "Through passes", "Deep completions", "Key passes", "Second assists", 
                   "Third assists", "Shot assists"]

    formatted_data = []

    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_number]
        text = page.extract_text()
        if text:
            lines = text.split('\n')
            start_processing = False
            for line in lines:
                if "Player" in line:
                    start_processing = True
                    continue
                if start_processing and line.strip():
                    # Splitting the line into segments based on multiple spaces
                    segments = line.split(maxsplit=2)
                    if len(segments) < 3:
                        continue  # Skip if the line doesn't have enough segments

                    player_number, player_name, stats_str = segments
                    # Removing percentage signs and splitting the stats
                    stats = stats_str.replace('%', '').split()
                    # Adjust the stats to match the format
                    stats = [stat if '/' in stat else stat.split('/')[0] for stat in stats]

                    formatted_stats = dict(zip(data_format, stats))
                    formatted_player_data = {"Player Number": player_number, "Player Name": player_name}
                    formatted_player_data.update(formatted_stats)

                    formatted_data.append(formatted_player_data)

    return formatted_data

# Extracting and formatting data from page 7
formatted_data_page_7 = extract_and_format_data(6)  # Page numbers are 0-indexed

# Convert to JSON
json_data = json.dumps(formatted_data_page_7, indent=4)
print(json_data)
