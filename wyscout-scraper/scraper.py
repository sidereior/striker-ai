import fitz  # PyMuPDF
import pandas as pd
import re

def extract_data_from_pdf(pdf_path):
    # Open the PDF
    doc = fitz.open(pdf_path)

    # Extract text from each page
    full_text = ""
    for page in doc:
        full_text += page.get_text("text")
    doc.close()

    # Find the player's name from the file name
    player_name = pdf_path.split('/')[-1].split('_')[0].split('-')[-1]

    # Regex pattern to match the statistics format
    pattern = re.compile(r'([A-Za-z\s/]+)\s+([0-9/]+)\s+[0-9%]+\s+([0-9/]+)\s+[0-9%]+\s+([0-9/]+)')

    # Find all matches
    matches = pattern.findall(full_text)

    # Process and structure the data
    data = []
    for match in matches:
        statistic, match_stat, first_half_stat, second_half_stat = match
        data.append([statistic.strip(), match_stat.strip(), first_half_stat.strip(), second_half_stat.strip()])

    # Create a DataFrame
    df = pd.DataFrame(data, columns=['Statistic', 'Match Stat', '1st Half Stat', '2nd Half Stat'])
    df.insert(0, 'Player Name', player_name)

    return df

# Path to the PDF file
pdf_path = 'path_to_your_pdf_file.pdf'

# Extract data and create a DataFrame
df = extract_data_from_pdf(pdf_path)

# Save the DataFrame to a CSV file
csv_path = 'path_to_your_csv_file.csv'
df.to_csv(csv_path, index=False)

print(f"Data extracted and saved to {csv_path}")
