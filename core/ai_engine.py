import os
from openai import OpenAI
import streamlit as st
from typing import List, Optional
from data.schema import Experience
from functools import lru_cache

class AIEngine:
    def __init__(self, api_key: Optional[str] = None):
        # Priority: Passed Key -> Streamlit Secrets -> Environment Variable
        self.api_key = api_key or st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)

    def is_ready(self) -> bool:
        return self.client is not None

    @lru_cache(maxsize=100)
    def _generate_response(self, prompt: str, model: str = "gpt-4o-mini") -> str:
        if not self.is_ready():
            return "⚠️ API Key missing. Please provide a key to use AI features."

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert career coach and ATS optimization specialist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error: {str(e)}"

    def quantify_bullet(self, bullet: str) -> str:
        """Transforms a duty into a quantified achievement."""
        prompt = f"""
        Transform the following resume bullet point into a high-impact, quantified achievement.

        Guidelines:
        - Add plausible metrics (%, $, time, numbers) if the context allows.
        - Use strong action verbs (e.g., 'Spearheaded', 'Optimized', 'Engineered').
        - Keep it truthful but impressive.
        - Return ONLY the rewritten bullet point.

        Bullet: {bullet}
        """
        return self._generate_response(prompt)

    def polish_wording(self, text: str, tone: str = "Confident") -> str:
        """Rewrites text for better recruiter appeal based on tone."""
        prompt = f"""
        Rewrite the following professional summary or experience section to be more recruiter-friendly.
        Tone: {tone}

        Guidelines:
        - Remove passive language.
        - Ensure parallel structure.
        - Use industry-standard terminology.
        - Return the polished version.

        Text: {text}
        """
        return self._generate_response(prompt)

    def rewrite_experience_for_jd(self, experience_list: List[Experience], job_description: str, tone: str = "Confident") -> List[Experience]:
        """Rewrites the entire experience list to align with a specific job description."""
        if not self.is_ready():
            return experience_list

        current_resumes_text = ""
        for exp in experience_list:
            current_resumes_text += f"Role: {exp.role}, Company: {exp.company}\nBullets: {'\n'.join(exp.description)}\n\n"

        prompt = f"""
        You are an expert resume writer. Rewrite the following professional experience to align perfectly with the provided Job Description.

        Job Description: {job_description}

        Current Experience:
        {current_resumes_text}

        Guidelines:
        - Use a {tone} tone.
        - Integrate critical keywords from the JD.
        - Maintain the truthfulness of the original roles.
        - Rewrite bullet points to be impact-driven and quantified.
        - Format the response as a JSON array of objects with keys: 'role', 'company', 'location', 'start_date', 'end_date', 'description' (as an array of strings).

        Return ONLY valid JSON.
        """

        response = self._generate_response(prompt, model="gpt-4o")
        try:
            import json
            # Clean JSON markers if GPT included them
            clean_json = response.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        except Exception:
            return experience_list # Fallback to original if parsing fails
