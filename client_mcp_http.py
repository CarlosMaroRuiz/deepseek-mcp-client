from deepseek_mcp_client import DeepSeekClient
import asyncio

agent = DeepSeekClient(
    model='deepseek-chat',
    mcp_servers=[{
        'url': 'http://localhost:8000/mcp/',
        'timeout': None
    }],

)

async def main():
    result = await agent.execute('What tools do you have available in the server MCP_SQL?')
    print(result.output)

asyncio.run(main())