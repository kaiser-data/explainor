"""Modal deployment configuration for Explainor.

Deploy with: modal deploy modal_app.py
Run locally: modal serve modal_app.py
"""

import modal

# Define the Modal app
app = modal.App("explainor-v6")

# Create image with dependencies
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "gradio==4.44.1",  # Use older stable version without aggressive SSE
        "elevenlabs>=1.0.0",
        "httpx>=0.25.0",
        "python-dotenv>=1.0.0",
        "fastapi",
        "uvicorn",
    )
    .add_local_dir("src", remote_path="/app/src", copy=True)
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
@modal.web_server(port=7860, startup_timeout=120)
def serve():
    """Serve the Gradio app via web_server."""
    import subprocess
    import sys
    import os

    os.chdir("/app")
    sys.path.insert(0, "/app")

    # Write a standalone gradio script
    script = '''
import sys
sys.path.insert(0, "/app")

import os
import tempfile
import gradio as gr
from src.personas import get_persona_names, get_persona
from src.agent import run_agent
from src.tts import generate_speech

def format_sources(sources):
    if not sources:
        return "*No external sources used*"
    md = ""
    for i, src in enumerate(sources, 1):
        if src.get("url"):
            md += f"{i}. [{src['title']}]({src['url']})\\n"
        else:
            md += f"{i}. {src['title']} ({src.get('source', 'General')})\\n"
    return md

def format_mcp_tools(tools):
    if not tools:
        return "*No tools used*"
    md = "**Agent Tool Calls:**\\n\\n"
    for tool in tools:
        md += f"| {tool['icon']} | `{tool['name']}` | {tool['desc']} |\\n"
    return md

def explain_topic(topic, persona_name, audience=""):
    import traceback
    if not topic.strip():
        return "Please enter a topic!", "", "", ""
    if not persona_name:
        persona_name = "5-Year-Old"

    # Check API key
    nebius_key = os.getenv("NEBIUS_API_KEY")
    if not nebius_key:
        available_keys = [k for k in os.environ.keys() if "KEY" in k or "API" in k or "NEBIUS" in k]
        return f"Error: NEBIUS_API_KEY not found. Available: {available_keys}", "", "", ""

    steps_log = []
    explanation = ""
    sources = []
    mcp_tools = []
    try:
        for update in run_agent(topic, persona_name, audience):
            if update["type"] == "step":
                steps_log.append(f"**{update['title']}**\\n{update['content']}")
                if update["step"] == "research_done" and "sources" in update:
                    sources = update["sources"]
            elif update["type"] == "result":
                explanation = update["explanation"]
                sources = update.get("sources", sources)
                mcp_tools = update.get("mcp_tools", [])
    except Exception as e:
        return f"Error: {str(e)}\\n\\n{traceback.format_exc()}", "", "\\n\\n---\\n\\n".join(steps_log), ""
    return explanation, format_sources(sources), "\\n\\n---\\n\\n".join(steps_log), format_mcp_tools(mcp_tools)

def generate_audio(explanation, persona_name):
    if not explanation or not explanation.strip():
        return None
    if not persona_name:
        persona_name = "5-Year-Old"
    try:
        persona = get_persona(persona_name)
        audio_bytes = generate_speech(explanation, persona["voice_id"], persona.get("voice_settings"))
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(audio_bytes)
            return f.name
    except Exception as e:
        raise gr.Error(f"Audio generation failed: {str(e)}")

# Get persona names as a static list
persona_names = list(get_persona_names())

with gr.Blocks(title="Explainor") as demo:
    gr.Markdown("# Explainor\\n### Learn anything through the voice of your favorite characters!")
    with gr.Row():
        topic_input = gr.Textbox(label="Topic", placeholder="e.g., Quantum Computing")
        persona_dropdown = gr.Dropdown(choices=persona_names, value="5-Year-Old", label="Persona")
    audience_dropdown = gr.Dropdown(
        choices=["Just me", "Confused grandmother", "Skeptical robot", "Alien"],
        value="Just me",
        label="Audience"
    )
    explain_btn = gr.Button("Explain!", variant="primary")
    explanation_output = gr.Textbox(label="Explanation", lines=6)
    read_aloud_btn = gr.Button("Read Aloud")
    audio_output = gr.Audio(label="Listen", type="filepath", autoplay=True)
    with gr.Accordion("Tools", open=False):
        mcp_output = gr.Markdown("")
    with gr.Accordion("Sources", open=False):
        sources_output = gr.Markdown("")
    with gr.Accordion("Trace", open=False):
        steps_output = gr.Markdown("")

    def do_explain(topic, persona, audience):
        aud = "" if "Just me" in audience else audience
        return explain_topic(topic, persona, aud)

    explain_btn.click(
        fn=do_explain,
        inputs=[topic_input, persona_dropdown, audience_dropdown],
        outputs=[explanation_output, sources_output, steps_output, mcp_output],
    )
    read_aloud_btn.click(
        fn=generate_audio,
        inputs=[explanation_output, persona_dropdown],
        outputs=[audio_output],
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
'''

    # Write to file and run
    with open("/app/run_gradio.py", "w") as f:
        f.write(script)

    # Run the script with environment variables
    env = os.environ.copy()
    subprocess.Popen([sys.executable, "/app/run_gradio.py"], env=env)
