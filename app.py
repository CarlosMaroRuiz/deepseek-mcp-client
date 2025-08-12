from deepseek_mcp_client import DeepSeekClient

import asyncio


agent = DeepSeekClient(
    model='deepseek-chat',
    system_prompt='Eres un asistente especializado en e-commerce.',
    mcp_servers=[{
        'url': 'http://localhost:8000/mcp/',
        'timeout': None  
    },]
    
)

# Ejecución 
async def main():
    result = await agent.execute('Busca laptops gamer económicas calidad precio')
    print(result.output)

asyncio.run(main())