from pydantic import BaseModel


class ResumeUploadResponse(BaseModel):
    original_filename: str
    saved_as: str
    extracted_text: str