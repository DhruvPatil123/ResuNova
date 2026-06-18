import re
from typing import Dict, List, Tuple

class ATSScorer:
    def __init__(self):
        # Standard sections that most ATS parsers look for
        self.required_sections = ["Experience", "Education", "Skills", "Summary"]

    def analyze(self, resume_data, job_description: str) -> Dict:
        \"\"\"
        Analyzes the resume against a job description and returns a score and suggestions.
        \"\"\"
        score = 0
        suggestions = []

        # 1. Structural Check (20 points)
        sections_found = 0
        # Basic check: if the data lists aren't empty, we consider the section 'present'
        if resume_data.summary: sections_found += 1
        if resume_data.experience: sections_found += 1
        if resume_data.education: sections_found += 1
        if resume_data.skills: sections_found += 1

        struct_score = (sections_found / len(self.required_sections)) * 20
        score += struct_score
        if sections_found < len(self.required_sections):
            suggestions.append("Add missing standard sections (Summary, Experience, Education, or Skills).")

        # 2. Keyword Matching (40 points)
        # Simple keyword extraction from JD
        jd_keywords = self._extract_keywords(job_description)
        resume_text = self._get_full_resume_text(resume_data)

        matches = 0
        missing_keywords = []
        for kw in jd_keywords:
            if kw.lower() in resume_text.lower():
                matches += 1
            else:
                missing_keywords.append(kw)

        if jd_keywords:
            match_ratio = matches / len(jd_keywords)
            score += match_ratio * 40
            if match_ratio < 0.7:
                suggestions.append(f"Integrate these key skills from the JD: {', '.join(missing_keywords[:5])}")
        else:
            score += 40 # No JD provided, give full points for this section or neutral
            suggestions.append("Paste a job description to get an accurate keyword match score.")

        # 3. Impact Metric Density (40 points)
        # Count occurrences of numbers, %, $, etc. in experience bullets
        metric_count = 0
        total_bullets = 0

        metric_pattern = re.compile(r'(\d+%|\$\d+|increased|decreased|saved|managed|led|achieved)')

        for exp in resume_data.experience:
            for bullet in exp.description:
                total_bullets += 1
                if metric_pattern.search(bullet.lower()):
                    metric_count += 1

        if total_bullets > 0:
            metric_ratio = metric_count / total_bullets
            score += metric_ratio * 40
            if metric_ratio < 0.5:
                suggestions.append("Quantify your achievements. Use more numbers, percentages, and dollar amounts.")
        else:
            suggestions.append("Add work experience to analyze your impact metrics.")

        return {
            "score": round(score),
            "suggestions": suggestions,
            "breakdown": {
                "structure": round(struct_score),
                "keywords": round((matches / len(jd_keywords) * 40) if jd_keywords else 40),
                "metrics": round((metric_count / total_bullets * 40) if total_bullets > 0 else 0)
            }
        }

    def _extract_keywords(self, text: str) -> List[str]:
        \"\"\"Very basic keyword extraction (can be improved with spaCy/NLTK)\"\"\"
        # Simple approach: Split by comma/space and filter common words
        # In a real app, this would be a list of industry-standard skills
        words = re.findall(r'\b\w{3,}\b', text.lower())
        common_stop_words = {'the', 'and', 'with', 'this', 'that', 'from', 'their', 'will'}
        # Filter for potentially 'skill-like' words (longer, non-common)
        # This is a placeholder for a proper NER (Named Entity Recognition) system
        potential_keywords = [w for w in words if w not in common_stop_words]
        # Return top 10 most frequent as a proxy for importance
        from collections import Counter
        counts = Counter(potential_keywords)
        return [word for word, count in counts.most_common(10)]

    def _get_full_resume_text(self, resume_data) -> str:
        text = resume_data.summary + " "
        for exp in resume_data.experience:
            text += f" {exp.role} {exp.company} " + " ".join(exp.description)
        text += " " + " ".join(resume_data.skills)
        return text
