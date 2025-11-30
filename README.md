---
title: Explainor
emoji: 🎭
colorFrom: purple
colorTo: pink
sdk: gradio
sdk_version: 6.0.1
app_file: app.py
pinned: false
license: mit
short_description: AI agent explains topics in fun character voices with MCP
tags:
  - mcp-in-action-track-creative
---

# 🎭 Explainor

> **Learn anything through the voice of your favorite characters!**

[![MCP Hackathon](https://img.shields.io/badge/MCP%20Hackathon-1st%20Birthday-purple)](https://huggingface.co/MCP-1st-Birthday)
[![Track](https://img.shields.io/badge/Track-MCP%20in%20Action-blue)](https://huggingface.co/MCP-1st-Birthday)
[![Category](https://img.shields.io/badge/Category-Creative-green)](https://huggingface.co/MCP-1st-Birthday)

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

## 🛠️ How It Works

1. **Enter a topic** - Anything from "Quantum Computing" to "How do volcanoes work?"
2. **Choose a persona** - Pick your favorite character
3. **Choose your audience** - Who are you explaining to?
4. **Watch the magic** - The AI agent:
   - 🔍 Researches your topic using web search
   - 📋 Extracts key facts from sources
   - 🎭 Transforms the explanation into the character's voice
   - 🔊 Reads it aloud with a matching voice!

## 👤 Who's Listening?

Make the explanation even more tailored by choosing your audience:

| Audience | Effect |
|----------|--------|
| 👤 Just me | Standard explanation |
| 👵 My confused grandmother | Extra simple, patient |
| 🤖 A skeptical robot | Logical, evidence-based |
| 👽 An alien visiting Earth | Explain Earth concepts |

## 🔌 MCP Server Integration

This app is a **real MCP Server**! You can connect it to Claude Desktop or any MCP-compatible client.

**MCP Endpoint:**
```
https://agents-mcp-hackathon-explainor.hf.space/gradio_api/mcp/sse
```

**Available Tools:**
- `explain_topic` - Get explanations in character voices
- `generate_audio` - Generate TTS audio from explanations

## 🚀 Tech Stack

- **MCP**: Model Context Protocol - App exposes itself as an MCP server via Gradio
- **LLM**: [Nebius AI](https://nebius.com) - Llama 3.3 70B for intelligent explanations
- **TTS**: [ElevenLabs](https://elevenlabs.io) - Realistic voice synthesis with character-matched voices
- **Web Search**: DuckDuckGo API for topic research
- **Frontend**: [Gradio](https://gradio.app) with native MCP integration

## 🏆 Hackathon Submission

- **Event**: MCP's 1st Birthday Hackathon
- **Track**: MCP in Action (Track 2)
- **Category**: Creative
- **Team/Author**: kaiser-data
- **HF Username**: [kaiser-data](https://huggingface.co/kaiser-data)
- **Sponsor Integration**: ElevenLabs for text-to-speech

### 📹 Demo Video
<!-- TODO: Add demo video link -->
*Coming soon*

### 📱 Social Post
<!-- TODO: Add social media post link -->
*Coming soon*

## 📝 License

MIT License - Feel free to use and modify!

---

**Made with ❤️ for MCP's 1st Birthday Hackathon**
