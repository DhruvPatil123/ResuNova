import PyPDF2
import json
from data.schema import ResumeData, Experience, Education

class ResumeParser:
    @staticmethod
    def parse_pdf(file_stream) -> dict:
        """
        Very basic PDF to text conversion.
        In a production app, this would use more advanced NLP (like spaCy)
        to map extracted text to the ResumeData schema.
        """
        reader = PyPDF2.PdfReader(file_stream)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\\n"

        # Placeholder logic: we return a dictionary that can be used to populate ResumeData
        # Real parsing requires complex regex/NER
        return {
            "full_name": "Extracted Name", # Placeholder
            "summary": text[:500] + "...", # First 500 chars as summary
            "raw_text": text
        }

    @staticmethod
    def parse_json(json_data) -> ResumeData:
        """Parses a JSON string into a ResumeData object."""
        try:
            data = json.loads(json_data)
            return ResumeData(**data)
        except Exception as e:
            print(f"JSON Parse Error: {e}")
            return ResumeData()
