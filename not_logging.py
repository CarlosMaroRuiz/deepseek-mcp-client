from deepseek_mcp_client import DeepSeekClient

import asyncio


agent = DeepSeekClient(
    model='deepseek-chat',
    mcp_servers=[{
        'url': 'http://localhost:8000/mcp',
        'timeout': None  
    }]

)

# Execution 
async def main():
    result = await agent.execute('tienes accesso a las tool')
    print(result.output)

asyncio.run(main())