import pyaudio
from openai import AsyncAzureOpenAI
from typing import Optional
from loguru import logger
import asyncio

from src.settings import settings
from src.visualizer import Visualizer


class TextToSpeech:
    """
    A class to asynchronously stream OpenAI Text-to-Speech output in real-time using PyAudio.
    """

<<<<<<< HEAD
    def __init__(self, client: AsyncAzureOpenAI, model: str = "tts-1", voice: str = "nova", rate: int = 15500):
=======
    def __init__(self, client: AsyncAzureOpenAI, model: str = "tts-1", voice: str = "nova", rate: int = 15000):
>>>>>>> 8408410155300391741746111fec68794621c62e
        """
        Initialize the AsyncRealTimeTTSPlayer.

        Args:
            model (str): The TTS model to use. Default is 'tts-1'.
            voice (str): The voice to use for synthesis. Default is 'alloy'.
            rate (int): The audio sampling rate in Hz. Default is 24000.
        """
        self.client = client
        self.model = model
        self.voice = voice
        self.rate = rate
        self.audio_player = pyaudio.PyAudio()
        self.stream = self.audio_player.open(format=pyaudio.paInt16, channels=1, rate=self.rate, output=True)

    async def stream_text_to_speech(self, text: str, visualizer: Visualizer) -> None:
        """
        Asynchronously stream OpenAI TTS audio output and play it in real-time.

        Args:
            text (str): The input text to be synthesized.
        """
        logger.info(f"Starting TTS streaming for text: {text[:100]}...")  # Log a preview of the text
        try:
            # Initialize the streaming response from OpenAI
            async with self.client.audio.speech.with_streaming_response.create(
                model=self.model,
                voice=self.voice,
                response_format="pcm",  # PCM audio format
                input=text,
            ) as response:
                logger.info(f"Response Status Code: {response.status_code}")
                logger.info("Streaming audio...")
                # Play audio chunks as they are streamed
                if response.status_code == 200:
                    visualizer.audio_detected = True
                    logger.info("Audio data received.")
                    async for chunk in response.iter_bytes(chunk_size=1024):
                        #self.stream.write(chunk)
                        await asyncio.to_thread(self.stream.write, chunk)
            if not visualizer.audio_detected:
                logger.warning("No audio data was received during TTS streaming.")
            visualizer.audio_detected=False
        except Exception as e:
            logger.error(f"Error during TTS streaming: {e}")
        finally:
            logger.info("TTS streaming finished.")

    async def close(self) -> None:
        """
        Close the audio stream and release resources asynchronously.
        """
        logger.info("Closing audio stream and resources.")
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.audio_player.terminate()

# Example usage
async def main():
    try:
        visualizer = Visualizer("orb.mp4")
        asyncio.create_task(visualizer._run_video_loop())
        tts_client = AsyncAzureOpenAI(api_key=settings.AZURE_OPENAI_TTS_API_KEY, api_version=settings.AZURE_OPENAI_TTS_API_VERSION, azure_endpoint=settings.AZURE_OPENAI_TTS_ENDPOINT)
        tts_player = TextToSpeech(client=tts_client)

        sample_text = """
        Hi, this is Dogan under a blue sky. I love you su much.
        """
        await tts_player.stream_text_to_speech(sample_text, visualizer=visualizer)
        ### Testing some logic
        for number in range(10):
            print(f"Received: {number}")
            await asyncio.sleep(1)
        #####
    finally:
        await tts_player.close()


if __name__ == "__main__":
    asyncio.run(main())
