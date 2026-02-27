"""
CVAlign Lens — Job Description Parser Service
Extracts structured intelligence from raw job description text.
"""

import json
from prompts.prompt_templates import SYSTEM_PROMPT, JD_EXTRACTION_PROMPT
from utils.text_processing import clean_text, truncate_text, is_meaningful_text
from utils.llm_client import LLMClient


class JDParser:
    """
    Parses a raw job description into structured data for downstream analysis.
    """

    def __init__(self):
        self.llm = LLMClient()

    def parse(self, raw_jd: str) -> dict:
        """
        Parse a job description and return structured JD intelligence.

        Args:
            raw_jd: Raw job description text.

        Returns:
            dict: Structured JD data.

        Raises:
            ValueError: If the input is insufficient for meaningful parsing.
        """
        cleaned = clean_text(raw_jd)
        truncated = truncate_text(cleaned, max_chars=6000)

        if not is_meaningful_text(truncated, min_words=20):
            raise ValueError(
                "Job description is too short or lacks meaningful content. "
                "Please provide a complete job description."
            )

        prompt = JD_EXTRACTION_PROMPT.format(job_description=truncated)
        result = self.llm.call(system_prompt=SYSTEM_PROMPT, user_prompt=prompt)

        return self._validate_and_normalize(result)

    def _validate_and_normalize(self, data: dict) -> dict:
        """
        Ensure all expected fields are present with sensible defaults.
        """
        defaults = {
            "role_title": "Unknown Role",
            "seniority_level": "Unknown",
            "core_technical_skills": [],
            "soft_skills": [],
            "domain_knowledge": [],
            "key_responsibilities": [],
            "must_have_requirements": [],
            "nice_to_have_requirements": [],
            "keywords_for_ats": [],
        }
        for key, default in defaults.items():
            if key not in data or data[key] is None:
                data[key] = default
        return data
