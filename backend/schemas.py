"""Pydantic schemas for structured LLM outputs.
These schemas validate the JSON returned by the LLM and serve as a
single source of truth for the resume template contract.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Annotated


class ExperinceItem(BaseModel):
    """A single project entry shown in the EXPERIENCE section of the CV."""
    name: str = Field(..., min_length=1, max_length=80)
    description: str = Field(..., min_length=20, max_length=300)


class FilledResume(BaseModel):
    """Validated LLM output used to placeholders in the resume template."""
    job_position: Annotated[
        str, Field(alias="JOB_POSITION", min_length=1, max_length=80)]
    summary: Annotated[
        str, Field(alias="SUMMARY", min_length=30, max_length=500)]
    experience: Annotated[
        list[ExperinceItem],
        Field(alias="EXPERIENCE", min_length=3, max_length=3)]

    @field_validator("summary")
    @classmethod
    def must_start_with_phrase(cls, text: str) -> str:
        if not text.startswith("with experience in "):
            raise ValueError("SUMMARY must start with 'with experience in '")
        return text

    model_config = {"populate_by_name": True}
