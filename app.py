"""
CVAlign Lens — Flask Application Entry Point
"""
from dotenv import load_dotenv
import os
import json
from flask import Flask, request, jsonify, render_template
from werkzeug.exceptions import RequestEntityTooLarge

from services.jd_parser import JDParser
from services.resume_parser import ResumeParser
from services.analyzer import Analyzer
from services.scorer import Scorer
from utils.file_handlers import FileHandler

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB limit

file_handler = FileHandler()
jd_parser = JDParser()
resume_parser = ResumeParser()
analyzer = Analyzer()
scorer = Scorer()


@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    return jsonify({"error": "File too large. Maximum size is 5MB."}), 413


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/analyze", methods=["POST"])
def analyze():
    try:
        job_description_text = request.form.get("job_description", "").strip()
        resume_text = request.form.get("resume_text", "").strip()
        resume_file = request.files.get("resume_file")

        # job description
        if not job_description_text:
            return jsonify({"error": "Job description is required."}), 400

        # Resolve resume text
        if resume_file and resume_file.filename:
            extracted = file_handler.extract_text(resume_file)
            if extracted.get("error"):
                return jsonify({"error": extracted["error"]}), 400
            resume_text = extracted["text"]

        if not resume_text:
            return jsonify({"error": "Resume content is required (paste text or upload a file)."}), 400

        # Parse the inputs
        jd_data = jd_parser.parse(job_description_text)
        resume_data = resume_parser.parse(resume_text)

        # Run the analysis
        analysis = analyzer.analyze(jd_data, resume_data)

        # Score the analysis
        score_data = scorer.score(analysis)

        return jsonify({
            "success": True,
            "jd_summary": jd_data,
            "resume_summary": resume_data,
            "analysis": analysis,
            "score": score_data,
        })

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 422
    except Exception as e:
        app.logger.error(f"Analysis failed: {e}", exc_info=True)
        return jsonify({"error": "Analysis failed. Please verify your API key and inputs, then try again."}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
