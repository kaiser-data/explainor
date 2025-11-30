# 🎭 Explainor

> **Learn anything through the voice of your favorite characters!**

[![MCP Hackathon](https://img.shields.io/badge/MCP%20Hackathon-1st%20Birthday-purple)](https://huggingface.co/MCP-1st-Birthday)
[![Track](https://img.shields.io/badge/Track-MCP%20in%20Action-blue)](https://huggingface.co/MCP-1st-Birthday)
[![Category](https://img.shields.io/badge/Category-Creative-green)](https://huggingface.co/MCP-1st-Birthday)

**Tags:** `mcp-in-action-track-creative`

---

## 🌟 What is Explainor?

Explainor is an AI agent that takes any topic you want to learn about and explains it through the voice of fun characters! Choose from 6 unique personas:

| Persona | Style |
|---------|-------|
| 👶 **5-Year-Old** | Simple words, excited, curious questions |
| 👨‍🍳 **Gordon Ramsay** | Intense, food metaphors, "It's RAW!" |
| 🏴‍☠️ **Pirate** | "Arrr!", treasure metaphors, swashbuckling |
| 🎭 **Shakespeare** | Dramatic, old English, theatrical |
| 🏄 **Surfer Dude** | "Brooo", chill vibes, wave metaphors |
| 🧙 **Yoda** | Inverted syntax, wise, Force references |

## 🎬 Demo

[Demo Video Placeholder]

## 🛠️ How It Works

1. **Enter a topic** - Anything from "Quantum Computing" to "How do volcanoes work?"
2. **Choose a persona** - Pick your favorite character
3. **Watch the magic** - The AI agent:
   - 🔍 Researches your topic using web search
   - 🧠 Shows its reasoning process
   - ✍️ Transforms the explanation into the character's voice
   - 🔊 Reads it aloud with a matching voice!

## 🚀 Tech Stack

- **LLM**: [Nebius AI](https://nebius.com) - Llama 3.3 70B for intelligent explanations
- **TTS**: [ElevenLabs](https://elevenlabs.io) - Realistic voice synthesis with character-matched voices
- **Web Search**: DuckDuckGo API for topic research
- **Frontend**: [Gradio](https://gradio.app) - Beautiful, responsive UI
- **Deployment**: [Modal](https://modal.com) - Serverless infrastructure

## 💻 Local Development

### Prerequisites

- Python 3.11+
- Nebius API key
- ElevenLabs API key

### Setup

```bash
# Clone the repository
git clone https://huggingface.co/spaces/MCP-1st-Birthday/explainor

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Run locally
python app.py
```

### Environment Variables

```bash
NEBIUS_API_KEY=your_nebius_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
```

## 🌐 Deployment

### Modal Deployment

```bash
# Set up Modal secrets
modal secret create nebius-api-key NEBIUS_API_KEY=your_key
modal secret create elevenlabs-api-key ELEVENLABS_API_KEY=your_key

# Deploy
modal deploy modal_app.py
```

### Hugging Face Spaces

This app is designed to run on Hugging Face Spaces with the Gradio SDK.

## 📁 Project Structure

```
explainor/
├── app.py              # Main Gradio application
├── modal_app.py        # Modal deployment config
├── requirements.txt    # Python dependencies
├── src/
│   ├── __init__.py
│   ├── personas.py     # Persona definitions & voice mappings
│   ├── agent.py        # Agent logic & web search
│   └── tts.py          # ElevenLabs integration
└── README.md
```

## 🏆 Hackathon Submission

- **Event**: MCP's 1st Birthday Hackathon
- **Track**: MCP in Action (Track 2)
- **Category**: Creative
- **Team**: kaiser-data
- **Sponsor Integration**: ElevenLabs for text-to-speech

## 📝 License

MIT License - Feel free to use and modify!

---

**Made with ❤️ for MCP's 1st Birthday Hackathon**
