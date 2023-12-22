import pdfplumber
import json
import re
import datetime

# List of paths to PDF files
pdf_paths = ['test1.pdf']  # Add your PDF file paths here

def find_pages_with_string(pdf_path, target_string):
    pages_with_string = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text and target_string in text:
                pages_with_string.append(i)
    return pages_with_string

def process_stat(stat):
    if stat.endswith("'") or stat == '-' or '/' not in stat:
        return stat
    else:  # If stat is a fraction and a percentage
        if stat.endswith('%'):
            stat = stat[:-1]
            split_stat = stat.split('/')
            denom = split_stat[0]
            num = split_stat[1]
            i = 1
            first_num = num[:len(num)-0]
            while len(first_num) > 0:
                first_num = num[:len(num)-i]
                second_num = num[len(num)-i:]
                if first_num:  # Check if first_num is not empty
                    result = int(first_num) / int(denom)
                    result = result * 100
                    if int(result) == int(second_num) or int(result) == int(second_num) + 1 or int(result) == int(second_num) - 1:
                        return str(denom) + "/" + str(first_num)
                else:
                    break  # Break the loop if first_num is empty to avoid errors

                i += 1
            return 'PARSE ERROR'
        elif re.match(r"^\d+/\d+$", stat):
            return stat
        return 'INPUT ERROR'  # If no matching fraction is found

def extract_and_format_data(pdf_path, page_number, filter, after_or_before):
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
            for line in lines[:-1]:
                if "Player" in line:
                    start_processing = True
                    continue
                if start_processing and line.strip():
                    segments = line.split()
                    player_number = segments[0]
                    indexToGoTo = -1

                    for(segment_index, segment) in enumerate(segments):
                        if "'" in segment:
                            indexToGoTo = segment_index-1
                            break
                            
                    player_name_full = " ".join(segments[1:indexToGoTo+1]).strip()
                    stats_str = segments[indexToGoTo+1:]
                    stats = [process_stat(stat) for stat in stats_str]
                    formatted_stats = dict(zip(data_format, stats))
                    formatted_player_data = {"Player Number": player_number, "Player Name": player_name_full}
                    formatted_player_data.update(formatted_stats)
                    formatted_data.append(formatted_player_data)

    return formatted_data

# List of paths to PDF files
pdf_paths = ['test1.pdf']  # Add your PDF file paths here

# Initialize a list to collect data from all PDFs
all_formatted_data = []

# Target string to search for in each PDF
target_string = "Throw-ins"

# Iterate over each PDF path
for pdf_path in pdf_paths:
    # Find the pages with the target string
    pages_to_process = find_pages_with_string(pdf_path, target_string, "test")

    #check if both words on same page

    # Extracting and formatting data from the identified pages of each PDF
    for page_number in pages_to_process:
        formatted_data = extract_and_format_data(pdf_path, page_number)
        # Append extracted data to the collective list
        all_formatted_data.extend(formatted_data)

# Convert all data to JSON
json_data = json.dumps(all_formatted_data, indent=4)

# Generate a timestamped filename for the JSON output
timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
json_output_filename = f'combined_passing_tables_{timestamp}.json'

# Write JSON data to a file
with open(json_output_filename, 'w') as file:
    file.write(json_data)