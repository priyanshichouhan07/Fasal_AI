from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def speech_to_text(audio_path):

    with open(audio_path, "rb") as file:

        transcription = client.audio.transcriptions.create(
            file=("audio.ogg", file.read()),
            model="whisper-large-v3",
            response_format="text"
        )

    return transcription