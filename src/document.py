from abc import ABC
from typing import (
    Any,
    Literal,
    Optional,
    TypedDict,
    Union,
    cast,
)
from pydantic import BaseModel, Field
import torch


class Document(BaseModel):

    page_content: str
    id: Optional[int] = None
    metadata: dict = Field(default_factory=dict)
    embeddings: torch.Tensor = Field(default_factory=torch.Tensor)

    class Config:
        arbitrary_types_allowed = True
    
    # ensures that the validation works
    def __init__(self, page_content: str, **kwargs: Any) -> None:
        super().__init__(page_content=page_content, **kwargs)


    def get_vars_as_dict(self, exclude_none: bool = False) -> dict:
        """
        Returns the instance's variables as a dictionary, with optional filtering.
        :param exclude_none: If True, exclude fields with None values.
        """
        return self.model_dump(exclude_none=exclude_none)
    


docs = Document(page_content="Hi", metadata={"author": "John"})

print(docs.embeddings)
print(type(docs.embeddings))