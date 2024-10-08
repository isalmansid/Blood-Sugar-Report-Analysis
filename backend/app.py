from flask import Flask, request, jsonify
import pdfplumber
import spacy
import sys
import pytesseract
from pdf2image import convert_from_path
import re
from flask_cors import CORS
from spacy.matcher import Matcher


app = Flask(__name__)
CORS(app)

def extract_text_with_pdfplumber(file):
    """Extract text from a PDF file using pdfplumber."""
    try:
        with pdfplumber.open(file) as pdf:
            full_text = ''
            for page in pdf.pages:
                full_text += page.extract_text() + '\n'
        return full_text
    except Exception as e:
        print(f'[ERROR] An error occurred while extracting text with pdfplumber: {e}')
        return ''

def extract_text_with_ocr(file):
    """Extract text from a PDF file using OCR."""
    try:
        images = convert_from_path(file)
        full_text = ''
        for image in images:
            text = pytesseract.image_to_string(image)
            full_text += text + '\n'
        return full_text
    except Exception as e:
        print(f'[ERROR] An error occurred while extracting text with OCR: {e}')
        return ''

def extract_month_from_text(text):
    """Extract month and year from a date in the format DD/MM/YYYY or 'DD MMM YYYY'."""
    date_pattern1 = r'(\d{2})/(\d{2})/(\d{4})'
    date_pattern2 = r'(\d{2})\s+([A-Za-z]{3})\s+(\d{4})'

    match1 = re.search(date_pattern1, text)
    match2 = re.search(date_pattern2, text)

    if match1:
        day, month, year = match1.groups()
        month_name = {
            '01': 'January', '02': 'February', '03': 'March', '04': 'April',
            '05': 'May', '06': 'June', '07': 'July', '08': 'August',
            '09': 'September', '10': 'October', '11': 'November', '12': 'December'
        }.get(month, month)
        return f"{month_name} {year}"

    if match2:
        day, month, year = match2.groups()
        month_name = month.capitalize()
        return f"{month_name} {year}"

    return None

def extract_blood_sugar_nlp(file):
    """Extract blood sugar levels and month from a PDF."""
    # Load spaCy's English model
    try:
        nlp = spacy.load('en_core_web_sm')
    except OSError:
        print('[ERROR] spaCy English model not found. Please run "python -m spacy download en_core_web_sm"')
        sys.exit(1)

    # Initialize the Matcher
    matcher = Matcher(nlp.vocab)

    # Define patterns to match fasting and post-lunch blood sugar levels
    patterns = [
        [
            {'LOWER': 'fasting'},
            {'LOWER': 'blood'},
            {'LOWER': {'IN': ['glucose', 'sugar']}},
            {'LIKE_NUM': True},
            {'LOWER': {'IN': ['mg/dl']}, 'OP': '?'}
        ],
        [
            {'LOWER': 'post'},
            {'LOWER': 'lunch'},
            {'LOWER': 'blood'},
            {'LOWER': {'IN': ['glucose', 'sugar']}},
            {'LIKE_NUM': True},
            {'LOWER': {'IN': ['mg/dl']}, 'OP': '?'}
        ]
    ]
    matcher.add('FASTING_BLOOD_SUGAR', [patterns[0]])
    matcher.add('POST_LUNCH_BLOOD_SUGAR', [patterns[1]])

    # Step 1: Try extracting text with pdfplumber
    print('[INFO] Extracting text using pdfplumber...')
    text = extract_text_with_pdfplumber(file)

    # If no text found, use OCR
    if not text or not text.strip():
        print('[WARNING] No text extracted with pdfplumber. Attempting OCR...')
        text = extract_text_with_ocr(file)
        if not text or not text.strip():
            print('[ERROR] Failed to extract text using both pdfplumber and OCR.')
            sys.exit(1)

    # print(f'[INFO] Extracted Text: {text}')

    # Extract month and year from the text
    month = extract_month_from_text(text)

    # Process the extracted text with spaCy
    doc = nlp(text)

    # Find matches using the matcher
    matches = matcher(doc)

    # Initialize lists to store readings
    fasting_readings = []
    post_lunch_readings = []

    for match_id, start, end in matches:
        span = doc[start:end]

        # Extract the numeric value and unit
        value = None
        unit = None
        for token in span:
            if token.like_num:
                value = token.text
            elif token.text.lower() in ['mg/dl']:
                unit = token.text.lower()

        if value:
            reading = f'{value} {unit}' if unit else f'{value} (mg/dl)'

            if nlp.vocab.strings[match_id] == 'FASTING_BLOOD_SUGAR':
                fasting_readings.append(reading)
            elif nlp.vocab.strings[match_id] == 'POST_LUNCH_BLOOD_SUGAR':
                post_lunch_readings.append(reading)

    # Check for fasting and postprandial readings in the extracted text
    lines = text.splitlines()
    for line in lines:
        # Search for the fasting blood sugar reading
        if "FASTING BLOOD SUGAR(GLUCOSE) PHOTOMETRY" in line:
            match = re.search(r'FASTING BLOOD SUGAR\(GLUCOSE\) PHOTOMETRY\s+([\d\.]+)\s*mg/dL', line)
            if match:
                fasting_readings.append(f"{match.group(1)} mg/dL")

        # Search for the postprandial blood sugar reading
        if "POSTPRANDIAL BLOOD SUGAR(GLUCOSE) PHOTOMETRY" in line:
            match = re.search(r'POSTPRANDIAL BLOOD SUGAR\(GLUCOSE\) PHOTOMETRY\s+([\d\.]+)\s*mg/dL', line)
            if match:
                post_lunch_readings.append(f"{match.group(1)} mg/dL")

    # Remove duplicates
    fasting_readings = list(set(fasting_readings))
    post_lunch_readings = list(set(post_lunch_readings))

    # Prepare result
    result = {
        'month': month,
        'fasting': fasting_readings,
        'post_lunch': post_lunch_readings
    }

    return result

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400

    files = request.files.getlist('files')
    results = []

    for file in files:
        if file and file.filename.endswith('.pdf'):
            # Process the file directly
            blood_sugar_data = extract_blood_sugar_nlp(file)  # Extract readings
            results.append(blood_sugar_data)  # Store results

    return jsonify(results)  # Return all extracted data

if __name__ == "__main__":
    app.run(debug=True)
