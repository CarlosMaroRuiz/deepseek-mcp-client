from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Any, Optional


@dataclass
class ClientResult:
    output: str
    success: bool
    execution_id: str
    timestamp: datetime
    tools_used: List[str]
    metadata: Dict[str, Any]
    raw_response: Optional[Any] = None
    error: Optional[str] = None
    
    def __str__(self) -> str:
        """Representación string del resultado"""
        status = "✅ ÉXITO" if self.success else "❌ ERROR"
        return f"{status} [{self.execution_id}] - {len(self.tools_used)} herramientas usadas"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        return {
            "output": self.output,
            "success": self.success,
            "execution_id": self.execution_id,
            "timestamp": self.timestamp.isoformat(),
            "tools_used": self.tools_used,
            "metadata": self.metadata,
            "error": self.error
        }