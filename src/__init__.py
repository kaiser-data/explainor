"""Explainor - AI agent that explains topics in persona voices."""

from .personas import PERSONAS, get_persona, get_persona_names
from .agent import run_agent, research_topic
from .tts import generate_speech, generate_speech_file

__all__ = [
    "PERSONAS",
    "get_persona",
    "get_persona_names",
    "run_agent",
    "research_topic",
    "generate_speech",
    "generate_speech_file",
]
