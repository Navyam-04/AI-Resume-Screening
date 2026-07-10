from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY

from app.database.session import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(150), nullable=False)

    description = Column(Text, nullable=False)

    required_skills = Column(ARRAY(String), nullable=False)

    min_experience_years = Column(
        Integer,
        nullable=False,
        default=0,
    )