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


# Custom CSS for better styling
CUSTOM_CSS = """
/* Dark mode input fix */
.dark input, .dark textarea {
    background-color: #374151 !important;
    color: #ffffff !important;
}

/* Header styling */
.header-container {
    text-align: center;
    padding: 1rem 0;
}

/* Card-like sections */
.input-section, .output-section {
    border-radius: 12px;
    padding: 1rem;
}

/* Primary button enhancement */
.primary-btn {
    font-size: 1.1rem !important;
    padding: 0.75rem 2rem !important;
}

/* Audio section layout */
.audio-row {
    display: flex;
    align-items: center;
    gap: 1rem;
}

/* Persona cards in examples */
.example-row {
    margin-top: 0.5rem;
}

/* Footer styling */
.footer {
    text-align: center;
    opacity: 0.8;
    font-size: 0.9rem;
}

/* MCP badge */
.mcp-badge {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    display: inline-block;
    font-weight: bold;
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
    """Format tools used as markdown table."""
    if not tools:
        return "*Waiting for explanation...*"

    md = "| Tool | Description |\n|------|-------------|\n"
    for tool in tools:
        md += f"| {tool['icon']} `{tool['name']}` | {tool['desc']} |\n"
    return md


def explain_topic(topic: str, persona_name: str, audience: str = "", progress=gr.Progress()):
    """Main function to explain a topic in a persona's voice."""
    if not topic.strip():
        return "Please enter a topic to explain!", "", "", ""

    if not persona_name:
        persona_name = "5-Year-Old"

    steps_log = []
    explanation = ""
    sources = []
    mcp_tools = []

    progress(0, desc="Starting...")

    for update in run_agent(topic, persona_name, audience):
        if update["type"] == "step":
            step_text = f"**{update['title']}**\n{update['content']}"
            steps_log.append(step_text)

            if update["step"] == "research":
                progress(0.2, desc="🔍 Researching...")
            elif update["step"] == "research_done":
                progress(0.4, desc="📚 Research complete")
                if "sources" in update:
                    sources = update["sources"]
            elif update["step"] == "generating":
                progress(0.6, desc="🎭 Generating explanation...")

        elif update["type"] == "result":
            explanation = update["explanation"]
            sources = update.get("sources", sources)
            mcp_tools = update.get("mcp_tools", [])
            progress(1.0, desc="✅ Done!")

    steps_md = "\n\n---\n\n".join(steps_log)
    sources_md = format_sources(sources)
    mcp_md = format_mcp_tools(mcp_tools)

    return explanation, sources_md, steps_md, mcp_md


def generate_audio(explanation: str, persona_name: str, progress=gr.Progress()):
    """Generate audio from the explanation text."""
    if not explanation or not explanation.strip():
        return None

    if not persona_name:
        persona_name = "5-Year-Old"

    persona = get_persona(persona_name)
    voice_id = persona["voice_id"]
    voice_settings = persona.get("voice_settings")

    progress(0.3, desc="🔊 Generating audio...")

    try:
        audio_bytes = generate_speech(explanation, voice_id, voice_settings)
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(audio_bytes)
            audio_path = f.name
        progress(1.0, desc="✅ Audio ready!")
        return audio_path
    except Exception as e:
        progress(1.0, desc="❌ Audio failed")
        raise gr.Error(f"Audio generation failed: {str(e)}")


