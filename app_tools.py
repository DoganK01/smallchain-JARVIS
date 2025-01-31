import os
from time import perf_counter
from typing import Any
from uuid import uuid4
import asyncio

from openai import AsyncAzureOpenAI
from loguru import logger
from rich.console import Console
from termcolor import colored

from src.tools.google_tools.google_maps_tool import GoogleMapsTool
from src.tools.get_weather import WeatherTool
from src.tools.utils import prepare_schemas
from src.tools.google_tools.google_tools_executors import GmailReadTool, GmailSendTool, CalendarReadTool, CalendarInsertTool
from src.settings import settings
from src.tools.google_tools.credentials import GoogleCredsManager
from src.prompts import generate_prompt
from src.visualizer import Visualizer
from src.tts import TextToSpeech
from src.stt import SpeechToText
from src.astream import ahandle_stream, extract_tool_input_args
from src.persistence import save_json_chat_history

console = Console()

google_creds_manager = GoogleCredsManager()

whisper_client = AsyncAzureOpenAI(
    api_key=settings.AZURE_OPENAI_WHISPER_API_KEY,
    api_version=settings.AZURE_OPENAI_WHISPER_API_VERSION,
    azure_endpoint=settings.AZURE_OPENAI_WHISPER_ENDPOINT
) 

tts_client = AsyncAzureOpenAI(api_key=settings.AZURE_OPENAI_TTS_API_KEY,
                              api_version=settings.AZURE_OPENAI_TTS_API_VERSION,
                              azure_endpoint=settings.AZURE_OPENAI_TTS_ENDPOINT)

azure_openai_client = AsyncAzureOpenAI(api_key=settings.AZURE_OPENAI_GPT_API_KEY,
                                  api_version=settings.AZURE_OPENAI_GPT_API_VERSION,
                                  azure_endpoint=settings.AZURE_OPENAI_GPT_ENDPOINT
                                  )

tts = TextToSpeech(client=tts_client)
stt = SpeechToText()

google_cred_tools: dict[str, Any] = {
    "read_gmail_emails": GmailReadTool,
    "send_gmail_email": GmailSendTool,
    "get_calendar_appointments": CalendarReadTool,
    "insert_calendar_appointment": CalendarInsertTool
}

other_tools: dict[str, Any] = {
    "google_maps": GoogleMapsTool,
    "get_weather_data": WeatherTool,
}

google_creds_manager = GoogleCredsManager()

SYSTEM_PROMPT: str = generate_prompt(prepare_schemas(models=[*other_tools.values(), *google_cred_tools.values()]))


def fancy_print(prompt: str, role: str):
    """Prints user input with a typing effect and styling."""
    console.print(f"[bold cyan]{role} >[/bold cyan] {prompt}", end=" ", style="cyan", highlight=False)

async def main():
    visualizer: Visualizer = Visualizer(video_path="orb.mp4")
    asyncio.create_task(visualizer._run_video_loop())
    await asyncio.sleep(3)

    conversation_id: str = str(uuid4())
    logger.info("Starting conversation with ID: {id}", id=conversation_id)

    chat_history: dict[str, Any] = {
        "conversation_id": conversation_id,
        "content": [],
    }

    messages: list[dict[str, str]] = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
    ]
    os.system("clear")

    while True:
        
        if not (user_prompt := await stt.listen_for_speech(whisper_client)):
            continue
        fancy_print(user_prompt, "You")

        if user_prompt.lower().strip() in ("exit", "quit"):
            break

        messages.append({"role": "user", "content": user_prompt})

        logger.info("Azure OpenAI Service generating response...")
        _now: float = perf_counter()
        stream_response = await azure_openai_client.chat.completions.create(model="gpt-4o-attention-project",
                                            messages=messages,
                                            stream=True)
        print("STREAM RESPONSEEEEEEEEE 1: ", stream_response)
        logger.info("Azure OpenAI Service generation time: {s:.3f} seconds", s=perf_counter() - _now)
        print(colored("Assistant > ", "green"), end="", flush=True)
        
        extracted_response, metadata, tool_calls = await ahandle_stream(stream_response)
        print("Tool Callllss: ", tool_calls)

        messages.append({"role": "assistant", "content": extracted_response})

        if tool_calls:
            logger.info("tool call: {r}", r=extracted_response.removeprefix("<tool>").removesuffix("</tool>"))
            tool_args: dict[str, Any] = extract_tool_input_args(input=extracted_response)
            tool_name: str = tool_args.get("name")
            tool_inputs: dict[str, Any] = tool_args.get("parameters")

            if tool_name in google_cred_tools:
                tool_inputs["google_creds_manager"] = google_creds_manager
                tool_output: Any = await google_cred_tools.get(tool_name)(**tool_inputs).arun()
            else:
                tool_output: Any = await other_tools.get(tool_name)(**tool_inputs).arun()
            print("TOOL OUTPUT: ",tool_output)
            logger.info("Tool output: {o}", o=tool_output)
            messages.append({"role": "user", "content": user_prompt+"\n\n"+str(tool_output)})
            chat_history["content"].append({"messages": messages.copy(), **metadata.model_dump()})
            save_json_chat_history(conversation_id=conversation_id, chat_history=chat_history)


            logger.info("Azure OpenAI Service generating response...")
            _now: float = perf_counter()
            stream_response = await azure_openai_client.chat.completions.create(model="gpt-4o-attention-project",
                                                messages=messages,
                                                stream=True)
            print("STREAM RESPONSEEEEEEEEE 2: ", stream_response)
            logger.info("Azure OpenAI Service generation time: {s:.3f} seconds", s=perf_counter() - _now)
            print(colored("Assistant > ", "green"), end="", flush=True)
            
            extracted_response, metadata, _ = await ahandle_stream(stream_response)

        else:
            logger.info("There is no tool call")
        
        await tts.stream_text_to_speech(text=extracted_response, visualizer=visualizer)

        print()
        chat_history["content"].append({"messages": messages.copy(), **metadata.model_dump()})
        save_json_chat_history(conversation_id=conversation_id, chat_history=chat_history)

if __name__ == "__main__":

    asyncio.run(main())
