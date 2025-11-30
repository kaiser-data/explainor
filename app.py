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


# Custom CSS for dark mode input visibility
CUSTOM_CSS = """
/* Fix dark mode input visibility */
input, textarea, select {
    color: var(--body-text-color) !important;
    background-color: var(--input-background-fill) !important;
}

input:hover, textarea:hover, select:hover,
input:focus, textarea:focus, select:focus {
    color: var(--body-text-color) !important;
    background-color: var(--input-background-fill) !important;
}

/* Ensure placeholder is visible */
input::placeholder, textarea::placeholder {
    color: var(--body-text-color-subdued) !important;
    opacity: 0.7;
}

/* Force dark background on inputs */
.dark input, .dark textarea {
    background-color: #374151 !important;
    color: #ffffff !important;
}
"""


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


def format_mcp_tools(tools: list[dict]) -> str:
    """Format tools used as markdown."""
    if not tools:
        return "*No tools used*"

    md = "**🔌 Agent Tool Calls:**\n\n"
    for tool in tools:
        md += f"| {tool['icon']} | `{tool['name']}` | {tool['desc']} |\n"
    return md


def explain_topic(topic: str, persona_name: str, audience: str = "", progress=gr.Progress()):
    """Main function to explain a topic in a persona's voice.

    Returns: (explanation_text, sources_md, steps_md, mcp_md)
    """
    if not topic.strip():
        return (
            "Please enter a topic to explain!",
            "",
            "❌ No topic provided",
            "",
        )

    if not persona_name:
        persona_name = "5-Year-Old"

    steps_log = []
    explanation = ""
    sources = []
    mcp_tools = []

    # Run the agent pipeline
    progress(0, desc="Starting...")

    for update in run_agent(topic, persona_name, audience):
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
            mcp_tools = update.get("mcp_tools", [])
            progress(1.0, desc="Done!")

    # Format the steps log
    steps_md = "\n\n---\n\n".join(steps_log)

    # Format sources
    sources_md = format_sources(sources)

    # Format MCP tools
    mcp_md = format_mcp_tools(mcp_tools)

    return explanation, sources_md, steps_md, mcp_md


def generate_audio(explanation: str, persona_name: str, progress=gr.Progress()):
    """Generate audio from the explanation text.

    Returns: audio_path
    """
    if not explanation or not explanation.strip():
        return None

    if not persona_name:
        persona_name = "5-Year-Old"

    # Get persona voice settings
    persona = get_persona(persona_name)
    voice_id = persona["voice_id"]
    voice_settings = persona.get("voice_settings")

    progress(0.3, desc="Generating audio...")

    try:
        audio_bytes = generate_speech(explanation, voice_id, voice_settings)
        # Save to temp file for Gradio
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(audio_bytes)
            audio_path = f.name
        progress(1.0, desc="Audio ready!")
        return audio_path
    except Exception as e:
        progress(1.0, desc="Audio failed")
        raise gr.Error(f"Audio generation failed: {str(e)}")


# Build the Gradio interface
def create_app():
    """Create and configure the Gradio app."""

    with gr.Blocks(title="Explainor - AI Persona Explanations") as app:
        # Header
        gr.Markdown(
            """
            # 🎭 Explainor
            ### *AI Agent with Tool Orchestration*

            **Learn anything through the voice of your favorite characters!**

            This agent orchestrates multiple tools to: research your topic,
            extract key facts, transform explanations into character voices, and generate audio.
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

        with gr.Row():
            # Funny listener options (don't overlap with personas)
            listener_choices = [
                "👤 Just me",
                "👵 My confused grandmother",
                "🤖 A skeptical robot",
                "👽 An alien visiting Earth",
                "🧟 A zombie (short attention span)",
                "🦊 A very smart fox",
                "👔 A stressed CEO",
                "🎮 A distracted gamer",
            ]
            audience_dropdown = gr.Dropdown(
                choices=listener_choices,
                value=listener_choices[0],
                label="👤 Who's listening?",
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

                read_aloud_btn = gr.Button(
                    "🔊 Read Aloud",
                    variant="secondary",
                    size="sm",
                )
                audio_output = gr.Audio(
                    label="🔊 Listen to the explanation",
                    type="filepath",
                    autoplay=True,
                )

        with gr.Row():
            with gr.Column():
                with gr.Accordion("🔌 Agent Tool Calls", open=True):
                    mcp_output = gr.Markdown("")

        with gr.Row():
            with gr.Column():
                with gr.Accordion("🔍 Sources", open=False):
                    sources_output = gr.Markdown("")

            with gr.Column():
                with gr.Accordion("🧠 Execution Trace", open=False):
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

        # Event handler for explanation
        def process_and_explain(topic, persona_with_emoji, audience_with_emoji):
            # Extract persona name (remove emoji prefix)
            persona_name = persona_with_emoji.split(" ", 1)[1] if " " in persona_with_emoji else persona_with_emoji
            # Extract audience (remove emoji prefix), skip if "Just me"
            audience = ""
            if audience_with_emoji and "Just me" not in audience_with_emoji:
                audience = audience_with_emoji.split(" ", 1)[1] if " " in audience_with_emoji else audience_with_emoji
            return explain_topic(topic, persona_name, audience)

        explain_btn.click(
            fn=process_and_explain,
            inputs=[topic_input, persona_dropdown, audience_dropdown],
            outputs=[explanation_output, sources_output, steps_output, mcp_output],
        )

        # Also trigger on Enter key in topic input
        topic_input.submit(
            fn=process_and_explain,
            inputs=[topic_input, persona_dropdown, audience_dropdown],
            outputs=[explanation_output, sources_output, steps_output, mcp_output],
        )

        # Event handler for audio generation
        def process_audio(explanation, persona_with_emoji):
            # Extract persona name (remove emoji prefix)
            persona_name = persona_with_emoji.split(" ", 1)[1] if " " in persona_with_emoji else persona_with_emoji
            return generate_audio(explanation, persona_name)

        read_aloud_btn.click(
            fn=process_audio,
            inputs=[explanation_output, persona_dropdown],
            outputs=[audio_output],
        )

    return app


# Create the app
app = create_app()

if __name__ == "__main__":
    # MCP server enabled for Gradio 5+
    enable_mcp = os.getenv("ENABLE_MCP_SERVER", "true").lower() == "true"

    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        mcp_server=enable_mcp,
    )
