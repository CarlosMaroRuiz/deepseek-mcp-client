# DeepSeek MCP Client

Un cliente de Python para conectar modelos de lenguaje DeepSeek con servidores del Protocolo de Contexto de Modelo (MCP), permitiendo una integración perfecta entre modelos de IA y herramientas externas.

## Características

- **Soporte de Múltiples Transportes**: Conexiones HTTP/HTTPS, STDIO y en memoria
- **Configuración Flexible**: Soporte para múltiples servidores MCP simultáneamente  
- **Monitoreo de Progreso**: Seguimiento en tiempo real de operaciones de larga duración
- **Descubrimiento Automático de Herramientas**: Detección y uso dinámico de herramientas disponibles
- **Logging Configurable**: Silencioso por defecto, con logging detallado opcional
- **Recuperación de Errores**: Manejo robusto de errores y gestión de conexiones
- **Arquitectura Modular**: Código base limpio y mantenible con responsabilidades separadas

## Instalación

### Desde PyPI (Recomendado)

```bash
pip install deepseek-mcp-client
```

### Desde el Código Fuente

```bash
git clone https://github.com/CarlosMaroRuiz/deepseek-mcp-client.git
cd deepseek-mcp-client
pip install -e .
```

## Inicio Rápido

### 1. Configurar tu clave API

```bash
export DEEPSEEK_API_KEY="tu_clave_api_aqui"
```

### 2. Uso básico

```python
from deepseek_mcp_client import DeepSeekClient
import asyncio

# Cliente simple sin servidores MCP
client = DeepSeekClient(model='deepseek-chat')

async def main():
    result = await client.execute('Hola, ¿cómo estás?')
    print(result.output)
    await client.close()

asyncio.run(main())
```

## Configuración

### Servidores MCP HTTP

```python
from deepseek_mcp_client import DeepSeekClient

client = DeepSeekClient(
    model='deepseek-chat',
    system_prompt='Eres un asistente útil con acceso a herramientas externas.',
    mcp_servers=[
        'http://localhost:8000/mcp/',  # URL simple
        {
            'url': 'http://localhost:8001/mcp/',
            'headers': {'Authorization': 'Bearer tu-token'},
            'timeout': 30.0
        }
    ]
)
```

### Servidores MCP STDIO

```python
client = DeepSeekClient(
    model='deepseek-chat',
    mcp_servers=[
        {
            'command': 'python',
            'args': ['mcp_server.py'],
            'env': {'LOG_LEVEL': 'INFO'},
            'cwd': './servers/',
            'timeout': 60.0
        }
    ]
)
```

### Configuración Mixta

```python
from fastmcp import FastMCP

# Servidor en memoria
calculator = FastMCP("Calculator")

@calculator.tool
def add(a: float, b: float) -> float:
    """Sumar dos números"""
    return a + b

# Tipos de transporte mixtos
client = DeepSeekClient(
    model='deepseek-chat',
    mcp_servers=[
        'http://localhost:8000/mcp/',           # HTTP
        {                                       # STDIO
            'command': 'python',
            'args': ['local_server.py']
        },
        calculator                              # En memoria
    ]
)
```

## Control de Logging

### Operación Silenciosa (Por Defecto)

```python
# Completamente silencioso - sin logs
client = DeepSeekClient(model='deepseek-chat')
```

### Habilitar Logging

```python
client = DeepSeekClient(
    model='deepseek-chat',
    enable_logging=True,        # Mostrar operaciones del cliente
    enable_progress=True,       # Mostrar actualizaciones de progreso
    log_level="INFO"           # Establecer nivel de logging
)
```

### Logging con Colores

```python
from deepseek_mcp_client import setup_colored_logging

# Habilitar salida con colores
setup_colored_logging("INFO")

client = DeepSeekClient(
    model='deepseek-chat',
    enable_logging=True
)
```

## Uso Avanzado

### Configuración Personalizada de Servidor

```python
from deepseek_mcp_client import MCPServerConfig

# Configuración detallada de servidor HTTP
http_config = MCPServerConfig(
    url='http://localhost:8000/mcp/',
    headers={'X-API-Key': 'tu-clave'},
    timeout=45.0,
    transport_type='http'
)

# Configuración detallada de servidor STDIO
stdio_config = MCPServerConfig(
    command='node',
    args=['server.js', '--port', '3000'],
    env={'NODE_ENV': 'production'},
    cwd='./node-server/',
    timeout=30.0
)

client = DeepSeekClient(
    model='deepseek-chat',
    mcp_servers=[http_config, stdio_config]
)
```

### Manejo de Errores

