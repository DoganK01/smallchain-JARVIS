from abc import ABC, abstractmethod
from typing import (
    Any,
    Annotated,
    Literal,
    Optional,
    TypedDict,
    Union,
    Dict,
    cast,
)

from pydantic import BaseModel, ConfigDict, Field, SkipValidation
from pydantic.fields import FieldInfo
from typing_extensions import NotRequired


class AsyncBaseTool(BaseModel, ABC):

    args_schema: Annotated[Optional[Dict[str, Any]], "Dict value to be used in json format for prompt"] = Field(
    default=None, description="Json schema for the tool."
    )

    metadata: Annotated[Optional[Dict[str, Any]], "Metadatas. A dict value"] = Field(
    default=None, description="Metadata for the tool."
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)



    async def arun(self):
        return await self._arun()
    

    @abstractmethod
    async def _arun(self):
        pass

