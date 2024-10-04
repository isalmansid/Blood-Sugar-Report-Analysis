# Blood Sugar Report Analysis

This is a full-stack application designed to help users analyze their blood sugar levels over time by uploading reports.
The application processes the uploaded files, extracts relevant data, and presents it visually using charts.


/blood-sugar-report-analysis
    ├── /backend
    │   ├── app.py
    │   ├── requirements.txt
    └── /blood-sugar-report (frontend)
        ├── package.json
        ├── src
        │   ├── App.js
        │   ├── BloodSugarUpload.js
        │   └── index.js
        └── public


1. Install the necessary packages:

```bash
pip install pdfplumber spacy
python -m spacy download en_core_web_sm
pip install pytesseract pdf2image
pip install pdfplumber spacy pytesseract pdf2image


pip install -r requirements.txt
```

2. Run the Flask application:

```bash
python app.py
```

3. Run the react app

```bash
npm start
```

4. Upload the blood reports from documents folder for testing
