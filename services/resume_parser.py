"""
CVAlign Lens — Resume Parser Service
Extracts structured candidate intelligence from raw resume text.
"""

from prompts.prompt_templates import SYSTEM_PROMPT, RESUME_EXTRACTION_PROMPT
from utils.text_processing import clean_text, truncate_text, is_meaningful_text
from utils.llm_client import LLMClient


class ResumeParser:
    """
    Parses a raw resume into structured data for downstream analysis.
    """

    def __init__(self):
        self.llm = LLMClient()

    def parse(self, raw_resume: str) -> dict:
        """
        Parse resume text and return structured candidate intelligence.

        Args:
            raw_resume: Raw resume text.

        Returns:
            dict: Structured resume data.

        Raises:
            ValueError: If the input is insufficient for meaningful parsing.
        """
        cleaned = clean_text(raw_resume)
        truncated = truncate_text(cleaned, max_chars=7000)

        if not is_meaningful_text(truncated, min_words=50):
            raise ValueError(
                "Resume content is too short to analyze meaningfully. "
                "Please provide more complete resume content."
            )

        prompt = RESUME_EXTRACTION_PROMPT.format(resume_text=truncated)
        result = self.llm.call(system_prompt=SYSTEM_PROMPT, user_prompt=prompt)

        return self._validate_and_normalize(result)

    def _validate_and_normalize(self, data: dict) -> dict:
        """
        Ensure all expected fields are present with sensible defaults.
        """
        defaults = {
            "candidate_name": None,
            "inferred_title": "Unknown",
            "years_of_experience": "Unknown",
            "technical_skills": [],
            "soft_skills": [],
            "domain_experience": [],
            "education": [],
            "notable_achievements": [],
            "resume_sections_present": [],
            "missing_sections": [],
            "keywords_present": [],
        }
        for key, default in defaults.items():
            if key not in data or data[key] is None:
                data[key] = default
        return data
