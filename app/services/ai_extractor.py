from functools import lru_cache

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from app.schemas.extraction import ExtractedResumeData

load_dotenv()

EXTRACTION_PROMPT = """
You are an AI resume parser.

Extract the following information from the resume.

- Full Name
- Email
- Total Years of Experience
- Skills

If something is missing, leave it blank instead of guessing.

Resume:

{resume_text}
"""


@lru_cache
def _get_structured_llm():
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
    )

    return llm.with_structured_output(ExtractedResumeData)


def extract_candidate_info(resume_text: str) -> ExtractedResumeData:
    structured_llm = _get_structured_llm()

    prompt = EXTRACTION_PROMPT.format(
        resume_text=resume_text
    )

    return structured_llm.invoke(prompt)