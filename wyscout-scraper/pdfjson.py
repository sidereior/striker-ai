import pdfplumber
import json
import re

pdf_path = 'test.pdf'

def extract_and_format_data(page_number):
    data_format = ["Min. played", "Forward passes", "Back passes", "Lateral passes", 
                   "Short-med passes", "Long passes", "Prog. passes", "Passes final 3rd", 
                   "Through passes", "Deep completions", "Key passes", "Second assists", 
                   "Third assists", "Shot assists"]

    formatted_data = []

    def process_stat(stat):
        # Check if the input is alphanumeric, ends with a single quote, or is a single dash
        if re.match('^[a-zA-Z0-9]*$', stat) or stat.endswith("'") or stat == '-':
            return stat
        elif '/' not in stat:  # If stat is a number
            return float(stat)
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
            return 'ERROR'  # If the fraction doesn't match the percentage and it's over 100%

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
                    segments = line.split(maxsplit=2)
                    if len(segments) < 3:
                        continue

                    player_number, player_name, stats_str = segments
                    stats = [process_stat(stat) for stat in stats_str.split()]

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
