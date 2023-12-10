import fitz  # PyMuPDF
import os
import pytesseract  # For OCR
import time
import requests
from PIL import Image

# Function to convert specified pages of PDF to PNG, perform OCR and save text to files
def convert_specified_pdf_pages_to_png_ocr(pdf_path, pages_to_scrape, output_folder):
    # Open the PDF file
    doc = fitz.open(pdf_path)
    
    # Create the output folder for text if it doesn't exist
    output_text_folder = os.path.join(output_folder, "text_outputs")
    os.makedirs(output_text_folder, exist_ok=True)

    # Iterate over each specified page of the PDF
    for page_num in pages_to_scrape:
        # Load the page
        page = doc.load_page(page_num)

    doc.close()

# Define the path to the PDF file and output folder
pdf_path = 'data/pd1.pdf'  # Replace with your actual PDF file path
output_folder = 'data'  # Replace with your actual output folder path
pages_to_scrape = [5, 6, 7, 8, 9, 10]  # Pages to scrape, zero-indexed

# Call the function to convert and OCR specified pages
convert_specified_pdf_pages_to_png_ocr(pdf_path, pages_to_scrape, output_folder)


files = {'pdf': ('pd1.pdf', open('data/pd1.pdf', 'rb'))}
response = requests.post('http://localhost:1616', files=files, data={'lang': 'de'})
id = response.json()['id']

while True:
    r = requests.get(f"http://localhost:1616/update/{id}")
    j = r.json()
    if 'text' in j:
        break
    print('waiting...')
    time.sleep(1)
print(j['text'])
