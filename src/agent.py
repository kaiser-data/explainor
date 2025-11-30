"""Explainor Agent - Research and explain topics in persona voices."""

import os
import json
import httpx
from typing import Generator

from .personas import get_persona


# Nebius API configuration (OpenAI-compatible)
NEBIUS_API_BASE = "https://api.studio.nebius.com/v1"
NEBIUS_MODEL = "meta-llama/Llama-3.3-70B-Instruct"


def get_nebius_client():
    """Get configured httpx client for Nebius API."""
    api_key = os.getenv("NEBIUS_API_KEY")
    if not api_key:
        raise ValueError("NEBIUS_API_KEY environment variable not set")
    return api_key


def web_search(query: str) -> dict:
    """Perform web search using DuckDuckGo (no API key needed).

    Returns structured search results.
    """
    try:
        # Use DuckDuckGo HTML search (no API needed)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        with httpx.Client(timeout=10.0) as client:
            # DuckDuckGo instant answer API
            resp = client.get(
                "https://api.duckduckgo.com/",
                params={
                    "q": query,
                    "format": "json",
                    "no_html": "1",
                    "skip_disambig": "1",
                },
                headers=headers,
            )
            data = resp.json()

            results = []

            # Abstract (main answer)
            if data.get("Abstract"):
                results.append({
                    "title": data.get("Heading", "Overview"),
                    "snippet": data["Abstract"],
                    "source": data.get("AbstractSource", "DuckDuckGo"),
                    "url": data.get("AbstractURL", ""),
                })

            # Related topics
            for topic in data.get("RelatedTopics", [])[:3]:
                if isinstance(topic, dict) and topic.get("Text"):
                    results.append({
                        "title": topic.get("Text", "")[:50] + "...",
                        "snippet": topic.get("Text", ""),
                        "source": "DuckDuckGo",
                        "url": topic.get("FirstURL", ""),
                    })

            # If no results, try a simpler search
            if not results:
                results.append({
                    "title": f"Search: {query}",
                    "snippet": f"Topic: {query}. Please explain this concept based on general knowledge.",
                    "source": "General Knowledge",
                    "url": "",
                })

            return {"results": results, "query": query}

    except Exception as e:
        return {
            "results": [{
                "title": f"Search: {query}",
                "snippet": f"Topic: {query}. Please explain this concept based on general knowledge.",
                "source": "General Knowledge",
                "url": "",
            }],
            "query": query,
            "error": str(e),
        }


