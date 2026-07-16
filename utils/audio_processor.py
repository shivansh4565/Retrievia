import os
import subprocess
import yt_dlp

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_youtube_audio(url: str) -> str:
    """
    Download YouTube audio directly as 16kHz mono WAV.
    """

    output_template = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

    base = os.path.splitext(filename)[0]
    wav_path = base + ".wav"

    return convert_to_wav(wav_path)


def convert_to_wav(input_path: str) -> str:
    """
    Convert any audio/video file into
    mono 16kHz WAV using ffmpeg.
    """

    output_path = os.path.splitext(input_path)[0] + "_converted.wav"

    command = [
        "ffmpeg",
        "-y",
        "-i",
        input_path,
        "-ac",
        "1",
        "-ar",
        "16000",
        output_path,
    ]

    subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )

    return output_path


def chunk_audio(wav_path: str, chunk_minutes: int = 10):
    """
    Split WAV into equal chunks using ffmpeg.
    """

    chunk_seconds = chunk_minutes * 60

    output_pattern = wav_path.replace(".wav", "_chunk_%03d.wav")

    command = [
        "ffmpeg",
        "-y",
        "-i",
        wav_path,
        "-f",
        "segment",
        "-segment_time",
        str(chunk_seconds),
        "-c",
        "copy",
        output_pattern,
    ]

    subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )

    chunks = []
    index = 0

    while True:
        path = wav_path.replace(".wav", f"_chunk_{index:03d}.wav")
        if not os.path.exists(path):
            break
        chunks.append(path)
        index += 1

    return chunks


def process_input(source: str):

    if source.startswith(("http://", "https://")):
        print("Downloading YouTube audio...")
        wav_path = download_youtube_audio(source)
    else:
        print("Converting local file...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)

    print(f"Created {len(chunks)} chunks.")

    return chunks
