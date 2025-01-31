from typing import Any

from pydantic import BaseModel, Field


class Metadata(BaseModel):
    id: str
    created: int
    model: str