```python
async def ejecucion_robusta():
    client = DeepSeekClient(
        model='deepseek-chat',
        mcp_servers=['http://localhost:8000/mcp/']
    )
    
    try:
        result = await client.execute('Tu consulta aquí')
        
        if result.success:
            print(f"Éxito: {result.output}")
            print(f"Herramientas usadas: {result.tools_used}")
            print(f"Duración: {result.metadata.get('duration'):.2f}s")
        else:
            print(f"Error: {result.error}")
            
    except Exception as e:
        print(f"Error crítico: {e}")
    finally:
        await client.close()
```

### Trabajando con Resultados

```python
result = await client.execute('Analizar la base de datos')

# Verificar estado de ejecución
if result.success:
    print("Ejecución completada exitosamente")
    
# Acceder a datos de respuesta
print(f"Respuesta: {result.output}")
print(f"ID de ejecución: {result.execution_id}")
print(f"Herramientas usadas: {result.tools_used}")

# Acceder a metadatos
metadata = result.metadata
print(f"Duración: {metadata.get('duration')}s")
print(f"Servidores conectados: {metadata.get('servers_connected')}")
print(f"Herramientas disponibles: {metadata.get('tools_available')}")

# Convertir a diccionario para serialización
result_dict = result.to_dict()
```

## Casos de Uso Comunes

### Análisis de Base de Datos

```python
client = DeepSeekClient(
    model='deepseek-chat',
    system_prompt='Eres un analista de base de datos con experiencia en SQL.',
    mcp_servers=['http://localhost:8000/mcp/']
)

result = await client.execute('''
Analiza la estructura de la tabla user_orders y proporciona información sobre:
1. Esquema de tabla y relaciones
2. Patrones de distribución de datos
3. Sugerencias de optimización de rendimiento
''')
```

### Integración de E-commerce

```python
client = DeepSeekClient(
    model='deepseek-chat',
    system_prompt='Eres un asistente de e-commerce.',
    mcp_servers=[
        'http://localhost:8000/mcp/',  # MCP de búsqueda de productos
        'http://localhost:8001/mcp/'   # MCP de comparación de precios
    ]
)

result = await client.execute(
    'Encuentra las mejores laptops gaming por menos de $1500 y compara precios entre plataformas'
)
```

### Generación de Documentos

```python
client = DeepSeekClient(
    model='deepseek-chat',
    system_prompt='Eres un especialista en generación de documentos.',
    mcp_servers=[
        {
            'command': 'python',
            'args': ['latex_server.py'],
            'env': {'DOCUMENT_TEMPLATE': 'professional'}
        }
    ]
)

result = await client.execute('''
Genera un reporte técnico sobre nuestro rendimiento Q4 con:
- Resumen ejecutivo
- Gráficos de métricas de rendimiento
- Sección de recomendaciones
Exportar en formato PDF
''')
```

## Referencia de API

### DeepSeekClient

```python
DeepSeekClient(
    model: str,                          # Nombre del modelo DeepSeek (requerido)
    system_prompt: str = None,           # Prompt del sistema para el modelo
    mcp_servers: List = None,            # Configuraciones de servidores MCP
    enable_logging: bool = False,        # Habilitar logging del cliente
    enable_progress: bool = False,       # Habilitar monitoreo de progreso
    log_level: str = "INFO"             # Nivel de logging
)
```

### ClientResult

```python
@dataclass
class ClientResult:
    output: str                    # Respuesta del modelo
    success: bool                  # Estado de ejecución
    execution_id: str             # Identificador único de ejecución
    timestamp: datetime           # Marca de tiempo de ejecución
    tools_used: List[str]         # Lista de herramientas ejecutadas
    metadata: Dict[str, Any]      # Metadatos de ejecución
    raw_response: Any = None      # Respuesta cruda del modelo
    error: str = None             # Mensaje de error si falló
```

### MCPServerConfig

```python
@dataclass
class MCPServerConfig:
    # Configuración HTTP
    url: str = None
    headers: Dict[str, str] = None
    
    # Configuración STDIO  
    command: str = None
    args: List[str] = None
    env: Dict[str, str] = None
    cwd: str = None
    
    # Configuración general
    transport_type: str = None    # 'http', 'stdio', 'memory'
    timeout: float = 30.0
    keep_alive: bool = True
```

## Variables de Entorno

```bash
# Requerido
DEEPSEEK_API_KEY=tu_clave_api_deepseek

# Opcional
MCP_LOG_LEVEL=INFO
MCP_TIMEOUT=30
```

## Servidores MCP Compatibles

