from cli_project.core.claude import Claude
from cli_project.mcp_client import MCPClient
from cli_project.core.tools import ToolManager


class Chat:
    def __init__(self, claude_service: Claude, clients: dict):
        self.claude_service: Claude = claude_service
        self.clients: dict = clients
        self.messages: list = []

    async def _process_query(self, query: str):
        self.messages.append({"role": "user", "content": query})

    async def run(self, query: str) -> str:
        final_text_response = ""

        await self._process_query(query)

        while True:
            response = self.claude_service.chat(
                messages=self.messages,
                tools=await ToolManager.get_all_tools(self.clients),
            )

            self.claude_service.add_assistant_message(self.messages, response)

            # Use get_stop_reason to normalize OpenRouter → Anthropic naming
            stop_reason = self.claude_service.get_stop_reason(response)

            if stop_reason == "tool_use":
                print(self.claude_service.text_from_message(response))
                tool_result_parts = await ToolManager.execute_tool_requests(
                    self.clients, response
                )
                # OpenRouter tool results appended individually
                for tool_result in tool_result_parts:
                    self.messages.append(tool_result)
            else:
                final_text_response = self.claude_service.text_from_message(response)
                break

        return final_text_response
