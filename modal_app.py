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
    container_idle_timeout=300,
)
@modal.web_server(port=7860, startup_timeout=120)
def serve():
    """Serve the Gradio app via web_server."""
    import subprocess
    import os
    os.chdir("/app")
    subprocess.Popen(["python", "app.py"])


# For local testing
if __name__ == "__main__":
    # Run with: python modal_app.py
    print("Run with: modal serve modal_app.py")
    print("Or deploy: modal deploy modal_app.py")