### Servidores de Producción
- **LaTeX MCP**: Generación de documentos y creación de PDF  
- **Database MCP**: Operaciones de base de datos SQL y análisis
- **Weather MCP**: Datos meteorológicos y pronósticos
- **Web Search MCP**: Búsqueda en internet y recuperación de contenido

### Servidores de Desarrollo
- **FastMCP**: Servidores en memoria para testing y desarrollo
- **Local File MCP**: Operaciones del sistema de archivos
- **Calculator MCP**: Operaciones matemáticas

## Servidores MCP Que Te Podrían Interesar

- **[MCP SQL](https://github.com/CarlosMaroRuiz/mcp_sql)**: Operaciones avanzadas de base de datos SQL con aprendizaje de consultas, análisis de esquemas y características de optimización de rendimiento

---

# DeepSeek MCP Client

A Python client for connecting DeepSeek language models with Model Context Protocol (MCP) servers, enabling seamless integration between AI models and external tools.

## Features

- **Multiple Transport Support**: HTTP/HTTPS, STDIO, and in-memory connections
- **Flexible Configuration**: Support for multiple MCP servers simultaneously  
- **Progress Monitoring**: Real-time tracking of long-running operations
- **Automatic Tool Discovery**: Dynamic detection and usage of available tools
- **Configurable Logging**: Silent by default, with optional detailed logging
- **Error Recovery**: Robust error handling and connection management
- **Modular Architecture**: Clean, maintainable codebase with separated concerns

## Installation

### From PyPI (Recommended)

```bash
pip install deepseek-mcp-client
```

### From Source

```bash
git clone https://github.com/CarlosMaroRuiz/deepseek-mcp-client.git
cd deepseek-mcp-client
pip install -e .
```

## Quick Start

### 1. Set up your API key

```bash
export DEEPSEEK_API_KEY="your_api_key_here"
```

### 2. Basic usage

```python
from deepseek_mcp_client import DeepSeekClient
import asyncio

# Simple client without MCP servers
client = DeepSeekClient(model='deepseek-chat')

async def main():
    result = await client.execute('Hello, how are you?')
    print(result.output)
    await client.close()

asyncio.run(main())
```

## Configuration

### HTTP MCP Servers

```python
from deepseek_mcp_client import DeepSeekClient

client = DeepSeekClient(
    model='deepseek-chat',
    system_prompt='You are a helpful assistant with access to external tools.',
    mcp_servers=[
        'http://localhost:8000/mcp/',  # Simple URL
        {
            'url': 'http://localhost:8001/mcp/',
            'headers': {'Authorization': 'Bearer your-token'},
            'timeout': 30.0
        }
    ]
)
```

### STDIO MCP Servers

```python
client = DeepSeekClient(
    model='deepseek-chat',
    mcp_servers=[
        {
            'command': 'python',
            'args': ['mcp_server.py'],
            'env': {'LOG_LEVEL': 'INFO'},
            'cwd': './servers/',
            'timeout': 60.0
        }
    ]
)
```

### Mixed Configuration

```python
from fastmcp import FastMCP

# In-memory server
calculator = FastMCP("Calculator")

@calculator.tool
def add(a: float, b: float) -> float:
    """Add two numbers"""
    return a + b

# Mixed transport types
client = DeepSeekClient(
    model='deepseek-chat',
    mcp_servers=[
        'http://localhost:8000/mcp/',           # HTTP
        {                                       # STDIO
            'command': 'python',
            'args': ['local_server.py']
        },
        calculator                              # In-memory
    ]
)
```

## Logging Control

### Silent Operation (Default)

```python
# Completely silent - no logs
client = DeepSeekClient(model='deepseek-chat')
```

### Enable Logging

```python
client = DeepSeekClient(
    model='deepseek-chat',
    enable_logging=True,        # Show client operations
    enable_progress=True,       # Show progress updates
    log_level="INFO"           # Set logging level
)
```

### Colored Logging

```python
from deepseek_mcp_client import setup_colored_logging

# Enable colored output
setup_colored_logging("INFO")

client = DeepSeekClient(
    model='deepseek-chat',
    enable_logging=True
)
```

## Advanced Usage

### Custom Server Configuration

```python
from deepseek_mcp_client import MCPServerConfig

# Detailed HTTP server configuration
http_config = MCPServerConfig(
    url='http://localhost:8000/mcp/',
    headers={'X-API-Key': 'your-key'},
    timeout=45.0,
    transport_type='http'
)

# Detailed STDIO server configuration
stdio_config = MCPServerConfig(
    command='node',
    args=['server.js', '--port', '3000'],
    env={'NODE_ENV': 'production'},
    cwd='./node-server/',
    timeout=30.0
)

client = DeepSeekClient(
    model='deepseek-chat',
    mcp_servers=[http_config, stdio_config]
)
```

### Error Handling

```python
async def robust_execution():
    client = DeepSeekClient(
        model='deepseek-chat',
        mcp_servers=['http://localhost:8000/mcp/']
    )
    
    try:
        result = await client.execute('Your query here')
        
        if result.success:
            print(f"Success: {result.output}")
            print(f"Tools used: {result.tools_used}")
            print(f"Duration: {result.metadata.get('duration'):.2f}s")
        else:
            print(f"Error: {result.error}")
            
    except Exception as e:
        print(f"Critical error: {e}")
    finally:
        await client.close()
```

### Working with Results

```python
result = await client.execute('Analyze the database')

# Check execution status
if result.success:
    print("Execution completed successfully")
    
# Access response data
print(f"Response: {result.output}")
print(f"Execution ID: {result.execution_id}")
print(f"Tools used: {result.tools_used}")

# Access metadata
metadata = result.metadata
print(f"Duration: {metadata.get('duration')}s")
print(f"Servers connected: {metadata.get('servers_connected')}")
print(f"Tools available: {metadata.get('tools_available')}")

# Convert to dictionary for serialization
result_dict = result.to_dict()
```

## Common Use Cases

### Database Analysis

```python
client = DeepSeekClient(
    model='deepseek-chat',
    system_prompt='You are a database analyst with SQL expertise.',
    mcp_servers=['http://localhost:8000/mcp/']
)

result = await client.execute('''
Analyze the user_orders table structure and provide insights on:
1. Table schema and relationships
2. Data distribution patterns
3. Performance optimization suggestions
''')
```

### E-commerce Integration

```python
client = DeepSeekClient(
    model='deepseek-chat',
    system_prompt='You are an e-commerce assistant.',
    mcp_servers=[
        'http://localhost:8000/mcp/',  # Product search MCP
        'http://localhost:8001/mcp/'   # Price comparison MCP
    ]
)

result = await client.execute(
    'Find the best gaming laptops under $1500 and compare prices across platforms'
)
```

### Document Generation

```python
client = DeepSeekClient(
    model='deepseek-chat',
    system_prompt='You are a document generation specialist.',
    mcp_servers=[
        {
            'command': 'python',
            'args': ['latex_server.py'],
            'env': {'DOCUMENT_TEMPLATE': 'professional'}
        }
    ]
)

result = await client.execute('''
Generate a technical report on our Q4 performance with:
- Executive summary
- Performance metrics charts
- Recommendations section
Export as PDF format
''')
```

## API Reference

### DeepSeekClient

```python
DeepSeekClient(
    model: str,                          # DeepSeek model name (required)
    system_prompt: str = None,           # System prompt for the model
    mcp_servers: List = None,            # MCP server configurations
    enable_logging: bool = False,        # Enable client logging
    enable_progress: bool = False,       # Enable progress monitoring
    log_level: str = "INFO"             # Logging level
)
```

### ClientResult

```python
@dataclass
class ClientResult:
    output: str                    # Model response
    success: bool                  # Execution status
    execution_id: str             # Unique execution identifier
    timestamp: datetime           # Execution timestamp
    tools_used: List[str]         # List of tools executed
    metadata: Dict[str, Any]      # Execution metadata
    raw_response: Any = None      # Raw model response
    error: str = None             # Error message if failed
```

### MCPServerConfig

```python
@dataclass
class MCPServerConfig:
    # HTTP configuration
    url: str = None
    headers: Dict[str, str] = None
    
    # STDIO configuration  
    command: str = None
    args: List[str] = None
    env: Dict[str, str] = None
    cwd: str = None
    
    # General configuration
    transport_type: str = None    # 'http', 'stdio', 'memory'
    timeout: float = 30.0
    keep_alive: bool = True
```

## Environment Variables

```bash
# Required
DEEPSEEK_API_KEY=your_deepseek_api_key

# Optional
MCP_LOG_LEVEL=INFO
MCP_TIMEOUT=30
```

## Compatible MCP Servers

### Production Servers
- **LaTeX MCP**: Document generation and PDF creation  
- **Database MCP**: SQL database operations and analysis
- **Weather MCP**: Weather data and forecasting
- **Web Search MCP**: Internet search and content retrieval

### Development Servers
- **FastMCP**: In-memory servers for testing and development
- **Local File MCP**: File system operations
- **Calculator MCP**: Mathematical operations

## MCP Servers That Might Interest You

- **[MCP SQL](https://github.com/CarlosMaroRuiz/mcp_sql)**: Advanced SQL database operations with query learning, schema analysis, and performance optimization features