"""Explainor - AI Agent that explains any topic in fun persona voices.

MCP's 1st Birthday Hackathon Submission
Track: MCP in Action (Creative)
Team: kaiser-data
"""

import os
import tempfile
import gradio as gr
from dotenv import load_dotenv

from src.personas import PERSONAS, get_persona_names, get_persona
from src.agent import run_agent
from src.tts import generate_speech

# Load environment variables
load_dotenv()


def format_sources(sources: list[dict]) -> str:
    """Format sources as markdown."""
    if not sources:
        return "*No external sources used*"

    md = ""
    for i, src in enumerate(sources, 1):
        if src.get("url"):
            md += f"{i}. [{src['title']}]({src['url']})\n"
        else:
            md += f"{i}. {src['title']} ({src.get('source', 'General')})\n"
    return md


def explain_topic(topic: str, persona_name: str, progress=gr.Progress()):
    """Main function to explain a topic in a persona's voice.

    Returns: (explanation_text, audio_path, sources_md, steps_md)
    """
    if not topic.strip():
        return (
            "Please enter a topic to explain!",
            None,
            "",
            "❌ No topic provided",
        )

    if not persona_name:
        persona_name = "5-Year-Old"

    steps_log = []
    explanation = ""
    sources = []
    voice_id = None

    # Run the agent pipeline
    progress(0, desc="Starting...")

    for update in run_agent(topic, persona_name):
        if update["type"] == "step":
            step_text = f"**{update['title']}**\n{update['content']}"
            steps_log.append(step_text)

            if update["step"] == "research":
                progress(0.2, desc="Researching...")
            elif update["step"] == "research_done":
                progress(0.4, desc="Research complete")
                if "sources" in update:
                    sources = update["sources"]
            elif update["step"] == "generating":
                progress(0.6, desc="Generating explanation...")

        elif update["type"] == "result":
            explanation = update["explanation"]
            sources = update.get("sources", sources)
            voice_id = update["voice_id"]
            progress(0.8, desc="Explanation ready!")

    # Format the steps log
    steps_md = "\n\n---\n\n".join(steps_log)

    # Generate audio
    audio_path = None
    if explanation and voice_id:
        progress(0.9, desc="Generating audio...")
        try:
            audio_bytes = generate_speech(explanation, voice_id)
            # Save to temp file for Gradio
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                f.write(audio_bytes)
                audio_path = f.name
            progress(1.0, desc="Done!")
        except Exception as e:
            steps_log.append(f"**⚠️ Audio generation failed**\n{str(e)}")
            steps_md = "\n\n---\n\n".join(steps_log)
            progress(1.0, desc="Done (no audio)")

    # Format sources
    sources_md = format_sources(sources)

    return explanation, audio_path, sources_md, steps_md


# Build the Gradio interface
def create_app():
    """Create and configure the Gradio app."""

    with gr.Blocks(title="Explainor - AI Persona Explanations") as app:
        # Header
        gr.Markdown(
            """
            # 🎭 Explainor

            **Learn anything through the voice of your favorite characters!**

            Enter any topic and choose a persona. The AI will research your topic,
            transform the explanation into that character's unique voice, and read it aloud.
            """
        )

        with gr.Row():
            with gr.Column(scale=2):
                topic_input = gr.Textbox(
                    label="📝 What do you want to learn about?",
                    placeholder="e.g., Blockchain, Photosynthesis, Black Holes...",
                    lines=1,
                    max_lines=1,
                )

            with gr.Column(scale=1):
                # Build persona choices with emojis
                persona_choices = [
                    f"{PERSONAS[name]['emoji']} {name}"
                    for name in get_persona_names()
                ]
                persona_dropdown = gr.Dropdown(
                    choices=persona_choices,
                    value=persona_choices[0],
                    label="🎭 Choose your explainer",
                )

        explain_btn = gr.Button(
            "✨ Explain it to me!",
            variant="primary",
            size="lg",
        )

        # Output section
        with gr.Row():
            with gr.Column():
                explanation_output = gr.Textbox(
                    label="📖 Explanation",
                    lines=8,
                    max_lines=15,
                )

                audio_output = gr.Audio(
                    label="🔊 Listen to the explanation",
                    type="filepath",
                    autoplay=False,
                )

        with gr.Row():
            with gr.Column():
                with gr.Accordion("🔍 Sources", open=False):
                    sources_output = gr.Markdown("")

            with gr.Column():
                with gr.Accordion("🧠 Agent Reasoning", open=False):
                    steps_output = gr.Markdown("")

        # Example topics
        gr.Examples(
            examples=[
                ["Quantum Computing", f"{PERSONAS['5-Year-Old']['emoji']} 5-Year-Old"],
                ["Blockchain", f"{PERSONAS['Gordon Ramsay']['emoji']} Gordon Ramsay"],
                ["Black Holes", f"{PERSONAS['Pirate']['emoji']} Pirate"],
                ["Machine Learning", f"{PERSONAS['Shakespeare']['emoji']} Shakespeare"],
                ["Climate Change", f"{PERSONAS['Surfer Dude']['emoji']} Surfer Dude"],
                ["The Force", f"{PERSONAS['Yoda']['emoji']} Yoda"],
            ],
            inputs=[topic_input, persona_dropdown],
            label="Try these examples:",
        )

        # Footer
        gr.Markdown(
            """
            ---
            **Built for MCP's 1st Birthday Hackathon** | Track: MCP in Action (Creative)

            Powered by: [Nebius AI](https://nebius.com) (LLM) + [ElevenLabs](https://elevenlabs.io) (TTS)

            Made with ❤️ by **kaiser-data**
            """
        )

        # Event handler
        def process_and_explain(topic, persona_with_emoji):
            # Extract persona name (remove emoji prefix)
            persona_name = persona_with_emoji.split(" ", 1)[1] if " " in persona_with_emoji else persona_with_emoji
            return explain_topic(topic, persona_name)

        explain_btn.click(
            fn=process_and_explain,
            inputs=[topic_input, persona_dropdown],
            outputs=[explanation_output, audio_output, sources_output, steps_output],
        )

        # Also trigger on Enter key in topic input
        topic_input.submit(
            fn=process_and_explain,
            inputs=[topic_input, persona_dropdown],
            outputs=[explanation_output, audio_output, sources_output, steps_output],
        )

    return app


# Create the app
app = create_app()

if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
    )
