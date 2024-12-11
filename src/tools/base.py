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
    name: str
    description: str

    args_schema: Annotated[Optional[Dict[str, Any]], "Dict value to be used in json format for prompt"] = Field(
    default=None, description="The tool schema."
    )

    metadata: Annotated[Optional[Dict[str, Any]], "Metadatas. A dict value"] = Field(
    default=None, description="Metadata."
    )


    def __init__(self, name, description, **kwargs):
        super().__init__(name=name, description=description, **kwargs)
        print("PRINTING KWARGSSS")
        print(kwargs)


    async def arun(self):
        return self._arun
    

    @abstractmethod
    async def _arun(self):
        pass



#obj = AsyncBaseTool(name="Allah", description="Some tool descp")

#print(obj.metadata)
