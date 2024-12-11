from pydantic.json_schema import GenerateJsonSchema
from typing import Any


class MyGenerateJsonSchema(GenerateJsonSchema):
    def generate(self, schema, mode="validation"):
        return super().generate(schema, mode=mode)



