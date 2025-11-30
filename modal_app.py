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
        "gradio>=5.0.0",
        "elevenlabs>=1.0.0",
        "httpx>=0.25.0",
        "python-dotenv>=1.0.0",
    )
    .copy_local_dir("src", "/app/src")
    .copy_local_file("app.py", "/app/app.py")
)


@app.function(
    image=image,
    secrets=[
        modal.Secret.from_name("nebius-api-key"),
        modal.Secret.from_name("elevenlabs-api-key"),
    ],
    timeout=600,
    allow_concurrent_inputs=10,
)
@modal.asgi_app()
def serve():
    """Serve the Gradio app."""
    import sys
    sys.path.insert(0, "/app")

    from app import app as gradio_app
    return gradio_app


# For local testing
if __name__ == "__main__":
    # Run with: python modal_app.py
    print("Run with: modal serve modal_app.py")
    print("Or deploy: modal deploy modal_app.py")
