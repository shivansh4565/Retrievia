import os
import requests
import whisper
from dotenv import load_dotenv
from pydub import AudioSegment

# Load .env
load_dotenv()

# Sarvam sync API accepts <=30s audio
SARVAM_PIECE_SECONDS = 25

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")
SARVAM_STT_TRANSLATE_URL = "https://api.sarvam.ai/speech-to-text-translate"
SARVAM_MODEL = os.getenv("SARVAM_STT_MODEL", "saaras:v2.5")

_model = None


def load_model():
    global _model

    if _model is None:
        print(f"Loading Whisper model: {WHISPER_MODEL}...")
        _model = whisper.load_model(WHISPER_MODEL)
        print("Whisper model loaded.")

    return _model


def transcribe_chunk_whisper(chunk_path: str) -> str:
    model = load_model()
    result = model.transcribe(chunk_path, task="transcribe")
    return result["text"]


def _get_sarvam_key():
    api_key = os.getenv("SARVAM_API_KEY")

    if not api_key:
        raise RuntimeError(
            "SARVAM_API_KEY not found. Check your .env file."
        )

    return api_key


def _send_to_sarvam(piece_path: str) -> str:
    headers = {
        "api-subscription-key": _get_sarvam_key()
    }

    with open(piece_path, "rb") as f:
        files = {
            "file": (
                os.path.basename(piece_path),
                f,
                "audio/wav"
            )
        }

        data = {
            "model": SARVAM_MODEL,
            "with_diarization": "false"
        }

        response = requests.post(
            SARVAM_STT_TRANSLATE_URL,
            headers=headers,
            files=files,
            data=data,
            timeout=120
        )

    if not response.ok:
        print(f"Status Code: {response.status_code}")
        print(response.text)
        response.raise_for_status()

    return response.json().get("transcript", "")


def transcribe_chunk_sarvam(chunk_path: str) -> str:
    audio = AudioSegment.from_wav(chunk_path)

    piece_ms = SARVAM_PIECE_SECONDS * 1000

    transcript = ""

    for i, start in enumerate(range(0, len(audio), piece_ms)):
        piece = audio[start:start + piece_ms]

        piece_path = f"{chunk_path}_part_{i}.wav"

        piece.export(piece_path, format="wav")

        try:
            print(f"Uploading piece {i + 1}...")
            transcript += _send_to_sarvam(piece_path) + " "
        finally:
            if os.path.exists(piece_path):
                os.remove(piece_path)

    return transcript.strip()


def transcribe_chunk(chunk_path: str, language="english"):
    language = language.lower()

    if language == "hinglish":
        return transcribe_chunk_sarvam(chunk_path)

    return transcribe_chunk_whisper(chunk_path)


def transcribe_all(chunks, language="english"):
    print(
        f"Using {'Sarvam AI' if language.lower()=='hinglish' else 'Whisper'}"
    )

    transcript = ""

    for i, chunk in enumerate(chunks):
        print(f"Transcribing chunk {i+1}/{len(chunks)}")
        transcript += transcribe_chunk(chunk, language) + " "

    print("Transcription complete.")

    return transcript.strip()