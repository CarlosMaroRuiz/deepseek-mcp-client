
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from fastmcp import FastMCP


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
    
    # Metadatos
    name: Optional[str] = None
    description: Optional[str] = None
    
    def __post_init__(self):
        """Validaciones después de la inicialización"""
        if not self.transport_type:
            self.transport_type = self._detect_transport_type()
        
        if not self.name:
            self.name = self._generate_name()
    
    def _detect_transport_type(self) -> str:
        """Auto-detectar tipo de transporte"""
        if self.url:
            return 'http'
        elif self.command:
            return 'stdio'
        elif self.fastmcp_instance:
            return 'memory'
        else:
            raise ValueError("No se puede determinar el tipo de transporte")
    
    def _generate_name(self) -> str:
        """Generar nombre automático"""
        if self.url:
            return f"HTTP_{self.url.split('/')[-2] if '/' in self.url else 'server'}"
        elif self.command:
            return f"STDIO_{self.command}_{self.args[0] if self.args else 'server'}"
        elif self.fastmcp_instance:
            return f"MEMORY_{self.fastmcp_instance.name}"
        else:
            return "unknown_server"
    
    def is_valid(self) -> bool:
        """Verificar si la configuración es válida"""
        if self.transport_type == 'http':
            return bool(self.url)
        elif self.transport_type == 'stdio':
            return bool(self.command)
        elif self.transport_type == 'memory':
            return bool(self.fastmcp_instance)
        return False
    
    def to_dict(self) -> Dict[str, any]:
        """Convertir a diccionario"""
        return {
            "name": self.name,
            "transport_type": self.transport_type,
            "url": self.url,
            "command": self.command,
            "args": self.args,
            "timeout": self.timeout,
            "description": self.description
        }
    
    def __str__(self) -> str:
        """Representación string"""
        return f"MCPServer({self.name}, {self.transport_type})"