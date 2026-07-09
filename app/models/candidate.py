from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from app.database.session import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    experience_years = Column(Integer, nullable=False)
    skills = Column(ARRAY(String), nullable=False)