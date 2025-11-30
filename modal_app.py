"""Modal deployment configuration for Explainor.

Deploy with: modal deploy modal_app.py
Run locally: modal serve modal_app.py
"""

import os
import modal

# Define the Modal app
app = modal.App("explainor")

# Create image with dependencies
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "gradio[mcp]>=5.0.0",
        "elevenlabs>=1.0.0",
        "httpx>=0.25.0",
        "python-dotenv>=1.0.0",
    )
    .add_local_dir("src", remote_path="/app/src", copy=True)
    .add_local_file("app.py", remote_path="/app/app.py", copy=True)
)


@app.function(
    image=image,
    secrets=[
        modal.Secret.from_name("nebius-api-key"),
        modal.Secret.from_name("elevenlabs-api-key"),
    ],
    timeout=600,
    scaledown_window=300,
)
@modal.asgi_app()
def serve():
    """Serve the Gradio app as ASGI."""
    import sys
    import os
    sys.path.insert(0, "/app")

    # Disable MCP server on Modal (causes issues)
    os.environ["ENABLE_MCP_SERVER"] = "false"

    import gradio as gr
    from src.personas import PERSONAS, get_persona_names, get_persona
    from src.agent import run_agent
    from src.tts import generate_speech
    import tempfile

    def format_sources(sources):
        if not sources:
            return "*No external sources used*"
        md = ""
        for i, src in enumerate(sources, 1):
            if src.get("url"):
                md += f"{i}. [{src['title']}]({src['url']})\n"
            else:
                md += f"{i}. {src['title']} ({src.get('source', 'General')})\n"
        return md

    def format_mcp_tools(tools):
        if not tools:
            return "*No tools used*"
        md = "**Agent Tool Calls:**\n\n"
        for tool in tools:
            md += f"| {tool['icon']} | `{tool['name']}` | {tool['desc']} |\n"
        return md

    def explain_topic(topic, persona_name, audience=""):
        if not topic.strip():
            return "Please enter a topic!", "", "", ""
        if not persona_name:
            persona_name = "5-Year-Old"

        steps_log = []
        explanation = ""
        sources = []
        mcp_tools = []

        for update in run_agent(topic, persona_name, audience):
            if update["type"] == "step":
                steps_log.append(f"**{update['title']}**\n{update['content']}")
                if update["step"] == "research_done" and "sources" in update:
                    sources = update["sources"]
            elif update["type"] == "result":
                explanation = update["explanation"]
                sources = update.get("sources", sources)
                mcp_tools = update.get("mcp_tools", [])

        return explanation, format_sources(sources), "\n\n---\n\n".join(steps_log), format_mcp_tools(mcp_tools)

    def generate_audio(explanation, persona_name):
        if not explanation or not explanation.strip():
            return None
        if not persona_name:
            persona_name = "5-Year-Old"
        persona = get_persona(persona_name)
        voice_id = persona["voice_id"]
        voice_settings = persona.get("voice_settings")
        audio_bytes = generate_speech(explanation, voice_id, voice_settings)
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(audio_bytes)
            return f.name

    with gr.Blocks(title="Explainor - AI Persona Explanations") as demo:
        gr.Markdown("# Explainor\n### Learn anything through the voice of your favorite characters!")

        with gr.Row():
            topic_input = gr.Textbox(label="What do you want to learn about?", placeholder="e.g., Quantum Computing")
            persona_choices = [f"{PERSONAS[name]['emoji']} {name}" for name in get_persona_names()]
            persona_dropdown = gr.Dropdown(choices=persona_choices, value=persona_choices[0], label="Choose your explainer")

        audience_dropdown = gr.Dropdown(
            choices=["Just me", "My confused grandmother", "A skeptical robot", "An alien visiting Earth"],
            value="Just me",
            label="Who's listening?"
        )

        explain_btn = gr.Button("Explain it to me!", variant="primary")

        explanation_output = gr.Textbox(label="Explanation", lines=6)
        read_aloud_btn = gr.Button("Read Aloud", variant="secondary")
        audio_output = gr.Audio(label="Listen", type="filepath", autoplay=True)

        with gr.Accordion("Agent Tool Calls", open=False):
            mcp_output = gr.Markdown("")
        with gr.Accordion("Sources", open=False):
            sources_output = gr.Markdown("")
        with gr.Accordion("Execution Trace", open=False):
            steps_output = gr.Markdown("")

        def process_explain(topic, persona_with_emoji, audience):
            persona_name = persona_with_emoji.split(" ", 1)[1] if " " in persona_with_emoji else persona_with_emoji
            aud = "" if "Just me" in audience else audience
            return explain_topic(topic, persona_name, aud)

        def process_audio(explanation, persona_with_emoji):
            persona_name = persona_with_emoji.split(" ", 1)[1] if " " in persona_with_emoji else persona_with_emoji
            return generate_audio(explanation, persona_name)

        explain_btn.click(fn=process_explain, inputs=[topic_input, persona_dropdown, audience_dropdown],
                          outputs=[explanation_output, sources_output, steps_output, mcp_output])
        read_aloud_btn.click(fn=process_audio, inputs=[explanation_output, persona_dropdown], outputs=[audio_output])

    # Return the FastAPI app that Gradio creates
    return demo.app


# For local testing
if __name__ == "__main__":
    # Run with: python modal_app.py
    print("Run with: modal serve modal_app.py")
    print("Or deploy: modal deploy modal_app.py")
