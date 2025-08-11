from deepseek_mcp_client import DeepSeekClient

import asyncio

# Crear agent usando deepseek client
agent = DeepSeekClient(
    model='deepseek-chat',
    system_prompt='Eres un asistente especializado en e-commerce.',
    mcp_servers=['http://localhost:8000/mcp/']
)

# Ejecución 
async def main():
    result = await agent.execute('Busca laptops gamer económicas calidad precio')
    print(result.output)

asyncio.run(main())