def create_app():
    """Create and configure the Gradio app."""

    # Build persona choices
    persona_choices = [
        f"{PERSONAS[name]['emoji']} {name}"
        for name in get_persona_names()
    ]

    # Audience choices
    audience_choices = [
        "👤 Just me",
        "👵 Confused grandmother",
        "🤖 Skeptical robot",
        "👽 Alien visitor",
        "🧟 Zombie",
        "👔 Stressed CEO",
    ]

    with gr.Blocks(title="Explainor", fill_width=True) as app:

        # ===== HEADER =====
        gr.Markdown(
            """
            <div style="text-align: center; padding: 1rem 0;">
                <h1>🎭 Explainor</h1>
                <p style="font-size: 1.2rem; opacity: 0.9;">Learn anything through the voice of your favorite characters!</p>
            </div>
            """,
            elem_classes=["header-container"]
        )

        # ===== INPUT SECTION =====
        with gr.Group():
            # Topic input - full width, prominent
            topic_input = gr.Textbox(
                label="What do you want to learn about?",
                placeholder="Try: Quantum Computing, Blockchain, Black Holes, Climate Change...",
                lines=1,
                scale=2,
            )

            # Persona and Audience in one row
            with gr.Row():
                persona_dropdown = gr.Dropdown(
                    choices=persona_choices,
                    value=persona_choices[0],
                    label="🎭 Explainer",
                    scale=1,
                )
                audience_dropdown = gr.Dropdown(
                    choices=audience_choices,
                    value=audience_choices[0],
                    label="👤 Audience",
                    scale=1,
                )

        # ===== ACTION BUTTON =====
        explain_btn = gr.Button(
            "✨ Explain it to me!",
            variant="primary",
            size="lg",
            elem_classes=["primary-btn"],
        )

        # ===== OUTPUT SECTION =====
        with gr.Group():
            explanation_output = gr.Textbox(
                label="📖 Explanation",
                lines=6,
                show_copy_button=True,
            )

            # Audio controls in a row
            with gr.Row():
                read_aloud_btn = gr.Button(
                    "🔊 Read Aloud",
                    variant="secondary",
                    scale=1,
                )
                audio_output = gr.Audio(
                    label="Listen",
                    type="filepath",
                    autoplay=True,
                    scale=3,
                )

        # ===== DETAILS SECTION (Tabs) =====
        with gr.Accordion("📊 Details", open=False):
            with gr.Tabs():
                with gr.TabItem("🔧 Agent Tools"):
                    mcp_output = gr.Markdown("*Run an explanation to see tool calls*")

                with gr.TabItem("📚 Sources"):
                    sources_output = gr.Markdown("*Sources will appear here*")

                with gr.TabItem("🔍 Trace"):
                    steps_output = gr.Markdown("*Execution trace will appear here*")

        # ===== EXAMPLES =====
        gr.Markdown("### 💡 Try these examples")
        gr.Examples(
            examples=[
                ["Quantum Computing", "👶 5-Year-Old"],
                ["Blockchain", "👨‍🍳 Gordon Ramsay"],
                ["Black Holes", "🏴‍☠️ Pirate"],
                ["Machine Learning", "🎭 Shakespeare"],
                ["Climate Change", "🏄 Surfer Dude"],
                ["The Force", "🧙 Yoda"],
            ],
            inputs=[topic_input, persona_dropdown],
            label="",
        )

        # ===== MCP INFO =====
        with gr.Accordion("🔌 MCP Server", open=False):
            gr.Markdown(
                """
                This app is an **MCP Server**! Connect it to Claude Desktop or any MCP client:

                ```
                https://kaiser-data-mcp-1st-birthday-explainor.hf.space/gradio_api/mcp/sse
                ```

                **Available Tools:** `explain_topic`, `generate_audio`
                """
            )

        # ===== FOOTER =====
        gr.Markdown(
            """
            <div style="text-align: center; padding: 1rem 0; opacity: 0.7; font-size: 0.85rem;">
                <strong>MCP's 1st Birthday Hackathon</strong> · Track: MCP in Action (Creative)<br/>
                Powered by <a href="https://nebius.com">Nebius AI</a> + <a href="https://elevenlabs.io">ElevenLabs</a> ·
                Made with ❤️ by <strong>kaiser-data</strong>
            </div>
            """,
            elem_classes=["footer"]
        )

        # ===== EVENT HANDLERS =====
        def process_and_explain(topic, persona_with_emoji, audience_with_emoji):
            persona_name = persona_with_emoji.split(" ", 1)[1] if " " in persona_with_emoji else persona_with_emoji
            audience = ""
            if audience_with_emoji and "Just me" not in audience_with_emoji:
                audience = audience_with_emoji.split(" ", 1)[1] if " " in audience_with_emoji else audience_with_emoji
            return explain_topic(topic, persona_name, audience)

        def process_audio(explanation, persona_with_emoji):
            persona_name = persona_with_emoji.split(" ", 1)[1] if " " in persona_with_emoji else persona_with_emoji
            return generate_audio(explanation, persona_name)

        # Explain button click
        explain_btn.click(
            fn=process_and_explain,
            inputs=[topic_input, persona_dropdown, audience_dropdown],
            outputs=[explanation_output, sources_output, steps_output, mcp_output],
        )

        # Enter key in topic input
        topic_input.submit(
            fn=process_and_explain,
            inputs=[topic_input, persona_dropdown, audience_dropdown],
            outputs=[explanation_output, sources_output, steps_output, mcp_output],
        )

        # Read aloud button
        read_aloud_btn.click(
            fn=process_audio,
            inputs=[explanation_output, persona_dropdown],
            outputs=[audio_output],
        )

    return app


# Create the app
app = create_app()

if __name__ == "__main__":
    enable_mcp = os.getenv("ENABLE_MCP_SERVER", "true").lower() == "true"

    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        mcp_server=enable_mcp,
        css=CUSTOM_CSS,
    )
