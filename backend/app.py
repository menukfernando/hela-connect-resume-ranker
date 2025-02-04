import os
import re
import logging

from flask import Flask, jsonify, request
from flask_cors import CORS

import fitz
from sentence_transformers import SentenceTransformer, util
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

app = Flask(__name__)
CORS(app)

sbert_model = SentenceTransformer("all-MiniLM-L6-v2")

# Create an uploads directory if it doesn't exist
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            page_text = page.get_text()
            if page_text.strip():
                text += page_text
            else:
                # Fallback to OCR using the page's pixmap
                pix = page.get_pixmap()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                ocr_text = pytesseract.image_to_string(img)
                text += ocr_text
        doc.close()
    except Exception as e:
        logging.error(f"Error with PyMuPDF extraction: {e}")
        try:
            images = convert_from_path(pdf_path)
            for img in images:
                text += pytesseract.image_to_string(img)
        except Exception as ex:
            logging.error(f"Error during OCR with pdf2image: {ex}")
            text = ""
    return text


def extract_entities(text):
    emails = re.findall(r"\S+@\S+", text)
    names = re.findall(r"^([A-Z][a-z]+)\s+([A-Z][a-z]+)", text, re.MULTILINE)

    extracted_names = [" ".join(name) for name in names]

    return list(set(emails)), extracted_names


@app.route("/", methods=["POST"])
def analyze_resumes():
    try:
        job_description = request.form.get("job_description")
        resume_files = request.files.getlist("resume_files")

        if not job_description or not resume_files:
            return jsonify({"error": "Job description and resumes are required."}), 400

        job_desc_embedding = sbert_model.encode(job_description, convert_to_tensor=True)

        processed_resumes = []
        for resume_file in resume_files:

            resume_path = os.path.join(UPLOAD_FOLDER, resume_file.filename)
            resume_file.save(resume_path)

            resume_text = extract_text_from_pdf(resume_path)
            if not resume_text.strip():
                continue

            emails, names = extract_entities(resume_text)

            resume_embedding = sbert_model.encode(resume_text, convert_to_tensor=True)

            # Calculate cosine similarity between job description and resume
            similarity = util.cos_sim(job_desc_embedding, resume_embedding).item() * 100

            processed_resumes.append(
                {
                    "name": names[0] if names else "N/A",
                    "email": emails[0] if emails else "N/A",
                    "similarity": round(similarity, 2),
                }
            )

        ranked_resumes = sorted(
            processed_resumes, key=lambda x: x["similarity"], reverse=True
        )
        for i, resume in enumerate(ranked_resumes, start=1):
            resume["rank"] = i

        return jsonify(ranked_resumes)
    except Exception as e:
        logging.exception("Error processing resumes")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
