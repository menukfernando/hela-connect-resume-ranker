from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import spacy
import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import os

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app)

# Load spaCy NER model
nlp = spacy.load("en_core_web_sm")

# Create an uploads directory if it doesn't exist
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Function to extract text from PDFs
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, "rb") as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text

# Function to extract entities (names and emails) from text
def extract_entities(text):
    emails = re.findall(r'\S+@\S+', text)
    names = re.findall(r'^([A-Z][a-z]+)\s+([A-Z][a-z]+)', text)
    if names:
        names = [" ".join(names[0])]
    return emails, names

# Route to handle file uploads and resume analysis
@app.route('/', methods=['POST'])
def index():
    try:
        # Get job description and uploaded files from the request
        job_description = request.form.get('job_description')
        resume_files = request.files.getlist('resume_files')

        # Process uploaded resumes
        processed_resumes = []
        for resume_file in resume_files:
            # Save the uploaded file
            resume_path = os.path.join(UPLOAD_FOLDER, resume_file.filename)
            resume_file.save(resume_path)

            # Extract text and entities from the resume
            resume_text = extract_text_from_pdf(resume_path)
            emails, names = extract_entities(resume_text)
            processed_resumes.append((names, emails, resume_text))

        # TF-IDF vectorizer to compare job description with resumes
        tfidf_vectorizer = TfidfVectorizer()
        job_desc_vector = tfidf_vectorizer.fit_transform([job_description])

        # Rank resumes based on similarity to the job description
        ranked_resumes = []
        for (names, emails, resume_text) in processed_resumes:
            resume_vector = tfidf_vectorizer.transform([resume_text])
            similarity = cosine_similarity(job_desc_vector, resume_vector)[0][0] * 100
            ranked_resumes.append({
                "name": names[0] if names else "N/A",
                "email": emails[0] if emails else "N/A",
                "similarity": similarity
            })

        # Sort resumes by similarity score
        ranked_resumes.sort(key=lambda x: x["similarity"], reverse=True)

        return jsonify(ranked_resumes)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to download ranked resumes as a CSV file
@app.route('/download_csv', methods=['GET'])
def download_csv():
    try:
        csv_filename = "ranked_resumes.csv"
        csv_path = os.path.join(os.getcwd(), csv_filename)

        # Generate CSV content
        csv_content = "Rank,Name,Email,Similarity\n"
        for rank, resume in enumerate(ranked_resumes, start=1):
            csv_content += f'{rank},{resume["name"]},{resume["email"]},{resume["similarity"]:.2f}\n'

        # Write CSV file
        with open(csv_path, "w") as csv_file:
            csv_file.write(csv_content)

        # Send file for download
        return send_file(csv_path, as_attachment=True, download_name=csv_filename)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
