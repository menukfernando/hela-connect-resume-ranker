import os
import re

import PyPDF2
import spacy
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
CORS(app)

# Load spaCy NER model
nlp = spacy.load("en_core_web_sm")

# Create an uploads directory if it doesn't exist
UPLOAD_FOLDER = "uploads"
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
    emails = re.findall(r"\S+@\S+", text)
    names = re.findall(r"^([A-Z][a-z]+)\s+([A-Z][a-z]+)", text)
    if names:
        names = [" ".join(names[0])]
    return emails, names


# Route to handle file uploads and resume analysis
@app.route("/", methods=["POST"])
def index():
    try:
        # Get job description and uploaded files from the request
        job_description = request.form.get("job_description")
        resume_files = request.files.getlist("resume_files")

        if not job_description or not resume_files:
            return jsonify({"error": "Job description and resumes are required."}), 400

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
        for names, emails, resume_text in processed_resumes:
            resume_vector = tfidf_vectorizer.transform([resume_text])
            similarity = cosine_similarity(job_desc_vector, resume_vector)[0][0] * 100
            ranked_resumes.append(
                {
                    "name": names[0] if names else "N/A",
                    "email": emails[0] if emails else "N/A",
                    "similarity": similarity,
                }
            )

        # Sort resumes by similarity score
        ranked_resumes.sort(key=lambda x: x["similarity"], reverse=True)

        # Add rank to each resume
        for i, resume in enumerate(ranked_resumes, start=1):
            resume["rank"] = i

        return jsonify(ranked_resumes)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
