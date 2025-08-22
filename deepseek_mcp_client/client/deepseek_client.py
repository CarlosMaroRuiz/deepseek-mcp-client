"""
Cliente principal DeepSeek con soporte MCP
"""
import json
import os
import uuid
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging

from openai import OpenAI
from dotenv import load_dotenv
from fastmcp import Client, FastMCP
from fastmcp.client.transports import StdioTransport, StreamableHttpTransport
from fastmcp.client.logging import LogMessage

# Imports absolutos - ESTO ES LA CLAVE
from deepseek_mcp_client.models.client_result import ClientResult
from deepseek_mcp_client.models.server_config import MCPServerConfig
from deepseek_mcp_client.handlers.message_handler import DeepSeekMessageHandler
from deepseek_mcp_client.utils.logging_config import disable_external_logging

load_dotenv()


class DeepSeekClient:
    """
    Cliente DeepSeek con soporte completo para MCP
    """
    
    def __init__(
        self,
        model: str,
        system_prompt: Optional[str] = None,
        mcp_servers: Optional[List[Union[str, Dict[str, Any], FastMCP, MCPServerConfig]]] = None,
        enable_logging: bool = False,
        enable_progress: bool = False,
        log_level: str = "INFO"
    ):
        """
        Inicializar DeepSeekClient
        """
        self.model = model
        self.system_prompt = system_prompt or "You are a helpful and friendly assistant."
        self.mcp_servers = mcp_servers or []
        self.enable_logging = enable_logging
        self.enable_progress = enable_progress
        
        # Configurar logging
        self._setup_logging(log_level)
        
        # Configurar logs externos según la preferencia del usuario
        if not self.enable_logging:
            disable_external_logging()
        
        # Configurar cliente DeepSeek
        self._setup_deepseek_client()
        
        # Estado interno
        self.clients: List[Client] = []
        self.all_tools: List[Dict[str, Any]] = []
        self.tool_to_client: Dict[str, Client] = {}
        self.message_handlers: List[DeepSeekMessageHandler] = []
        self._connected = False
        
        # Log de configuración inicial
        self._log_initialization()
    
    def _setup_logging(self, log_level: str):
        """Configurar sistema de logging"""
        if self.enable_logging:
            logging.basicConfig(
                level=getattr(logging, log_level.upper()),
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        self.logger = logging.getLogger(__name__)
    
    def _setup_deepseek_client(self):
        """Configurar cliente DeepSeek"""
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("Configure DEEPSEEK_API_KEY in environment variables")
        
        self.deepseek_client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )
    
    def _log_initialization(self):
        """Log de inicialización"""
        if self.enable_logging:
            if self.mcp_servers:
                self.logger.info(f"Initialized with {len(self.mcp_servers)} MCP servers")
            else:
                self.logger.info("Initialized in direct mode (no MCP servers)")
    
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
            return self._parse_string_config(server_config)
        
        elif isinstance(server_config, dict):
            return self._parse_dict_config(server_config)
        
        else:
            raise ValueError(f"Unsupported server configuration type: {type(server_config)}")
    
    def _parse_string_config(self, config: str) -> MCPServerConfig:
        """Parsear configuración string"""
        if config.startswith(('http://', 'https://')):
            return MCPServerConfig(url=config, transport_type='http')
        elif config.endswith('.py'):
            return MCPServerConfig(command='python', args=[config], transport_type='stdio')
        elif config.endswith('.js'):
            return MCPServerConfig(command='node', args=[config], transport_type='stdio')
        else:
            raise ValueError(f"Cannot determine transport type for: {config}")
    
    def _parse_dict_config(self, config: dict) -> MCPServerConfig:
        """Parsear configuración diccionario"""
        mcp_config = MCPServerConfig(**config)
        
        if not mcp_config.transport_type:
            if mcp_config.url:
                mcp_config.transport_type = 'http'
            elif mcp_config.command:
                mcp_config.transport_type = 'stdio'
            elif mcp_config.fastmcp_instance:
                mcp_config.transport_type = 'memory'
            else:
                raise ValueError("Incomplete server configuration")
        
        return mcp_config
    
    def _create_client(self, config: MCPServerConfig) -> Client:
        """Crear cliente FastMCP según la configuración"""
        message_handler = DeepSeekMessageHandler(self.logger)
        self.message_handlers.append(message_handler)
        
        # Configurar handlers
        log_handler = self._create_log_handler() if self.enable_logging else None
        progress_handler = self._create_progress_handler() if self.enable_progress else None
        
        # Crear transporte según tipo
        if config.transport_type == 'http':
            transport = StreamableHttpTransport(
                url=config.url,
                headers=config.headers or {}
            )
        elif config.transport_type == 'stdio':
            transport = StdioTransport(
                command=config.command,
                args=config.args or [],
                env=config.env or {},
                cwd=config.cwd,
                keep_alive=config.keep_alive
            )
        elif config.transport_type == 'memory':
            transport = config.fastmcp_instance
        else:
            raise ValueError(f"Unsupported transport type: {config.transport_type}")
        
        return Client(
            transport,
            log_handler=log_handler,
            progress_handler=progress_handler,
            message_handler=message_handler,
            timeout=config.timeout
        )
    
    def _create_log_handler(self):
        """Crear handler de logs"""
        async def log_handler(message: LogMessage):
            if self.enable_logging:
                level_map = logging.getLevelNamesMapping()
                level = level_map.get(message.level.upper(), logging.INFO)
                msg = message.data.get('msg', '')
                extra = message.data.get('extra', {})
                self.logger.log(level, f"MCP Server: {msg}", extra=extra)
        
        return log_handler
    
    def _create_progress_handler(self):
        """Crear handler de progreso"""
        async def progress_handler(progress: float, total: float | None, message: str | None):
            if self.enable_progress:
                if total is not None:
                    percentage = (progress / total) * 100
                    self.logger.info(f"Progress: {percentage:.1f}% - {message or ''}")
                else:
                    self.logger.info(f"Progress: {progress} - {message or ''}")
        
        return progress_handler
    
    async def _connect_mcp_servers(self) -> None:
        """Conectar a todos los servidores MCP"""
        if self._connected or not self.mcp_servers:
            return
        
        if self.enable_logging:
            self.logger.info(f"Connecting to {len(self.mcp_servers)} MCP servers...")
        
        for i, server_config in enumerate(self.mcp_servers):
            await self._connect_single_server(i, server_config)
        
        self._connected = True
        if self.enable_logging:
            self.logger.info(f"Connection completed. {len(self.all_tools)} tools available")
    
    async def _connect_single_server(self, index: int, server_config):
        """Conectar a un servidor individual"""
        try:
            config = self._parse_server_config(server_config)
            if self.enable_logging:
                self.logger.info(f"Connecting to server {index+1} ({config.transport_type})")
            
            client = self._create_client(config)
            
            # Probar conexión
            async with client:
                await client.ping()
                tools = await client.list_tools()
                if self.enable_logging:
                    self.logger.info(f"Found {len(tools)} tools")
            
            self.clients.append(client)
            await self._load_tools_from_client(client)
            
        except Exception as e:
            if self.enable_logging:
                self.logger.error(f"Error connecting to server {index+1}: {e}")
    
    async def _load_tools_from_client(self, client: Client) -> None:
        """Cargar herramientas de un cliente"""
        async with client:
            tools = await client.list_tools()
            
            for tool in tools:
                deepseek_tool = {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description or f"Tool: {tool.name}",
                        "parameters": tool.inputSchema or {"type": "object", "properties": {}}
                    }
                }
                
                self.all_tools.append(deepseek_tool)
                self.tool_to_client[tool.name] = client
    
    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Ejecutar herramienta MCP con manejo de progreso"""
        client = self.tool_to_client.get(tool_name)
        if not client:
            return f"Error: Tool {tool_name} not found"
        
        try:
            if self.enable_logging:
                self.logger.info(f"Executing {tool_name}")
            
            async with client:
                tool_progress_handler = self._create_tool_progress_handler(tool_name)
                
                result = await client.call_tool(
                    tool_name, 
                    arguments,
                    progress_handler=tool_progress_handler if self.enable_progress else None
                )
                
                return self._format_tool_result(result, tool_name)
        
        except Exception as e:
            if self.enable_logging:
                self.logger.error(f"Error executing {tool_name}: {e}")
            return f"Error executing {tool_name}: {e}"
    
    def _create_tool_progress_handler(self, tool_name: str):
        """Crear handler de progreso para herramienta específica"""
        async def tool_progress_handler(progress: float, total: float | None, message: str | None):
            if self.enable_progress:
                if total is not None:
                    percentage = (progress / total) * 100
                    self.logger.info(f"{tool_name}: {percentage:.1f}% - {message or ''}")
                else:
                    self.logger.info(f"{tool_name}: {progress} - {message or ''}")
        
        return tool_progress_handler
    
    def _format_tool_result(self, result, tool_name: str) -> str:
        """Formatear resultado de herramienta"""
        if isinstance(result, dict):
            if 'error' in result:
                return f"Error in {tool_name}: {result['error']}"
            elif 'content' in result:
                return str(result['content'])
            else:
                return json.dumps(result, indent=2, ensure_ascii=False)
        else:
            return str(result)
    
    async def refresh_tools(self) -> None:
        """Refrescar herramientas si hay cambios"""
        for handler in self.message_handlers:
            if handler.tool_cache_dirty:
                await self._refresh_tool_cache()
                break
    
    async def _refresh_tool_cache(self):
        """Refrescar cache de herramientas"""
        if self.enable_logging:
            self.logger.info("Refreshing tool cache...")
        self.all_tools.clear()
        self.tool_to_client.clear()
        
        for client in self.clients:
            await self._load_tools_from_client(client)
        
        # Limpiar flags de todos los handlers
        for handler in self.message_handlers:
            handler.tool_cache_dirty = False
        
        if self.enable_logging:
            self.logger.info(f"Cache updated. {len(self.all_tools)} tools available")
    
    async def execute(self, instruction: str) -> ClientResult:
        """Ejecutar instrucción con soporte completo MCP"""
        execution_id = str(uuid.uuid4())[:8]
        start_time = datetime.now()
        tools_used = []
        
        try:
            # Conectar a MCP si es necesario
            if self.mcp_servers and not self._connected:
                await self._connect_mcp_servers()
            
            # Refrescar herramientas si es necesario
            if self.clients:
                await self.refresh_tools()
            
            if self.enable_logging:
                self.logger.info(f"Executing: {instruction}")
            
            # Preparar y ejecutar primera llamada
            response = await self._execute_initial_call(instruction)
            message = response.choices[0].message
            
            # Si no hay herramientas a ejecutar
            if not message.tool_calls:
                return self._create_direct_result(response, execution_id, start_time)
            
            # Ejecutar herramientas y obtener respuesta final
            final_response = await self._execute_tools_and_get_final_response(
                message, instruction, tools_used
            )
            
            return self._create_success_result(
                final_response, execution_id, start_time, tools_used
            )
        
        except Exception as e:
            if self.enable_logging:
                self.logger.error(f"Error in execution: {e}")
            return self._create_error_result(e, execution_id, start_time, tools_used)
    
    async def _execute_initial_call(self, instruction: str):
        """Ejecutar llamada inicial a DeepSeek"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": instruction}
        ]
        
        chat_params = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 4000,
            "temperature": 0.7
        }
        
        if self.all_tools:
            chat_params["tools"] = self.all_tools
            if self.enable_logging:
                self.logger.info(f"Sending {len(self.all_tools)} tools to DeepSeek")
        else:
            if self.enable_logging:
                self.logger.info("Executing in direct mode (no tools)")
        
        return self.deepseek_client.chat.completions.create(**chat_params)
    
    async def _execute_tools_and_get_final_response(self, message, instruction: str, tools_used: List[str]):
        """Ejecutar herramientas y obtener respuesta final"""
        if self.enable_logging:
            self.logger.info(f"Executing {len(message.tool_calls)} tools")
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": instruction}
        ]
        
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
        if self.enable_logging:
            self.logger.info("DeepSeek processing results...")
        
        return self.deepseek_client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.all_tools if self.all_tools else None,
            max_tokens=4000,
            temperature=0.7
        )
    
    def _create_direct_result(self, response, execution_id: str, start_time: datetime) -> ClientResult:
        """Crear resultado para respuesta directa"""
        return ClientResult(
            output=response.choices[0].message.content or "Empty response",
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
    
    def _create_success_result(self, response, execution_id: str, start_time: datetime, tools_used: List[str]) -> ClientResult:
        """Crear resultado exitoso"""
        return ClientResult(
            output=response.choices[0].message.content or "Empty response",
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
            raw_response=response
        )
    
    def _create_error_result(self, error: Exception, execution_id: str, start_time: datetime, tools_used: List[str]) -> ClientResult:
        """Crear resultado de error"""
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
                "error_type": type(error).__name__
            },
            error=str(error)
        )
    
    async def close(self):
        """Cerrar todas las conexiones"""
        if self.clients:
            if self.enable_logging:
                self.logger.info("Closing connections...")
            for client in self.clients:
                try:
                    pass  # FastMCP maneja el cierre automáticamente
                except Exception as e:
                    if self.enable_logging:
                        self.logger.warning(f"Error closing client: {e}")
            
            self.clients.clear()
            self._connected = False
            if self.enable_logging:
                self.logger.info("Connections closed")
        else:
            if self.enable_logging:
                self.logger.info("No connections to close")
    
    # Métodos de utilidad
    def get_available_tools(self) -> List[str]:
        """Obtener lista de herramientas disponibles"""
        return [tool["function"]["name"] for tool in self.all_tools]
    
    def get_server_count(self) -> int:
        """Obtener número de servidores conectados"""
        return len(self.clients)
    
    def is_connected(self) -> bool:
        """Verificar si está conectado a servidores MCP"""
        return self._connected
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del cliente"""
        return {
            "servers_configured": len(self.mcp_servers),
            "servers_connected": len(self.clients),
            "tools_available": len(self.all_tools),
            "is_connected": self._connected
        }