# Resume Align Lens

**Resume Intelligence Engine** — An AI-powered diagnostic tool that analyzes your resume against a job description and produces precise, explainable feedback. Not a resume builder. An analytical engine.

---

## Live DEMO :
    https://resume-align-lens.onrender.com


## What It Does and why 

ResumeAlign Lens performs a multi-stage analysis pipeline:

1. **Job Description Parsing** — Extracts role requirements, must-have skills, ATS keywords, and seniority signals
2. **Resume Intelligence Extraction** — Identifies skills, experience, achievements, and structural gaps
3. **Semantic Analysis** — Compares both using LLM reasoning (not naive string matching)
4. **Scoring** — Generates a 0–100 alignment score with dimensional breakdown
5. **Explainable Recommendations** — Every suggestion includes a specific reason grounded in the job description

---

## Architecture

```
cvalign-lens/
├── app.py                      # Flask entry point — routes & request handling
├── services/
│   ├── jd_parser.py            # Extracts structured intelligence from job descriptions
│   ├── resume_parser.py        # Extracts structured candidate data from resumes
│   ├── analyzer.py             # Core semantic comparison engine
│   └── scorer.py               # Alignment scoring with dimensional breakdown
├── prompts/
│   └── prompt_templates.py     # All LLM prompts (centralized, never inline)
├── utils/
│   ├── llm_client.py           # Anthropic API wrapper with JSON extraction
│   ├── file_handlers.py        # Resume file upload & text extraction (PDF/DOCX/TXT)
│   └── text_processing.py      # Text cleaning & normalization utilities
├── templates/
│   └── index.html              # Single-page application template
├── static/
│   ├── styles.css              # Custom premium dark UI (no Bootstrap)
│   └── app.js                  # Frontend interactions & results rendering
├── requirements.txt
└── README.md
```

---

## Prerequisites

- Python 3.10+
- An [Anthropic API key](https://console.anthropic.com/)

---

## Setup & Installation

### 1. Clone or download the project

```bash
cd resumealign-lens
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set your API key (you can use any API -KEY)

```bash
# macOS / Linux
export GROQ_API_KEY="sk-ant-your-key-here"

# Windows (Command Prompt)
set GROQ_API_KEY=sk-ant-your-key-here

# Windows (PowerShell)
$env:GROQ_API_KEY="sk-ant-your-key-here"
```

### 5. Run the application (use python3 or python)

```bash
python app.py
```

The app will be available at: **http://localhost:5000**

---

## Configuration

| Environment Variable | Default | Description |
|---|---|---|
| `GROQ_API_KEY` | Required | Your Groq API key |
| `GROQ_MODEL` | Model to use for analysis |
| `PORT` | `5000` | Port the Flask server listens on |
| `FLASK_DEBUG` | `false` | Enable Flask debug mode |

---

## Production Deployment

### Using Gunicorn (recommended)

```bash
gunicorn app:app --bind 0.0.0.0:8000 --workers 2 --timeout 120
```

### Environment notes for production

- Set `FLASK_DEBUG=false`
- Use a reverse proxy (nginx) in front of gunicorn
- Store your `GROQ_API_KEY` in a secrets manager or `.env` file (never commit it)
- Consider rate limiting the `/api/analyze` endpoint

---

## How the Analysis Works

### Pipeline

```
User Input (JD + Resume)
        ↓
   JD Parser (jd_parser.py)
   Extracts: role title, seniority, skills, requirements, ATS keywords
        ↓
   Resume Parser (resume_parser.py)
   Extracts: skills, experience, achievements, sections, keywords
        ↓
   Analyzer (analyzer.py)
   Produces: strengths, weaknesses, skill gaps, missing keywords,
             section improvements, bullet optimization patterns
        ↓
   Scorer (scorer.py)
   Produces: overall score, 5 dimensional scores,
             hiring recommendation, top 3 actions
        ↓
   JSON Response → Frontend renders results
```

### Prompt Design

All prompts are centralized in `prompts/prompt_templates.py`. No prompt text appears inside routes, services, or utilities. The system prompt defines the analytical persona; task prompts define the specific extraction or analysis task.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+, Flask 3.0 |
| AI | GROQ |
| PDF Parsing | pdfplumber |
| DOCX Parsing | python-docx |
| Frontend | Vanilla HTML / CSS / JavaScript |
| Production Server | Gunicorn |

---

## Design Principles

- **No pseudo-code** — every function is fully implemented
- **Separation of concerns** — parsing, analysis, and scoring are independent services
- **Centralized prompts** — all LLM prompts in one place, versioned together
- **Defensive error handling** — every external call is wrapped with informative error messages
- **Explainability first** — every AI suggestion includes explicit reasoning

---

## Limitations

- Analysis quality depends on resume and JD completeness — vague inputs produce vague results
- Scanned/image-based PDFs cannot be parsed; plain text paste is the fallback
- Each analysis costs approximately $0.01–0.04 in API credits depending on input length

---

## License

 free to use, modify, and deploy.
 If you like the work, please leave a STAR.
