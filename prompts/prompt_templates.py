"""
CVAlign Lens — Centralized Prompt Templates
All LLM prompts live here. Never embed prompt text inside routes or services directly.
"""


SYSTEM_PROMPT = """You are CVAlign Lens, an expert resume diagnostic engine with the analytical mindset of a senior technical recruiter and talent strategist.

Your role is to perform precise, evidence-based analysis of resumes against job descriptions. You are not a cheerleader or a generic resume coach. You identify real gaps, real strengths, and provide genuinely useful, specific improvement guidance.

Rules:
- Be direct and professional. Avoid filler phrases.
- Every suggestion must include a specific reason grounded in the job description.
- Confidence levels must reflect genuine certainty, not optimism.
- Do not fabricate skills or experience that are not present in the resume.
- Output only valid JSON. No markdown, no explanation outside the JSON structure.
"""


JD_EXTRACTION_PROMPT = """Analyze the following job description and extract structured intelligence.

Job Description:
{job_description}

Return a JSON object with this exact structure:
{{
  "role_title": "string — inferred job title",
  "seniority_level": "string — Junior / Mid-level / Senior / Lead / Principal",
  "core_technical_skills": ["list of hard technical skills explicitly required"],
  "soft_skills": ["list of soft skills or behavioral traits mentioned"],
  "domain_knowledge": ["industry domains, sectors, or specialized knowledge areas"],
  "key_responsibilities": ["3–6 concise responsibility statements"],
  "must_have_requirements": ["non-negotiable qualifications explicitly stated"],
  "nice_to_have_requirements": ["preferred but optional qualifications"],
  "keywords_for_ats": ["high-value ATS keywords from the JD"]
}}

Return only the JSON object. No explanation."""


RESUME_EXTRACTION_PROMPT = """Analyze the following resume and extract structured intelligence.

Resume:
{resume_text}

Return a JSON object with this exact structure:
{{
  "candidate_name": "string or null",
  "inferred_title": "string — best-fit job title based on experience",
  "years_of_experience": "string — e.g., '3–5 years' or 'Unknown'",
  "technical_skills": ["all technical skills found"],
  "soft_skills": ["soft skills or behavioral indicators"],
  "domain_experience": ["industries or domains worked in"],
  "education": ["highest degree and field, institution if present"],
  "notable_achievements": ["quantified or high-impact accomplishments"],
  "resume_sections_present": ["list of sections: e.g., Summary, Experience, Education, Projects, Certifications"],
  "missing_sections": ["sections commonly expected that are absent"],
  "keywords_present": ["strong ATS-relevant keywords found"]
}}

Return only the JSON object. No explanation."""


ANALYSIS_PROMPT = """You are performing a deep diagnostic comparison between a candidate's resume and a job description.

Job Description Intelligence:
{jd_data}

Resume Intelligence:
{resume_data}

Perform a rigorous analysis and return a JSON object with this exact structure:
{{
  "strengths": [
    {{
      "point": "string — specific strength",
      "reasoning": "string — why this is a strength relative to the JD",
      "confidence": "High | Medium | Low"
    }}
  ],
  "weaknesses": [
    {{
      "point": "string — specific weakness or gap",
      "reasoning": "string — why this is a weakness relative to the JD",
      "confidence": "High | Medium | Low"
    }}
  ],
  "missing_keywords": [
    {{
      "keyword": "string",
      "importance": "Critical | Important | Nice-to-have",
      "reasoning": "string — why this keyword matters for this role"
    }}
  ],
  "skill_gaps": [
    {{
      "skill": "string",
      "gap_severity": "Critical | Moderate | Minor",
      "reasoning": "string — explanation of the gap",
      "suggested_action": "string — concrete step to address this gap"
    }}
  ],
  "section_improvements": [
    {{
      "section": "string — resume section name",
      "issue": "string — what is wrong or missing",
      "suggestion": "string — specific actionable improvement",
      "reasoning": "string — why this improvement matters for this role"
    }}
  ],
  "bullet_optimizations": [
    {{
      "original_pattern": "string — describes the type of bullet currently present",
      "improved_pattern": "string — describes how bullets should be rewritten",
      "example_before": "string — example of a weak bullet (constructed, not copied)",
      "example_after": "string — improved version",
      "reasoning": "string — why this makes the resume stronger"
    }}
  ],
  "overall_assessment": "string — 2–3 sentence analytical summary of the candidate's fit"
}}

Be specific. Be honest. Be analytical. Return only the JSON object."""


SCORING_PROMPT = """Based on the following resume analysis for a job role, generate a precise alignment score and breakdown.

Analysis Data:
{analysis_data}

JD Data:
{jd_data}

Resume Data:
{resume_data}

Return a JSON object with this exact structure:
{{
  "overall_score": number between 0 and 100,
  "score_label": "string — one of: Poor Fit / Below Average / Average / Good Fit / Strong Fit / Excellent Fit",
  "score_rationale": "string — 1–2 sentence explanation of the score",
  "dimension_scores": {{
    "technical_skills_match": number between 0 and 100,
    "experience_relevance": number between 0 and 100,
    "keyword_coverage": number between 0 and 100,
    "achievement_quality": number between 0 and 100,
    "presentation_quality": number between 0 and 100
  }},
  "hiring_recommendation": "string — one of: Not Recommended / Possible with Development / Worth Interviewing / Strong Candidate / Top Priority",
  "confidence_in_assessment": "High | Medium | Low",
  "top_3_actions": [
    "string — most impactful action to improve alignment",
    "string",
    "string"
  ]
}}

Return only the JSON object. No explanation."""
