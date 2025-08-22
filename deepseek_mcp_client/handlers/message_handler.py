"""
Handler para mensajes MCP del cliente DeepSeek
"""
import logging
from typing import Optional, Callable, Any
from fastmcp.client.messages import MessageHandler
import mcp.types


class DeepSeekMessageHandler(MessageHandler):
    """Handler personalizado para mensajes MCP"""
    
    def __init__(
        self, 
        logger: Optional[logging.Logger] = None,
        on_tools_changed: Optional[Callable[[], None]] = None,
        on_resources_changed: Optional[Callable[[], None]] = None,
        on_progress_update: Optional[Callable[[float, Optional[float], Optional[str]], None]] = None
    ):
        """
        Inicializar handler con callbacks opcionales
        
        Args:
            logger: Logger para mensajes
            on_tools_changed: Callback cuando cambian las herramientas
            on_resources_changed: Callback cuando cambian los recursos
            on_progress_update: Callback para actualizaciones de progreso
        """
        self.logger = logger or logging.getLogger(__name__)
        self.tool_cache_dirty = False
        self.resource_cache_dirty = False
        self.prompt_cache_dirty = False
        
        # Callbacks opcionales
        self._on_tools_changed = on_tools_changed
        self._on_resources_changed = on_resources_changed
        self._on_progress_update = on_progress_update
        
        # Estadísticas
        self.stats = {
            "tools_changed_count": 0,
            "resources_changed_count": 0,
            "prompts_changed_count": 0,
            "progress_updates_count": 0
        }
    
    async def on_tool_list_changed(self, notification: mcp.types.ToolListChangedNotification):
        """Maneja cambios en la lista de herramientas"""
        self.logger.info("Tool list updated")
        self.tool_cache_dirty = True
        self.stats["tools_changed_count"] += 1
        
        if self._on_tools_changed:
            try:
                self._on_tools_changed()
            except Exception as e:
                self.logger.error(f"Error in tools changed callback: {e}")
    
    async def on_resource_list_changed(self, notification: mcp.types.ResourceListChangedNotification):
        """Maneja cambios en la lista de recursos"""
        self.logger.info("Resource list updated")
        self.resource_cache_dirty = True
        self.stats["resources_changed_count"] += 1
        
        if self._on_resources_changed:
            try:
                self._on_resources_changed()
            except Exception as e:
                self.logger.error(f"Error in resources changed callback: {e}")
    
    async def on_prompt_list_changed(self, notification: mcp.types.PromptListChangedNotification):
        """Maneja cambios en la lista de prompts"""
        self.logger.info("Prompt list updated")
        self.prompt_cache_dirty = True
        self.stats["prompts_changed_count"] += 1
    
    async def on_progress(self, notification: mcp.types.ProgressNotification):
        """Maneja notificaciones de progreso"""
        progress = notification.progress
        total = getattr(notification, 'total', None)
        
        if total:
            percentage = (progress / total) * 100
            message = f"Progress: {percentage:.1f}% ({progress}/{total})"
        else:
            message = f"Progress: {progress}"
        
        self.logger.info(message)
        self.stats["progress_updates_count"] += 1
        
        if self._on_progress_update:
            try:
                self._on_progress_update(progress, total, message)
            except Exception as e:
                self.logger.error(f"Error in progress update callback: {e}")
    
    def has_cache_changes(self) -> bool:
        """Verificar si hay cambios pendientes en cache"""
        return (
            self.tool_cache_dirty or 
            self.resource_cache_dirty or 
            self.prompt_cache_dirty
        )
    
    def clear_cache_flags(self):
        """Limpiar flags de cache dirty"""
        self.tool_cache_dirty = False
        self.resource_cache_dirty = False
        self.prompt_cache_dirty = False
    
    def get_stats(self) -> dict:
        """Obtener estadísticas del handler"""
        return self.stats.copy()
    
    def reset_stats(self):
        """Resetear estadísticas"""
        for key in self.stats:
            self.stats[key] = 0