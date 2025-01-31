from typing import Any, Dict, List, Union
import json

from openai import AsyncStream
from termcolor import colored

from src.metadata import Metadata


from typing import Any, Dict, Union

def extract_tool_input_args(input: str) -> Dict[str, Any]:
    """
    Extracts and processes tool input arguments from the model response, ensuring any embedded
    JSON strings within the data are parsed recursively.

    Args:
        s (str): The input string containing the content, which is expected to have "<tool>" 
                 and "</tool>" tags enclosing the data.

    Returns:
        Dict[str, Any]: The parsed tool input arguments, with any JSON strings recursively decoded.
    
    Raises:
        ValueError: If the input string does not contain valid JSON data within the <tool> tags.
    """
    # Strip the <tool> and </tool> tags and attempt to load the data
    try:
        data = json.loads(input.removeprefix("<tool>").removesuffix("</tool>"))
    except json.JSONDecodeError as e:
        raise ValueError("The content inside the <tool> tags is not valid JSON.") from e

    def parse_embedded_json(value: Union[str, Dict, List, Any]) -> Any:
        """
        Recursively parses strings that are valid JSON, returning the parsed object if applicable.

        Args:
            value (Union[str, Dict, List, Any]): The value to inspect and possibly decode.

        Returns:
            Any: The original value if not a JSON string, or the parsed JSON object if applicable.
        """
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        elif isinstance(value, dict):
            return {k: parse_embedded_json(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [parse_embedded_json(v) for v in value]
        else:
            return value

    return parse_embedded_json(data)



async def ahandle_stream(stream: AsyncStream, verbose: bool = True) -> tuple[str, Metadata, bool]:
    response: list[str] = []
    tool_calls: bool = False

    async for chunk in stream:
        if not chunk.choices:

            metadata: Metadata = Metadata(
                **chunk.model_dump()
            )
        elif token := chunk.choices[0].delta.content:
            response.append(token)
            if "<tool>" in "".join(response):
                tool_calls = True
                print(colored("Thinking ...", "yellow"), end="", flush=True)

            elif verbose and not tool_calls:
                # When the stream message stops. This is the n-1 chunk.
                print(colored(token, "blue"), end="", flush=True)
        
        else:
            print(colored("Generating ended", "red"), end="", flush=True)
    return "".join(response), metadata, tool_calls