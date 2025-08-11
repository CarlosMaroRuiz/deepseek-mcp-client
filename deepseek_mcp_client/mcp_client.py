import json
import os
import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from openai import OpenAI
from dotenv import load_dotenv
from fastmcp import Client

load_dotenv()


@dataclass
class ClientResult:
    """Resultado de la ejecución del Agent"""
    output: str
    success: bool
    execution_id: str
    timestamp: datetime
    tools_used: List[str]
    metadata: Dict[str, Any]
    raw_response: Optional[Any] = None
    error: Optional[str] = None


class DeepSeekClient:
    """
    
    Uso :
        agent = AgentDeepSeek(
            model='deepseek-chat',
            system_prompt='Eres un asistente especializado en e-commerce.',
            mcp_servers=['http://localhost:8000/mcp/']
        )
        
        async def main():
            result = await agent.execute('Busca laptops económicas')
            print(result.output)
        
        asyncio.run(main())
    """
    
    def __init__(
        self,
        model: str,
        system_prompt: str,
        mcp_servers: List[str]
    ):
        """
        Inicializar AgentDeepSeek
        
        Args:
            model: Modelo DeepSeek (ej: 'deepseek-chat')
            system_prompt: Prompt del sistema
            mcp_servers: Lista de URLs de servidores MCP
        """
        self.model = model
        self.system_prompt = system_prompt
        self.mcp_servers = mcp_servers
        
        # Configuración automática
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("Configura DEEPSEEK_API_KEY en las variables de entorno")
        
        # Cliente DeepSeek
        self.deepseek_client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )
        
        # Estado interno
        self.clients: List[Client] = []
        self.all_tools: List[Dict[str, Any]] = []
        self.tool_to_client: Dict[str, Client] = {}
        self._connected = False
    
    async def _connect_mcp_servers(self) -> None:
        """Conectar a servidores MCP internamente"""
        if self._connected:
            return
        
        print(f"🔌 Conectando a {len(self.mcp_servers)} servidores MCP...")
        
        for server_url in self.mcp_servers:
            try:
                print(f"🔗 Conectando a {server_url}")
                
                # Crear cliente FastMCP
                client = Client(server_url)
                
                # Verificar conexión
                async with client:
                    await client.ping()
                    tools = await client.list_tools()
                    print(f"🛠️  Encontradas {len(tools)} herramientas")
                
                # Guardar cliente
                self.clients.append(client)
                await self._load_tools_from_client(client)
                
            except Exception as e:
                print(f"❌ Error conectando a {server_url}: {e}")
        
        self._connected = True
        print(f"✅ Conexión completada. {len(self.all_tools)} herramientas disponibles")
    
    async def _load_tools_from_client(self, client: Client) -> None:
        """Cargar herramientas de un cliente"""
        async with client:
            tools = await client.list_tools()
            
            for tool in tools:
                deepseek_tool = {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description or f"Herramienta: {tool.name}",
                        "parameters": tool.inputSchema or {"type": "object", "properties": {}}
                    }
                }
                
                self.all_tools.append(deepseek_tool)
                self.tool_to_client[tool.name] = client
    
    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Ejecutar herramienta MCP"""
        client = self.tool_to_client.get(tool_name)
        if not client:
            return f"Error: Herramienta {tool_name} no encontrada"
        
        try:
            print(f"🔧 Ejecutando {tool_name}")
            
            async with client:
                result = await client.call_tool(tool_name, arguments)
                
                # Convertir resultado a string
                if isinstance(result, dict):
                    if 'error' in result:
                        return f"Error en {tool_name}: {result['error']}"
                    elif 'content' in result:
                        return str(result['content'])
                    else:
                        return json.dumps(result, indent=2, ensure_ascii=False)
                else:
                    return str(result)
        
        except Exception as e:
            return f"Error ejecutando {tool_name}: {e}"
    
    async def execute(self, instruction: str) -> ClientResult:
        """
        Ejecutar instrucción principal
        
        Args:
            instruction: Instrucción del usuario
            
        Returns:
            AgentResult con la respuesta
        """
        execution_id = str(uuid.uuid4())[:8]
        start_time = datetime.now()
        tools_used = []
        
        try:
            # Conectar a MCP si es necesario
            if not self._connected:
                await self._connect_mcp_servers()
            
            print(f"🤖 Ejecutando: {instruction}")
            
            # Preparar mensajes para DeepSeek
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": instruction}
            ]
            
            # Primera llamada a DeepSeek
            response = self.deepseek_client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.all_tools,
                max_tokens=4000,
                temperature=0.7
            )
            
            message = response.choices[0].message
            
            # Si no hay herramientas a ejecutar
            if not message.tool_calls:
                return ClientResult(
                    output=message.content or "Respuesta vacía",
                    success=True,
                    execution_id=execution_id,
                    timestamp=start_time,
                    tools_used=[],
                    metadata={
                        "model": self.model,
                        "direct_response": True,
                        "duration": (datetime.now() - start_time).total_seconds()
                    },
                    raw_response=response
                )
            
            # Ejecutar herramientas solicitadas por DeepSeek
            print(f"🔄 Ejecutando {len(message.tool_calls)} herramientas")
            
            # Agregar respuesta de DeepSeek al historial
            messages.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    } for tc in message.tool_calls
                ]
            })
            
            # Ejecutar cada herramienta
            for tool_call in message.tool_calls:
                try:
                    arguments = json.loads(tool_call.function.arguments)
                except:
                    arguments = {}
                
                tools_used.append(tool_call.function.name)
                result = await self._execute_tool(tool_call.function.name, arguments)
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
            
            # Segunda llamada a DeepSeek con resultados
            print("🤖 DeepSeek procesando resultados...")
            
            final_response = self.deepseek_client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.all_tools,
                max_tokens=4000,
                temperature=0.7
            )
            
            final_output = final_response.choices[0].message.content or "Respuesta vacía"
            
            return ClientResult(
                output=final_output,
                success=True,
                execution_id=execution_id,
                timestamp=start_time,
                tools_used=tools_used,
                metadata={
                    "model": self.model,
                    "tools_executed": len(tools_used),
                    "duration": (datetime.now() - start_time).total_seconds(),
                    "servers_connected": len(self.clients)
                },
                raw_response=final_response
            )
        
        except Exception as e:
            return ClientResult(
                output="",
                success=False,
                execution_id=execution_id,
                timestamp=start_time,
                tools_used=tools_used,
                metadata={
                    "model": self.model,
                    "duration": (datetime.now() - start_time).total_seconds()
                },
                error=str(e)
            )