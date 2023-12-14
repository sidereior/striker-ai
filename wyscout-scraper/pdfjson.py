
import pdfplumber
import json
import re
import time
import datetime

pdf_path = 'test.pdf'

def extract_and_format_data(page_number):
    data_format = ["Min. played", "Forward passes", "Back passes", "Lateral passes", 
                   "Short-med passes", "Long passes", "Prog. passes", "Passes final 3rd", 
                   "Through passes", "Deep completions", "Key passes", "Second assists", 
                   "Third assists", "Shot assists"]

    formatted_data = []

    def process_stat(stat):
        # Modified regex to include special characters
        if stat.endswith("'") or stat == '-' or '/' not in stat:
            return stat
        else:  # If stat is a fraction and a percentage
            if stat.endswith('%'):
                stat = stat[:-1]
                split_stat = stat.split('/')
                denom = split_stat[0]
                #15/1067
                #1067
                num = split_stat[1]
                i = 1
                first_num = num[:len(num)-0]
                while len(first_num) > 0:
                    first_num = num[:len(num)-i]
                    second_num = num[len(num)-i:]
                    result = int(first_num) / int(denom)
                    if first_num:  # Check if first_num is not empty
                        result = int(first_num) / int(denom)
                        result = result * 100
                        # Cast result to int for comparison
                        if int(result) == int(second_num) or int(result) == int(second_num) + 1 or int(result) == int(second_num) - 1:
                            return str(denom) + "/" + str(first_num)
                    else:
                        break  # Break the loop if first_num is empty to avoid errors

                    i += 1
                return 'PARSE ERROR'
            return 'INPUT ERROR'  # If no matching fraction is found
              
    # Generate a timestamped filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    output_filename = f'output{timestamp}.txt'

    with pdfplumber.open(pdf_path) as pdf, open(output_filename, 'w') as output_file:
        page = pdf.pages[page_number]
        text = page.extract_text()
        if text:
            lines = text.split('\n')
            start_processing = False
            for line in lines:
                # Write each line to the file
                output_file.write(line + '\n')

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
                            
                    player_name_full = ""
                    for i in range(1, indexToGoTo+1, 1):
                       player_name_full += segments[i] + " " 
                    player_name_full = player_name_full.strip() 
                    #player_name = segments[1:indexToGoTo+1]
                    stats_str = segments[indexToGoTo+1:]
                    for i in stats_str:
                        print(i)
                    stats = [process_stat(stat) for stat in stats_str]

                    formatted_stats = dict(zip(data_format, stats))
                    formatted_player_data = {"Player Number": player_number, "Player Name": player_name_full}
                    formatted_player_data.update(formatted_stats)

                    formatted_data.append(formatted_player_data)
    return formatted_data

# Extracting and formatting data from page 7
formatted_data_page_7 = extract_and_format_data(6)  # Page numbers are 0-indexed

# Convert to JSON
json_data = json.dumps(formatted_data_page_7, indent=4)
print(json_data)
