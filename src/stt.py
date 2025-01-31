import os
import tempfile
import pyaudio
from typing import List, Optional
from loguru import logger
from openai import AsyncAzureOpenAI
#from pynput import keyboard
import msvcrt
import wave
import asyncio
from src.settings import settings


CHANNELS: int = 1
FORMAT: int = pyaudio.paInt16
RATE: int = 16000
FRAMES_PER_BUFFER: int = 1024


class SpeechToText:
    def __init__(self, model: str = 'whisper', rate: int = 16000, channels: int = 1):
        self.model = model
        self.audio_stream = pyaudio.PyAudio()
        self.is_recording = True
        self.rate = rate
        self.channels = channels
        #self.listener = keyboard.Listener(on_press=self.on_key_press)
        #self.listener.start()

    def on_key_press(self, key):
        """Listen for key presses to stop the recording."""
        try:
            if key.char == 's':  # Stop the recording loop when 's' is pressed
                self.is_recording = False
                logger.info("Recording stopped.")
        except AttributeError:
            pass  # Ignore other key events

    async def listen_for_speech(self, client: AsyncAzureOpenAI, timeout: int = 20) -> Optional[str]:
        """Capture and transcribe speech asynchronously."""
        frames: List[bytes] = []
        temp_filename = None
        stream = None
        
        # Save recorded audio to a temporary WAV file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
            temp_filename: str = temp_audio.name
        try:
            # Start recording audio
            stream = self.audio_stream.open(format=FORMAT,
                                            channels=self.channels,
                                            rate=self.rate,
                                            input=True,
                                            frames_per_buffer=FRAMES_PER_BUFFER,
                                            start=False)
            stream.start_stream()
            
            logger.info("Recording audio...")
            for _ in range(0, int(self.rate / FRAMES_PER_BUFFER * timeout)):  # Recording for x seconds
                data = stream.read(FRAMES_PER_BUFFER)
                frames.append(data)
                await asyncio.sleep(0)

                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    if key == b'\r':
                        break

            stream.stop_stream()
            stream.close()

    
            with wave.open(temp_filename, "wb") as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(self.audio_stream.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b"".join(frames))
                #print(frames[0])

            # Transcribe the audio file using OpenAI's Whisper model
            with open(temp_filename, "rb") as audio_file:
                transcription: str = await client.audio.transcriptions.create(
                    model=self.model, file=audio_file, response_format="text", temperature=0.0
                )

            return transcription

        except Exception as e:
            logger.error(f"Error capturing voice: {e}", e=e)
            return None

        finally:
            # Clean up temporary file
            if temp_filename and os.path.exists(temp_filename):
                os.remove(temp_filename)
            logger.info("Temporary audio file cleaned up.")

async def main():
    whisper_client = AsyncAzureOpenAI(
        api_key=settings.AZURE_OPENAI_WHISPER_API_KEY,
        api_version=settings.AZURE_OPENAI_WHISPER_API_VERSION,
        azure_endpoint=settings.AZURE_OPENAI_WHISPER_ENDPOINT
    )
    stt = SpeechToText()
    
    try:
        while True:
            transcription = await stt.listen_for_speech(whisper_client)
            if transcription:
                if transcription.lower() in ("exit", "quit"):
                    break
                logger.info(f"Transcription: {transcription}")
            else:
                logger.error("No transcription received.")
    finally:
        stt.audio_stream.terminate()
        logger.info("PyAudio resources cleaned up")

if __name__ == "__main__":
    asyncio.run(main())    
