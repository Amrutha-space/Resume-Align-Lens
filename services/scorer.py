"""
CVAlign Lens — Scorer Service
Generates a precise role alignment score and dimensional breakdown.
"""

import json
from prompts.prompt_templates import SYSTEM_PROMPT, SCORING_PROMPT
from utils.llm_client import LLMClient


class Scorer:
    """
    Produces a calibrated alignment score based on the full analysis context.
    """

    def __init__(self):
        self.llm = LLMClient()

    def score(self, analysis: dict, jd_data: dict = None, resume_data: dict = None) -> dict:
        """
        Generate an alignment score from analysis data.

        Args:
            analysis: Full analysis result from Analyzer.
            jd_data: Optional JD data for deeper scoring context.
            resume_data: Optional resume data for deeper scoring context.

        Returns:
            dict: Score data with overall score, dimension breakdown, and recommendations.
        """
        prompt = SCORING_PROMPT.format(
            analysis_data=json.dumps(analysis, indent=2),
            jd_data=json.dumps(jd_data or {}, indent=2),
            resume_data=json.dumps(resume_data or {}, indent=2),
        )

        result = self.llm.call(system_prompt=SYSTEM_PROMPT, user_prompt=prompt)
        return self._validate_and_normalize(result)

    def _validate_and_normalize(self, data: dict) -> dict:
        """
        Ensure scoring data is complete and numerically bounded.
        """
        # Clamp overall score
        if "overall_score" in data:
            data["overall_score"] = max(0, min(100, int(data.get("overall_score", 0))))
        else:
            data["overall_score"] = 0

        defaults = {
            "score_label": "Unknown",
            "score_rationale": "Score could not be determined.",
            "dimension_scores": {
                "technical_skills_match": 0,
                "experience_relevance": 0,
                "keyword_coverage": 0,
                "achievement_quality": 0,
                "presentation_quality": 0,
            },
            "hiring_recommendation": "Not Recommended",
            "confidence_in_assessment": "Low",
            "top_3_actions": [],
        }

        for key, default in defaults.items():
            if key not in data or data[key] is None:
                data[key] = default

        # Clamp dimension scores
        if isinstance(data.get("dimension_scores"), dict):
            for dim_key in data["dimension_scores"]:
                raw = data["dimension_scores"][dim_key]
                try:
                    data["dimension_scores"][dim_key] = max(0, min(100, int(raw)))
                except (TypeError, ValueError):
                    data["dimension_scores"][dim_key] = 0

        return data