def call_llm(messages: list[dict], max_tokens: int = 1500) -> str:
    """Call Nebius LLM API."""
    api_key = get_nebius_client()

    try:
        with httpx.Client(timeout=60.0) as client:
            resp = client.post(
                f"{NEBIUS_API_BASE}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": NEBIUS_MODEL,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": 0.8,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
    except httpx.HTTPStatusError as e:
        raise Exception(f"Nebius API error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        raise Exception(f"LLM call failed: {str(e)}")


def research_topic(topic: str) -> tuple[str, list[dict]]:
    """Research a topic using web search.

    Returns: (research_summary, sources_list)
    """
    # Perform search
    search_results = web_search(topic)

    # Format research for the agent
    research_text = f"## Research on: {topic}\n\n"
    sources = []

    for i, result in enumerate(search_results.get("results", []), 1):
        research_text += f"### Source {i}: {result['title']}\n"
        research_text += f"{result['snippet']}\n\n"
        if result.get("url"):
            sources.append({
                "title": result["title"],
                "url": result["url"],
                "source": result.get("source", "Web"),
            })

    return research_text, sources


def generate_explanation(
    topic: str,
    persona_name: str,
    research: str,
) -> Generator[dict, None, None]:
    """Generate explanation in persona voice, yielding steps.

    Yields dicts with: {"step": str, "content": str}
    """
    persona = get_persona(persona_name)

    # Step 1: Acknowledge the task
    yield {
        "step": "understanding",
        "title": "📚 Understanding the topic",
        "content": f"Researching '{topic}' to gather key information...",
    }

    # Step 2: Show research
    yield {
        "step": "research",
        "title": "🔍 Research complete",
        "content": f"Found information about {topic}. Now transforming into {persona_name} voice...",
    }

    # Step 3: Generate the explanation
    messages = [
        {
            "role": "system",
            "content": f"""{persona['system_prompt']}

You are explaining a topic to someone. Your explanation should be:
1. Entertaining and fully in character
2. Educational - actually explain the concept clearly
3. About 150-200 words (suitable for audio)
4. Natural spoken language (will be read aloud)

Do NOT break character. Do NOT use markdown formatting or bullet points.
Just speak naturally as your character would.""",
        },
        {
            "role": "user",
            "content": f"""Here's some research on the topic:

{research}

Now explain "{topic}" in your unique voice and style. Make it fun and educational!""",
        },
    ]

    explanation = call_llm(messages)

    yield {
        "step": "explanation",
        "title": f"{persona['emoji']} Explanation ready",
        "content": explanation,
    }


def format_tool_call(tool_name: str, inputs: dict, output_summary: str) -> str:
    """Format a tool call for display."""
    import json
    return f"""```json
{{
  "tool": "{tool_name}",
  "input": {json.dumps(inputs, indent=4)},
  "status": "success",
  "output": "{output_summary}"
}}
```"""


def run_agent(topic: str, persona_name: str, audience: str = "") -> Generator[dict, None, None]:
    """Run the full agent pipeline with tool orchestration.

    Yields progress updates and final results.
    """
    # Tool 1: web_search (DuckDuckGo)
    yield {
        "type": "step",
        "step": "research",
        "title": "🔧 Tool: `web_search`",
        "content": format_tool_call("web_search", {"query": topic, "max_results": 5}, "Searching..."),
    }

    research, sources = research_topic(topic)

    yield {
        "type": "step",
        "step": "research_done",
        "title": "✅ Response: `web_search`",
        "content": format_tool_call("web_search", {"query": topic}, f"Found {len(sources)} sources"),
        "sources": sources,
    }

    # Tool 2: extract_facts
    yield {
        "type": "step",
        "step": "extracting",
        "title": "🔧 Tool: `extract_facts`",
        "content": format_tool_call("extract_facts", {"text": f"[{len(sources)} source documents]", "max_facts": 5}, "Extracting key facts..."),
    }

    # Generate explanation
    persona = get_persona(persona_name)

    # Build audience context
    audience_context = ""
    if audience and audience.strip():
        audience_context = f"\nYou are explaining this to: {audience.strip()}. Tailor your explanation appropriately for them."

    # Tool 3: persona_transform (Nebius LLM)
    yield {
        "type": "step",
        "step": "generating",
        "title": "🔧 Tool: `persona_transform`",
        "content": format_tool_call(
            "persona_transform",
            {
                "persona": persona_name,
                "audience": audience if audience else "general",
                "style": persona["system_prompt"][:50] + "...",
            },
            "Generating explanation..."
        ),
    }

    messages = [
        {
            "role": "system",
            "content": f"""{persona['system_prompt']}

You are explaining a topic to someone. Your explanation should be:
1. Entertaining and fully in character
2. Educational - actually explain the concept clearly
3. MAXIMUM 100 words - be concise!
4. Natural spoken language (will be read aloud)
5. Engaging and memorable{audience_context}

Do NOT break character. Do NOT use markdown, bullet points, or special formatting.
Just speak naturally as your character would.""",
        },
        {
            "role": "user",
            "content": f"""Research on the topic:

{research}

Now explain "{topic}" in your unique {persona_name} voice and style. Make it fun, memorable, and educational!""",
        },
    ]

    explanation = call_llm(messages)

    # Track tools used in pipeline
    mcp_tools = [
        {"name": "web_search", "icon": "🔍", "desc": "Web research via DuckDuckGo API"},
        {"name": "extract_facts", "icon": "📋", "desc": "Key fact extraction from sources"},
        {"name": "persona_transform", "icon": "🎭", "desc": "Persona explanation via Nebius LLM"},
    ]

    yield {
        "type": "result",
        "explanation": explanation,
        "sources": sources,
        "persona": persona_name,
        "persona_emoji": persona["emoji"],
        "voice_id": persona["voice_id"],
        "voice_settings": persona.get("voice_settings"),
        "mcp_tools": mcp_tools,
    }
