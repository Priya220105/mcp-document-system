from openai import OpenAI
import os
import json


class Claude:
    def __init__(self, model: str):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            default_headers={"HTTP-Referer": "http://localhost"}
        )
        self.model = model

    def add_user_message(self, messages: list, message):
        """Add user message - handles both string and tool result lists"""
        if isinstance(message, list):
            # tool results - append each separately
            for m in message:
                messages.append(m)
        else:
            messages.append({"role": "user", "content": message})

    def add_assistant_message(self, messages: list, response):
        """Add assistant message from OpenRouter response"""
        msg = response.choices[0].message
        messages.append({
            "role": "assistant",
            "content": msg.content,
            "tool_calls": msg.tool_calls if msg.tool_calls else None
        })

    def text_from_message(self, response) -> str:
        """Extract text content from OpenRouter response"""
        return response.choices[0].message.content or ""

    def get_stop_reason(self, response) -> str:
        """Get finish reason - maps OpenRouter to Anthropic equivalents"""
        finish_reason = response.choices[0].finish_reason
        # OpenRouter uses "tool_calls", Anthropic uses "tool_use"
        if finish_reason == "tool_calls":
            return "tool_use"
        return finish_reason or "end_turn"

    def chat(
        self,
        messages,
        system=None,
        temperature=1.0,
        stop=None,
        tools=None,
        tool_choice=None,
    ):
        all_messages = []

        if system:
            all_messages.append({"role": "system", "content": system})

        all_messages += messages

        params = {
            "model": self.model,
            "max_tokens": 8000,
            "messages": all_messages,
            "temperature": temperature,
        }

        if tools:
            # Convert Anthropic-style schemas to OpenRouter format
            params["tools"] = self._convert_tools(tools)

        if stop:
            params["stop"] = stop

        if tool_choice:
            params["tool_choice"] = {
                "type": "function",
                "function": {"name": tool_choice["name"]}
            }

        return self.client.chat.completions.create(**params)

    def _convert_tools(self, tools: list) -> list:
        """Convert Anthropic tool format to OpenRouter/OpenAI format"""
        converted = []
        for tool in tools:
            # Already in OpenAI format
            if "type" in tool and tool["type"] == "function":
                converted.append(tool)
            # Anthropic format - convert it
            elif "input_schema" in tool:
                converted.append({
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool.get("description", ""),
                        "parameters": tool["input_schema"],
                    }
                })
            else:
                converted.append(tool)
        return converted
