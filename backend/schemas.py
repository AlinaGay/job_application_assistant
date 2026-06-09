"""Pydantic schemas for structured LLM outputs.
These schemas validate the JSON returned by the LLM and serve as a
single source of truth for the resume template contract.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Annotated


class ExperinceItem(BaseModel):
    name: str = Field(..., min_length=1, max_length=80)
    description: str = Field(..., min_length=20, max_length=300)
