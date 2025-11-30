"""ElevenLabs Text-to-Speech integration."""

import os
from elevenlabs import ElevenLabs


def get_client() -> ElevenLabs:
    """Get configured ElevenLabs client."""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY environment variable not set")
    return ElevenLabs(api_key=api_key)


def generate_speech(text: str, voice_id: str) -> bytes:
    """Generate speech audio from text.

    Args:
        text: The text to convert to speech
        voice_id: ElevenLabs voice ID

    Returns:
        Audio bytes (MP3 format)
    """
    client = get_client()

    # Generate audio
    audio_generator = client.text_to_speech.convert(
        voice_id=voice_id,
        text=text,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )

    # Collect all audio chunks
    audio_chunks = []
    for chunk in audio_generator:
        audio_chunks.append(chunk)

    return b"".join(audio_chunks)


def generate_speech_file(text: str, voice_id: str, output_path: str) -> str:
    """Generate speech and save to file.

    Args:
        text: The text to convert to speech
        voice_id: ElevenLabs voice ID
        output_path: Path to save the audio file

    Returns:
        Path to the saved audio file
    """
    audio_bytes = generate_speech(text, voice_id)

    with open(output_path, "wb") as f:
        f.write(audio_bytes)

    return output_path
