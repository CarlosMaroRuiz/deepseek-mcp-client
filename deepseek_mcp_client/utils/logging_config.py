import logging
import sys
from typing import Optional


def setup_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
    include_timestamp: bool = True,
    include_level: bool = True,
    include_name: bool = True
) -> logging.Logger:
    """
    Configurar sistema de logging personalizado
    
    Args:
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Formato personalizado de logging
        include_timestamp: Incluir timestamp en logs
        include_level: Incluir nivel en logs
        include_name: Incluir nombre del logger en logs
    
    Returns:
        Logger configurado
    """
    if format_string is None:
        format_parts = []
        if include_timestamp:
            format_parts.append("%(asctime)s")
        if include_name:
            format_parts.append("%(name)s")
        if include_level:
            format_parts.append("%(levelname)s")
        format_parts.append("%(message)s")
        
        format_string = " - ".join(format_parts)
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        stream=sys.stdout,
        force=True  # Sobrescribir configuración existente
    )
    
    return logging.getLogger("deepseek_mcp_client")


def get_logger(name: str) -> logging.Logger:
    """
    Obtener logger con nombre específico
    
    Args:
        name: Nombre del logger
    
    Returns:
        Logger con el nombre especificado
    """
    return logging.getLogger(f"deepseek_mcp_client.{name}")


def set_log_level(level: str):
    """
    Cambiar nivel de logging global
    
    Args:
        level: Nuevo nivel de logging
    """
    root_logger = logging.getLogger("deepseek_mcp_client")
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # También actualizar handlers
    for handler in root_logger.handlers:
        handler.setLevel(getattr(logging, level.upper()))


def enable_external_logging(level: str = "INFO"):
    """
    Re-enable logging from external libraries
    
    Args:
        level: Logging level to set for external libraries
    """
    log_level = getattr(logging, level.upper())
    
    # Re-enable httpx logs
    logging.getLogger("httpx").setLevel(log_level)
    
    # Re-enable openai logs
    logging.getLogger("openai").setLevel(log_level)
    
    # Re-enable urllib3 logs
    logging.getLogger("urllib3").setLevel(log_level)
    
    # Re-enable requests logs
    logging.getLogger("requests").setLevel(log_level)
    
    # Re-enable MCP related logs
    logging.getLogger("mcp").setLevel(log_level)
    logging.getLogger("mcp.client").setLevel(log_level)
    logging.getLogger("mcp.client.streamable_http").setLevel(log_level)
    logging.getLogger("mcp.client.stdio").setLevel(log_level)
    
    # Re-enable FastMCP logs
    logging.getLogger("fastmcp").setLevel(log_level)
    
    # Set root logging to the specified level
    logging.getLogger().setLevel(log_level)


def disable_external_logging():
    """
    Disable logging from noisy external libraries
    """
    # Disable httpx logs
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    # Disable openai logs
    logging.getLogger("openai").setLevel(logging.WARNING)
    
    # Disable urllib3 logs
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    # Disable requests logs
    logging.getLogger("requests").setLevel(logging.WARNING)
    
    # Disable MCP related logs
    logging.getLogger("mcp").setLevel(logging.WARNING)
    logging.getLogger("mcp.client").setLevel(logging.WARNING)
    logging.getLogger("mcp.client.streamable_http").setLevel(logging.WARNING)
    logging.getLogger("mcp.client.stdio").setLevel(logging.WARNING)
    
    # Disable FastMCP logs
    logging.getLogger("fastmcp").setLevel(logging.WARNING)
    
    # Set root logging to WARNING to suppress most INFO messages
    logging.getLogger().setLevel(logging.WARNING)


class ColoredFormatter(logging.Formatter):
    """
    Formatter that adds colors to logs
    """
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record):
        # Apply color based on level
        level_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset_color = self.COLORS['RESET']
        
        # Format original message
        original_format = super().format(record)
        
        # Add colors
        colored_format = f"{level_color}{original_format}{reset_color}"
        
        return colored_format


def setup_colored_logging(level: str = "INFO") -> logging.Logger:
    """
    Setup logging with colors
    
    Args:
        level: Logging level
    
    Returns:
        Logger with colored format
    """
    logger = logging.getLogger("deepseek_mcp_client")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create new handler with colors
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level.upper()))
    
    # Apply colored formatter
    formatter = ColoredFormatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger