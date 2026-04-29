# CLI Chat with MCP — Free Version (OpenRouter)

A CLI chat app using MCP (Model Context Protocol) powered by **OpenRouter** (free tier).

## Setup

1. Get a free API key at https://openrouter.ai/keys

2. Create `.env`:
```
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=qwen/qwen-2.5-72b-instruct
```

3. Install dependencies:
```bash
pip install openai mcp prompt-toolkit python-dotenv
```

4. Run:
```bash
python main.py
```

## Usage

- Type any question and press Enter
- Use `@filename` to reference documents (e.g. `@report.pdf`)
- Use `/format report.pdf` to reformat a doc in markdown
- Press `Ctrl+C` to exit

## Available Documents
- deposition.md
- report.pdf
- financials.docx
- outlook.pdf
- plan.md
- spec.txt

## Changes from Original (Anthropic → OpenRouter)

| File | Change |
|---|---|
| `core/claude.py` | `Anthropic()` → `OpenAI(base_url=openrouter)` |
| `core/tools.py` | `input_schema` → `parameters`, `tool_use_id` → `tool_call_id` |
| `core/chat.py` | `stop_reason == "tool_use"` → `finish_reason == "tool_calls"` |
| `main.py` | `ANTHROPIC_API_KEY` → `OPENROUTER_API_KEY` |
| `pyproject.toml` | `anthropic` → `openai` |
| `mcp_server.py` | No changes |
| `mcp_client.py` | No changes |
| `core/cli.py` | No changes |
| `core/cli_chat.py` | No changes |
