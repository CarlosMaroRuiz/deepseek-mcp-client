"""
DeepSeek MCP Client - Cliente para conectar modelos DeepSeek con servidores MCP

Este paquete proporciona una interfaz completa para integrar modelos DeepSeek
con servidores MCP (Model Context Protocol), soportando múltiples tipos de transporte
y funcionalidades avanzadas de monitoreo.
"""

# Importaciones principales con imports absolutos
from deepseek_mcp_client.client.deepseek_client import DeepSeekClient
from deepseek_mcp_client.models.client_result import ClientResult
from deepseek_mcp_client.models.server_config import MCPServerConfig
from deepseek_mcp_client.handlers.message_handler import DeepSeekMessageHandler
from deepseek_mcp_client.utils.logging_config import (
    setup_logging,
    get_logger,
    setup_colored_logging,
    disable_external_logging,
    enable_external_logging
)

# Información del paquete
__version__ = "2.0.0"
__author__ = "Carlos Ruiz"
__email__ = "car06ma15@gmail.com"
__description__ = "Cliente para conectar modelos DeepSeek con servidores MCP"

# Exportaciones principales - Lo que los usuarios pueden importar directamente
__all__ = [
    # Cliente principal
    "DeepSeekClient",
    
    # Modelos de datos
    "ClientResult",
    "MCPServerConfig",
    
    # Handlers
    "DeepSeekMessageHandler",
    
    # Utilidades de logging
    "setup_logging",
    "get_logger", 
    "setup_colored_logging",
    "disable_external_logging",
    "enable_external_logging",
    
    # Metadatos
    "__version__",
    "__author__",
    "__email__",
    "__description__"
]
