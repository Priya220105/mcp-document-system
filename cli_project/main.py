import asyncio
import sys
import os
from dotenv import load_dotenv
from contextlib import AsyncExitStack

from cli_project.mcp_client import MCPClient
from cli_project.core.claude import Claude
from cli_project.core.cli_chat import CliChat
from cli_project.core.cli import CliApp
load_dotenv()

# OpenRouter Config (free - no cost!)
openrouter_model = os.getenv("OPENROUTER_MODEL", "qwen/qwen-2.5-72b-instruct")
openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "")

assert openrouter_api_key, (
    "Error: OPENROUTER_API_KEY cannot be empty. Update .env\n"
    "Get a free key at: https://openrouter.ai/keys"
)


async def main():
    claude_service = Claude(model=openrouter_model)

    server_scripts = sys.argv[1:]

    command, args = (
        ("python", ["-m", "cli_project.mcp_server"])
        
    )

    async with AsyncExitStack() as stack:
        doc_client = await stack.enter_async_context(
            MCPClient(command=command, args=args)
        )
        clients = {"doc_client": doc_client}

        for i, server_script in enumerate(server_scripts):
            client_id = f"client_{i}_{server_script}"
            client = await stack.enter_async_context(
                MCPClient(command="uv", args=["run", server_script])
            )
            clients[client_id] = client

        chat = CliChat(
            doc_client=doc_client,
            clients=clients,
            claude_service=claude_service,
        )

        cli = CliApp(chat)
        await cli.initialize()
        await cli.run()


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
