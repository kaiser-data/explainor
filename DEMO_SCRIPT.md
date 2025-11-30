# Demo Video Script (1-2 min)

## Opening (10 sec)
**Show:** App homepage
**Say:** "This is Explainor - an AI agent that explains any topic through fun character voices, built for MCP's 1st Birthday Hackathon."

## Demo Part 1: Basic Usage (30 sec)
**Action:** Type "Blockchain" in the topic field
**Say:** "Let's explain Blockchain..."

**Action:** Select "Gordon Ramsay" persona
**Say:** "...as Gordon Ramsay would explain it..."

**Action:** Select "Confused grandmother" audience
**Say:** "...to a confused grandmother."

**Action:** Click "Explain it to me!" and wait
**Say:** "The agent researches the topic, extracts key facts, and transforms it into Gordon's voice."

**Action:** Show the explanation result
**Say:** "And there we go - Blockchain explained with food metaphors and intensity!"

## Demo Part 2: Audio (20 sec)
**Action:** Click "Read Aloud" button
**Say:** "It can also read it aloud with a matching voice."

**Action:** Let audio play for 5-10 seconds

## Demo Part 3: MCP Integration (30 sec)
**Action:** Expand "MCP Server" accordion
**Say:** "The cool part - this app is a real MCP server. Any MCP client like Claude Desktop can connect to it."

**Action:** Show the MCP endpoint URL
**Say:** "Just add this SSE endpoint and you get two tools."

**Action:** Expand "Details" → "Agent Tools" tab
**Say:** "process_and_explain takes a topic, persona, and audience - and returns the explanation. process_audio takes that explanation plus persona and generates speech. Under the hood, it uses Nebius AI and ElevenLabs."

### MCP Tools Reference (for video)
```
Tool 1: process_and_explain
  - topic: "Blockchain"
  - persona_with_emoji: "👨‍🍳 Gordon Ramsay"
  - audience_with_emoji: "👵 Confused grandmother"
  → Returns: explanation text + sources

Tool 2: process_audio
  - explanation: "Listen here, love! Blockchain's like..."
  - persona_with_emoji: "👨‍🍳 Gordon Ramsay"
  → Returns: audio file
```

## Closing (10 sec)
**Say:** "Built with Gradio's native MCP support. Check it out on Hugging Face Spaces. Thanks for watching!"

---

# LinkedIn Post

🎭 **Explainor** - My submission for MCP's 1st Birthday Hackathon!

Ever wanted Yoda to explain Quantum Computing? Or Gordon Ramsay to break down Blockchain?

I built an AI agent that:
🔍 Researches any topic via web search
🎭 Transforms explanations into 6 fun character voices
🔊 Reads them aloud with ElevenLabs TTS
🔌 Works as an MCP server - connect it to Claude Desktop!

**MCP Tools available:**
- `process_and_explain(topic, persona, audience)` → text
- `process_audio(explanation, persona)` → audio

**Tech stack:**
- Gradio with native MCP integration
- Nebius AI (Llama 3.3 70B)
- ElevenLabs for voice synthesis

🔗 Try it: https://agents-mcp-hackathon-explainor.hf.space
🔌 MCP: https://agents-mcp-hackathon-explainor.hf.space/gradio_api/mcp/sse

#MCPHackathon #AI #MCP #Gradio #HuggingFace

---

# X/Twitter Post (shorter)

🎭 Built Explainor for @anthropabordar MCP's 1st Birthday Hackathon!

An AI agent that explains ANY topic as:
- 👶 A 5-year-old
- 👨‍🍳 Gordon Ramsay
- 🏴‍☠️ A Pirate
- 🧙 Yoda
...with voice!

It's also an MCP server - connect it to Claude Desktop!

Try it: https://agents-mcp-hackathon-explainor.hf.space

#MCPHackathon #AI
