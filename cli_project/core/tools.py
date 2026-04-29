import json
from typing import Optional, Literal, List
from mcp.types import CallToolResult, Tool, TextContent
from cli_project.mcp_client import MCPClient


class ToolManager:
    @classmethod
    async def get_all_tools(cls, clients: dict) -> list:
        """Gets all tools from the provided clients in OpenRouter format"""
        tools = []
        for client in clients.values():
            tool_models = await client.list_tools()
            tools += [
                {
                    "type": "function",           # ← OpenRouter requires this
                    "function": {                  # ← wrapped in function key
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.inputSchema,  # ← inputSchema → parameters
                    }
                }
                for t in tool_models
            ]
        return tools

    @classmethod
    async def _find_client_with_tool(
        cls, clients: list, tool_name: str
    ) -> Optional[MCPClient]:
        """Finds the first client that has the specified tool"""
        for client in clients:
            tools = await client.list_tools()
            tool = next((t for t in tools if t.name == tool_name), None)
            if tool:
                return client
        return None

    @classmethod
    def _build_tool_result(
        cls,
        tool_call_id: str,
        text: str,
        is_error: bool = False,
    ) -> dict:
        """Builds a tool result in OpenRouter format"""
        return {
            "role": "tool",                    # ← OpenRouter uses role: "tool"
            "tool_call_id": tool_call_id,      # ← not tool_use_id
            "content": text if not is_error else f"Error: {text}",
        }

    @classmethod
    async def execute_tool_requests(
        cls, clients: dict, response
    ) -> List[dict]:
        """Executes tool requests from OpenRouter response"""
        tool_calls = response.choices[0].message.tool_calls or []
        tool_result_blocks = []

        for tool_call in tool_calls:
            tool_call_id = tool_call.id
            tool_name = tool_call.function.name
            tool_input = json.loads(tool_call.function.arguments)

            client = await cls._find_client_with_tool(
                list(clients.values()), tool_name
            )

            if not client:
                tool_result_blocks.append(
                    cls._build_tool_result(tool_call_id, "Could not find that tool", True)
                )
                continue

            try:
                tool_output: CallToolResult | None = await client.call_tool(
                    tool_name, tool_input
                )
                items = []
                if tool_output:
                    items = tool_output.content
                content_list = [
                    item.text for item in items if isinstance(item, TextContent)
                ]
                content_json = json.dumps(content_list)
                is_error = tool_output.isError if tool_output else False
                tool_result_blocks.append(
                    cls._build_tool_result(tool_call_id, content_json, is_error)
                )
            except Exception as e:
                error_message = f"Error executing tool '{tool_name}': {e}"
                print(error_message)
                tool_result_blocks.append(
                    cls._build_tool_result(
                        tool_call_id,
                        json.dumps({"error": error_message}),
                        True
                    )
                )

        return tool_result_blocks
