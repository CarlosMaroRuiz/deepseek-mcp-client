import json
import os
import uuid
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import logging

from openai import OpenAI
from dotenv import load_dotenv
from fastmcp import Client, FastMCP
from fastmcp.client.transports import StdioTransport, StreamableHttpTransport
from fastmcp.client.messages import MessageHandler
from fastmcp.client.logging import LogMessage
import mcp.types

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


@dataclass
class MCPServerConfig:
    """Configuración de servidor MCP"""
    # Para HTTP/HTTPS
    url: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    
    # Para STDIO
    command: Optional[str] = None
    args: Optional[List[str]] = None
    env: Optional[Dict[str, str]] = None
    cwd: Optional[str] = None
    
    # Para in-memory
    fastmcp_instance: Optional[FastMCP] = None
    
    # Configuración general
    transport_type: Optional[str] = None  # 'http', 'stdio', 'memory'
    keep_alive: bool = True
    timeout: float = 30.0


class DeepSeekMessageHandler(MessageHandler):
    """Handler personalizado para mensajes MCP"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.tool_cache_dirty = False
        self.resource_cache_dirty = False
    
    async def on_tool_list_changed(self, notification: mcp.types.ToolListChangedNotification):
        """Maneja cambios en la lista de herramientas"""
        self.logger.info("🔄 Lista de herramientas actualizada")
        self.tool_cache_dirty = True
    
    async def on_resource_list_changed(self, notification: mcp.types.ResourceListChangedNotification):
        """Maneja cambios en la lista de recursos"""
        self.logger.info("🔄 Lista de recursos actualizada")
        self.resource_cache_dirty = True
    
    async def on_prompt_list_changed(self, notification: mcp.types.PromptListChangedNotification):
        """Maneja cambios en la lista de prompts"""
        self.logger.info("🔄 Lista de prompts actualizada")
    
    async def on_progress(self, notification: mcp.types.ProgressNotification):
        """Maneja notificaciones de progreso"""
        progress = notification.progress
        total = getattr(notification, 'total', None)
        if total:
            percentage = (progress / total) * 100
            self.logger.info(f"📊 Progreso: {percentage:.1f}% ({progress}/{total})")
        else:
            self.logger.info(f"📊 Progreso: {progress}")


class DeepSeekClient:
    """
    Cliente DeepSeek con soporte completo para MCP - Versión Limpia
    
    Ejemplos de uso:
    
    # Uso mínimo
    agent = DeepSeekClient(model='deepseek-chat')
    
    # Con prompt personalizado
    agent = DeepSeekClient(
        model='deepseek-chat',
        system_prompt='Eres un asistente especializado...'
    )
    
    # Con servidores MCP
    agent = DeepSeekClient(
        model='deepseek-chat',
        system_prompt='Eres un asistente...',
        mcp_servers=['http://localhost:8000/mcp/']
    )
    """
    
    def __init__(
        self,
        model: str,
        system_prompt: Optional[str] = None,
        mcp_servers: Optional[List[Union[str, Dict[str, Any], FastMCP, MCPServerConfig]]] = None,
        enable_logging: bool = True,
        enable_progress: bool = True,
        log_level: str = "INFO"
    ):
        """
        Inicializar DeepSeekClient con parámetros opcionales
        
        Args:
            model: Modelo DeepSeek (ej: 'deepseek-chat') - REQUERIDO
            system_prompt: Prompt del sistema (OPCIONAL)
            mcp_servers: Lista de configuraciones de servidores MCP (OPCIONAL)
            enable_logging: Habilitar logging de servidores MCP
            enable_progress: Habilitar monitoreo de progreso
            log_level: Nivel de logging
        """
        self.model = model
        self.system_prompt = system_prompt or "Eres un asistente útil y amigable."
        self.mcp_servers = mcp_servers or []
        self.enable_logging = enable_logging
        self.enable_progress = enable_progress
        
        # Configurar logging
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
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
        self.message_handlers: List[DeepSeekMessageHandler] = []
        self._connected = False
        
        # Log de configuración inicial
        if self.mcp_servers:
            self.logger.info(f"🔧 Inicializado con {len(self.mcp_servers)} servidores MCP")
        else:
            self.logger.info("🤖 Inicializado en modo directo (sin MCP)")
    
    def _parse_server_config(self, server_config: Union[str, Dict[str, Any], FastMCP, MCPServerConfig]) -> MCPServerConfig:
        """Parsear configuración de servidor a MCPServerConfig"""
        if isinstance(server_config, MCPServerConfig):
            return server_config
        
        elif isinstance(server_config, FastMCP):
            return MCPServerConfig(
                fastmcp_instance=server_config,
                transport_type='memory'
            )
        
        elif isinstance(server_config, str):
            if server_config.startswith(('http://', 'https://')):
                return MCPServerConfig(
                    url=server_config,
                    transport_type='http'
                )
            elif server_config.endswith('.py'):
                return MCPServerConfig(
                    command='python',
                    args=[server_config],
                    transport_type='stdio'
                )
            elif server_config.endswith('.js'):
                return MCPServerConfig(
                    command='node',
                    args=[server_config],
                    transport_type='stdio'
                )
            else:
                raise ValueError(f"No se puede determinar el tipo de transporte para: {server_config}")
        
        elif isinstance(server_config, dict):
            config = MCPServerConfig(**server_config)
            
            if not config.transport_type:
                if config.url:
                    config.transport_type = 'http'
                elif config.command:
                    config.transport_type = 'stdio'
                elif config.fastmcp_instance:
                    config.transport_type = 'memory'
                else:
                    raise ValueError("Configuración de servidor incompleta")
            
            return config
        
        else:
            raise ValueError(f"Tipo de configuración de servidor no soportado: {type(server_config)}")
    
    def _create_client(self, config: MCPServerConfig) -> Client:
        """Crear cliente FastMCP según la configuración"""
        
        message_handler = DeepSeekMessageHandler(self.logger)
        self.message_handlers.append(message_handler)
        
        async def log_handler(message: LogMessage):
            if self.enable_logging:
                level_map = logging.getLevelNamesMapping()
                level = level_map.get(message.level.upper(), logging.INFO)
                msg = message.data.get('msg', '')
                extra = message.data.get('extra', {})
                self.logger.log(level, f"🔧 MCP Server: {msg}", extra=extra)
        
        async def progress_handler(progress: float, total: float | None, message: str | None):
            if self.enable_progress:
                if total is not None:
                    percentage = (progress / total) * 100
                    self.logger.info(f"📊 Progreso: {percentage:.1f}% - {message or ''}")
                else:
                    self.logger.info(f"📊 Progreso: {progress} - {message or ''}")
        
        if config.transport_type == 'http':
            transport = StreamableHttpTransport(
                url=config.url,
                headers=config.headers or {}
            )
            return Client(
                transport,
                log_handler=log_handler if self.enable_logging else None,
                progress_handler=progress_handler if self.enable_progress else None,
                message_handler=message_handler,
                timeout=config.timeout
            )
        
        elif config.transport_type == 'stdio':
            transport = StdioTransport(
                command=config.command,
                args=config.args or [],
                env=config.env or {},
                cwd=config.cwd,
                keep_alive=config.keep_alive
            )
            return Client(
                transport,
                log_handler=log_handler if self.enable_logging else None,
                progress_handler=progress_handler if self.enable_progress else None,
                message_handler=message_handler,
                timeout=config.timeout
            )
        
        elif config.transport_type == 'memory':
            return Client(
                config.fastmcp_instance,
                log_handler=log_handler if self.enable_logging else None,
                progress_handler=progress_handler if self.enable_progress else None,
                message_handler=message_handler,
                timeout=config.timeout
            )
        
        else:
            raise ValueError(f"Tipo de transporte no soportado: {config.transport_type}")
    
    async def _connect_mcp_servers(self) -> None:
        """Conectar a todos los servidores MCP"""
        if self._connected or not self.mcp_servers:
            return
        
        self.logger.info(f"🔌 Conectando a {len(self.mcp_servers)} servidores MCP...")
        
        for i, server_config in enumerate(self.mcp_servers):
            try:
                config = self._parse_server_config(server_config)
                self.logger.info(f"🔗 Conectando servidor {i+1} ({config.transport_type})")
                
                client = self._create_client(config)
                
                async with client:
                    await client.ping()
                    tools = await client.list_tools()
                    self.logger.info(f"🛠️  Encontradas {len(tools)} herramientas")
                
                self.clients.append(client)
                await self._load_tools_from_client(client)
                
            except Exception as e:
                self.logger.error(f"❌ Error conectando servidor {i+1}: {e}")
        
        self._connected = True
        self.logger.info(f"✅ Conexión completada. {len(self.all_tools)} herramientas disponibles")
    
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
        """Ejecutar herramienta MCP con manejo de progreso"""
        client = self.tool_to_client.get(tool_name)
        if not client:
            return f"Error: Herramienta {tool_name} no encontrada"
        
        try:
            self.logger.info(f"🔧 Ejecutando {tool_name}")
            
            async with client:
                async def tool_progress_handler(progress: float, total: float | None, message: str | None):
                    if self.enable_progress:
                        if total is not None:
                            percentage = (progress / total) * 100
                            self.logger.info(f"🔧 {tool_name}: {percentage:.1f}% - {message or ''}")
                        else:
                            self.logger.info(f"🔧 {tool_name}: {progress} - {message or ''}")
                
                result = await client.call_tool(
                    tool_name, 
                    arguments,
                    progress_handler=tool_progress_handler if self.enable_progress else None
                )
                
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
            self.logger.error(f"❌ Error ejecutando {tool_name}: {e}")
            return f"Error ejecutando {tool_name}: {e}"
    
    async def refresh_tools(self) -> None:
        """Refrescar herramientas si hay cambios"""
        for handler in self.message_handlers:
            if handler.tool_cache_dirty:
                self.logger.info("🔄 Refrescando cache de herramientas...")
                self.all_tools.clear()
                self.tool_to_client.clear()
                
                for client in self.clients:
                    await self._load_tools_from_client(client)
                
                handler.tool_cache_dirty = False
                self.logger.info(f"✅ Cache actualizado. {len(self.all_tools)} herramientas disponibles")
                break
    
    async def execute(self, instruction: str) -> ClientResult:
        """Ejecutar instrucción con soporte completo MCP"""
        execution_id = str(uuid.uuid4())[:8]
        start_time = datetime.now()
        tools_used = []
        
        try:
            # Solo conectar a MCP si hay servidores configurados
            if self.mcp_servers and not self._connected:
                await self._connect_mcp_servers()
            
            # Solo refrescar herramientas si hay clientes MCP
            if self.clients:
                await self.refresh_tools()
            
            self.logger.info(f"🤖 Ejecutando: {instruction}")
            
            # Preparar mensajes para DeepSeek
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": instruction}
            ]
            
            # Preparar parámetros para DeepSeek
            chat_params = {
                "model": self.model,
                "messages": messages,
                "max_tokens": 4000,
                "temperature": 0.7
            }
            
            # Solo agregar herramientas si hay alguna disponible
            if self.all_tools:
                chat_params["tools"] = self.all_tools
                self.logger.info(f"🛠️ Enviando {len(self.all_tools)} herramientas a DeepSeek")
            else:
                self.logger.info("🤖 Ejecutando en modo directo (sin herramientas)")
            
            # Primera llamada a DeepSeek
            response = self.deepseek_client.chat.completions.create(**chat_params)
            
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
                        "mcp_enabled": bool(self.mcp_servers),
                        "tools_available": len(self.all_tools),
                        "duration": (datetime.now() - start_time).total_seconds(),
                        "servers_connected": len(self.clients)
                    },
                    raw_response=response
                )
            
            # Ejecutar herramientas solicitadas por DeepSeek
            self.logger.info(f"🔄 Ejecutando {len(message.tool_calls)} herramientas")
            
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
            self.logger.info("🤖 DeepSeek procesando resultados...")
            
            final_response = self.deepseek_client.chat.completions.create(**chat_params)
            
            final_output = final_response.choices[0].message.content or "Respuesta vacía"
            
            return ClientResult(
                output=final_output,
                success=True,
                execution_id=execution_id,
                timestamp=start_time,
                tools_used=tools_used,
                metadata={
                    "model": self.model,
                    "mcp_enabled": bool(self.mcp_servers),
                    "tools_executed": len(tools_used),
                    "tools_available": len(self.all_tools),
                    "duration": (datetime.now() - start_time).total_seconds(),
                    "servers_connected": len(self.clients),
                    "transport_types": [self._parse_server_config(s).transport_type for s in self.mcp_servers] if self.mcp_servers else []
                },
                raw_response=final_response
            )
        
        except Exception as e:
            self.logger.error(f"❌ Error en ejecución: {e}")
            return ClientResult(
                output="",
                success=False,
                execution_id=execution_id,
                timestamp=start_time,
                tools_used=tools_used,
                metadata={
                    "model": self.model,
                    "mcp_enabled": bool(self.mcp_servers),
                    "duration": (datetime.now() - start_time).total_seconds(),
                    "error_type": type(e).__name__
                },
                error=str(e)
            )
    
    async def close(self):
        """Cerrar todas las conexiones"""
        if self.clients:
            self.logger.info("🔌 Cerrando conexiones...")
            for client in self.clients:
                try:
                    pass
                except Exception as e:
                    self.logger.warning(f"⚠️ Error cerrando cliente: {e}")
            
            self.clients.clear()
            self._connected = False
            self.logger.info("✅ Conexiones cerradas")
        else:
            self.logger.info("✅ No hay conexiones que cerrar")