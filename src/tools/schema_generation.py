from pydantic.json_schema import GenerateJsonSchema
from typing import Any
from collections import OrderedDict


class MyGenerateJsonSchema(GenerateJsonSchema):
    def generate(self, schema, mode="validation"):
        # Generate the initial schema
        generated_schema = super().generate(schema, mode=mode)

        # Remove all "title" keys recursively
        def remove_titles(obj: Any) -> Any:
            if isinstance(obj, dict):
                return {k: remove_titles(v) for k, v in obj.items() if k != "title"}
            elif isinstance(obj, list):
                return [remove_titles(item) for item in obj]
            return obj
        
        def remove_google_creds(obj: Any) -> Any:
            if isinstance(obj, dict):
                filtered = {
                    k: remove_google_creds(v)
                    for k, v in obj.items()
                    if k != "google_creds_manager"  # Remove the specific key
                }
                # Remove `$defs` for GoogleCredsManager if present
                if "$defs" in filtered and "GoogleCredsManager" in filtered["$defs"]:
                    del filtered["$defs"]["GoogleCredsManager"]
                return filtered
            elif isinstance(obj, list):
                return [remove_google_creds(item) for item in obj]
            return obj
        
        # Reorder fields in the schema
        def reorder_fields(schema_dict: dict) -> OrderedDict:
            # Define the desired order of top-level keys
            key_order = ["name", "type", "description", "properties", "required"]
            reordered = OrderedDict()

            # Add keys in the desired order if they exist
            for key in key_order:
                if key in schema_dict:
                    reordered[key] = schema_dict[key]

            # Add any remaining keys not in the predefined order
            for key, value in schema_dict.items():
                if key not in key_order:
                    reordered[key] = value

            return reordered

        # Apply transformations
        cleaned_schema = remove_titles(generated_schema)
        no_google_creds_schema = remove_google_creds(cleaned_schema)
        reordered_schema = reorder_fields(no_google_creds_schema)

        return reordered_schema
