from deepseek_mcp_client import DeepSeekClient

import asyncio
import httpx



agent = DeepSeekClient(
    model='deepseek-chat')
  

# Ejecución 
async def main():
    result = await agent.execute('cual es la capital de mexico')
    print(result.output)

asyncio.run(main())