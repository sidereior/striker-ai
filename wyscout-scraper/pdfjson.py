
import pdfplumber
import json
import re
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
            fraction, percent = stat.split('%')[0].split('/')
            numerator = int(fraction)
            denominator = ''
            percent = percent.lstrip('0')  # remove leading zeros from percent
            for digit in percent:
                denominator += digit
                if denominator == '0':  # If denominator is zero
                    return f'{numerator}/{denominator}'
                elif numerator/int(denominator) == int(percent)/100:  # If the fraction matches the percentage
                    return f'{numerator}/{denominator}'
            return 'ERROR:'  # If the fraction doesn't match the percentage and it's over 100%
    
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
