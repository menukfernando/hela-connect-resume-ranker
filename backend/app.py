import logging
import os
import re
from functools import lru_cache

import fitz
import pytesseract
import spacy
from flask import Flask, jsonify, request
from flask_cors import CORS
from pdf2image import convert_from_path
from PIL import Image
from sentence_transformers import SentenceTransformer, util

app = Flask(__name__)
CORS(app)

sbert_model = SentenceTransformer("all-MiniLM-L6-v2")
nlp = spacy.load("en_core_web_sm")

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"


def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF using PyMuPDF with OCR fallback"""
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            page_text = page.get_text()
            if page_text.strip():
                text += page_text
            else:
                # Fallback to OCR
                pix = page.get_pixmap()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                text += pytesseract.image_to_string(img)
        doc.close()
    except Exception as e:
        logging.error(f"Error with PyMuPDF: {e}")
        try:
            images = convert_from_path(pdf_path)
            for img in images:
                text += pytesseract.image_to_string(img)
        except Exception as ex:
            logging.error(f"Error during OCR: {ex}")
            text = ""
    return text


def extract_name_with_heuristics(text):
    """Extract a name from the first few lines of the resume."""
    lines = text.split("\n")
    for line in lines[:5]:
        if len(line.split()) <= 3:
            return line.strip()
    return None


def filter_invalid_names(names):
    """Filter out invalid names."""
    valid_names = []
    for name in names:
        if name.isupper():
            continue
        if any(char.isdigit() for char in name):
            continue
        valid_names.append(name)
    return valid_names


def extract_entities(text):
    """Extract names and emails from the text."""
    emails = re.findall(EMAIL_REGEX, text)

    # Use SpaCy for NER
    doc = nlp(text)
    spacy_names = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]

    # Use heuristic name extraction
    heuristic_name = extract_name_with_heuristics(text)

    # Combine results, prioritize heuristic over SpaCy
    names = [heuristic_name] if heuristic_name else spacy_names
    names = filter_invalid_names(names)

    return list(set(emails)), list(set(names))


def extract_relevant_sections(text):
    """Extract key sections from the resume: Education, Experience, and Skills"""
    sections = {
        "education": re.search(
            r"(education|qualifications)[\s\S]+?(?=\n[A-Z]|\Z)", text, re.I
        ),
        "experience": re.search(
            r"(experience|work history|employment)[\s\S]+?(?=\n[A-Z]|\Z)", text, re.I
        ),
        "skills": re.search(
            r"(skills|technical skills)[\s\S]+?(?=\n[A-Z]|\Z)", text, re.I
        ),
    }
    return {k: v.group().strip() if v else "" for k, v in sections.items()}


@lru_cache(maxsize=10)
def get_job_desc_embedding(job_description):
    """Cache job description embeddings for efficiency"""
    return sbert_model.encode(job_description, convert_to_tensor=True)


def calculate_final_score(similarity, keyword_match, experience_match):
    # Adjust weights to prioritize NLP expertise
    return (0.5 * similarity) + (0.4 * keyword_match) + (0.1 * experience_match)


def keyword_matching(job_description, resume_text):
    """Improved keyword matching based on important skills and technologies."""
    # Define a set of important keywords (you can expand this list)
    important_keywords = [
        "react",
        "node",
        "javascript",
        "typescript",
        "python",
        "django",
        "flask",
        "mongodb",
        "postgresql",
        "mysql",
        "aws",
        "azure",
        "docker",
        "kubernetes",
        "api",
        "restful",
        "full stack",
        "html",
        "css",
        "git",
        "github",
        "gitlab",
        "express",
        "firebase",
    ]

    # Convert both job description and resume to lowercase for case-insensitive matching
    job_text = job_description.lower()
    resume_text = resume_text.lower()

    # Count how many important keywords appear both in job description and resume
    matched_keywords = [
        keyword
        for keyword in important_keywords
        if keyword in resume_text and keyword in job_text
    ]

    # Calculate match score
    match_score = (
        len(matched_keywords) / len(important_keywords) if important_keywords else 0
    )
    return round(match_score * 100, 2)


@app.route("/", methods=["POST"])
def analyze_resumes():
    try:
        job_description = request.form.get("job_description")
        resume_files = request.files.getlist("resume_files")

        if not job_description or not resume_files:
            return jsonify({"error": "Job description and resumes are required."}), 400

        job_desc_embedding = get_job_desc_embedding(job_description)

        processed_resumes = []
        for resume_file in resume_files:
            resume_path = os.path.join(UPLOAD_FOLDER, resume_file.filename)
            resume_file.save(resume_path)

            resume_text = extract_text_from_pdf(resume_path)
            if not resume_text.strip():
                continue

            emails, names = extract_entities(resume_text)
            sections = extract_relevant_sections(resume_text)

            relevant_text = sections["experience"] + " " + sections["skills"]
            if not relevant_text.strip():
                relevant_text = (
                    resume_text  # Fallback to full resume if sections are empty
                )

            resume_embedding = sbert_model.encode(relevant_text, convert_to_tensor=True)
            similarity = util.cos_sim(job_desc_embedding, resume_embedding).item() * 100
            keyword_match = keyword_matching(job_description, relevant_text)

            final_score = calculate_final_score(similarity, keyword_match, 80)

            processed_resumes.append(
                {
                    "name": names[0] if names else "N/A",
                    "email": emails[0] if emails else "N/A",
                    "similarity": round(similarity, 2),
                    "keyword_match": keyword_match,
                    "final_score": round(final_score, 2),
                }
            )

        ranked_resumes = sorted(
            processed_resumes, key=lambda x: x["final_score"], reverse=True
        )
        for i, resume in enumerate(ranked_resumes, start=1):
            resume["rank"] = i

        return jsonify(ranked_resumes)
    except Exception as e:
        logging.exception("Error processing resumes")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
