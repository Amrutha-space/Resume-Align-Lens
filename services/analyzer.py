import json
from prompts.prompt_templates import SYSTEM_PROMPT, ANALYSIS_PROMPT
from utils.llm_client import LLMClient


class Analyzer:
  
    def __init__(self):
        self.llm = LLMClient()

    def analyze(self, jd_data: dict, resume_data: dict) -> dict:

        prompt = ANALYSIS_PROMPT.format(
            jd_data=json.dumps(jd_data, indent=2),
            resume_data=json.dumps(resume_data, indent=2),
        )

        result = self.llm.call(system_prompt=SYSTEM_PROMPT, user_prompt=prompt)
        return self._validate_and_normalize(result)

    def _validate_and_normalize(self, data: dict) -> dict:
        
        #Ensure all analysis fields are present and properly structured.
        
        defaults = {
            "strengths": [],
            "weaknesses": [],
            "missing_keywords": [],
            "skill_gaps": [],
            "section_improvements": [],
            "bullet_optimizations": [],
            "overall_assessment": "Analysis could not be completed for this input.",
        }
        for key, default in defaults.items():
            if key not in data or data[key] is None:
                data[key] = default

        # recheck list of items — ensure each is a dict
        list_fields = [
            "strengths", "weaknesses", "missing_keywords",
            "skill_gaps", "section_improvements", "bullet_optimizations"
        ]
        for field in list_fields:
            if not isinstance(data[field], list):
                data[field] = []

        return data
