# 🚀 DeepSeek MCP Client - Versión Mejorada

<div align="center">
  <p><em>Cliente para conectar modelos DeepSeek con servidores MCP</em></p>
  <p><strong>Soporte completo para STDIO, HTTP, in-memory, message handlers y progress monitoring</strong></p>
  
  <img src="https://img.shields.io/badge/version-2.0.0-blue?style=for-the-badge" alt="Version"/>
  <img src="https://img.shields.io/badge/transport-HTTP%20%7C%20STDIO%20%7C%20Memory-green?style=for-the-badge" alt="Transport"/>
  <img src="https://img.shields.io/badge/monitoring-Progress%20%7C%20Logging-orange?style=for-the-badge" alt="Monitoring"/>
  <img src="https://img.shields.io/badge/install-PyPI-yellow?style=for-the-badge" alt="PyPI"/>
</div>

---

## 📚 Tabla de Contenidos

- [📦 Instalación](#-instalación)
- [⚙️ Configuración](#️-configuración)
- [🚀 Ejemplos de Uso](#-uso---ejemplos-completos)
- [📊 Monitoreo](#-monitoreo-y-logging)
- [🛠️ Casos Avanzados](#️-casos-de-uso-avanzados)
- [🛡️ Manejo de Errores](#️-manejo-de-errores-y-recuperación)
- [🔧 Troubleshooting](#-troubleshooting)
- [🏗️ Arquitectura](#️-arquitectura)

---

## Características

### 🔌 **Soporte Completo de Transporte**
- **HTTP/HTTPS**: Para servidores remotos y en producción
- **STDIO**: Para servidores locales con control completo del entorno
- **In-Memory**: Para testing y desarrollo rápido
- **Configuración Mixta**: Combina múltiples tipos de transporte

### 📊 **Monitoreo Avanzado**
- **Progress Monitoring**: Seguimiento en tiempo real de operaciones largas
- **Message Handlers**: Manejo automático de notificaciones del servidor
- **Logging Integrado**: Sistema de logs estructurado con niveles configurables
- **Cache Inteligente**: Actualización automática cuando cambian las herramientas

### ⚙️ **Configuración Flexible**
- **Auto-detección**: Identifica automáticamente el tipo de transporte
- **Variables de Entorno**: Manejo seguro de credenciales y configuración
- **Timeout Personalizable**: Control fino sobre timeouts de conexión
- **Manejo de Errores**: Recuperación robusta ante fallos

---

## 📦 Instalación

### **Instalación desde PyPI (Recomendado)**

```bash
# Instalación directa desde PyPI
pip install deepseek-mcp-client

# O con todas las dependencias opcionales
pip install deepseek-mcp-client[full]
```

### **Instalación desde código fuente**

```bash
# Solo si necesitas la versión de desarrollo
git clone https://github.com/CarlosMaroRuiz/deepseek-mcp-client.git
cd deepseek-mcp-client
pip install -e .
```

### **Verificar instalación**

```python
from deepseek_mcp_client import DeepSeekClient
print("✅ DeepSeek MCP Client instalado correctamente")
```

---

## ⚙️ Configuración

### **1. Configurar API Key**

```bash
# Opción 1: Variable de entorno
export DEEPSEEK_API_KEY="tu_api_key_aquí"

# Opción 2: Archivo .env
echo "DEEPSEEK_API_KEY=tu_api_key_aquí" > .env
```

### **2. Verificar configuración**

```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
if api_key:
    print("✅ API Key configurada correctamente")
else:
    print("❌ API Key no encontrada")
```

---

## 🚀 Uso - Ejemplos Completos

### 1. 🌐 **Configuración HTTP Simple**

```python
from deepseek_mcp_client import DeepSeekClient
import asyncio

# Servidores HTTP remotos
agent = DeepSeekClient(
    model='deepseek-chat',
    system_prompt='Eres un asistente especializado en e-commerce.',
    mcp_servers=[
        'http://localhost:8000/mcp/',  # MercadoLibre MCP
        'http://localhost:8001/mcp/'   # LaTeX MCP
    ],
    enable_logging=True,
    enable_progress=True
)

async def main():
    result = await agent.execute('Busca laptops gaming económicas')
    print(f"Resultado: {result.output}")
    print(f"Herramientas usadas: {result.tools_used}")
    print(f"Duración: {result.metadata.get('duration'):.2f}s")
    await agent.close()

asyncio.run(main())
```

### 2. 💻 **Configuración STDIO (Servidores Locales)**

```python
# Servidores locales con variables de entorno
agent = DeepSeekClient(
    model='deepseek-chat',
    system_prompt='Eres un asistente con herramientas locales.',
    mcp_servers=[
        {
            'command': 'python',
            'args': ['mercadolibre_server.py'],
            'env': {
                'LOG_LEVEL': 'DEBUG',
                'API_TIMEOUT': '30'
            },
            'cwd': './servers/',
            'keep_alive': True
        },
        {
            'command': 'node',
            'args': ['weather_server.js', '--port', '3000'],
            'env': {
                'WEATHER_API_KEY': 'tu_api_key_aquí'
            }
        }
    ],
    enable_logging=True,
    log_level="DEBUG"
)
```

### 3. 🔀 **Configuración Mixta (Múltiples Transportes)**

```python
from fastmcp import FastMCP

# Crear servidor en memoria para testing
test_server = FastMCP("Calculator")

@test_server.tool
def calculate(expression: str) -> str:
    """Calculadora simple"""
    try:
        # En producción, usar ast.literal_eval o similar
        result = eval(expression)
        return f"Resultado: {result}"
    except Exception as e:
        return f"Error: {str(e)}"

# Cliente con múltiples tipos de transporte
agent = DeepSeekClient(
    model='deepseek-chat',
    system_prompt='Asistente con múltiples herramientas.',
    mcp_servers=[
        'http://localhost:8000/mcp/',     # HTTP: Servidor remoto
        {                                 # STDIO: Servidor local
            'command': 'python',
            'args': ['local_server.py'],
            'env': {'DEBUG': 'true'}
        },
        test_server                       # In-Memory: Calculadora
    ]
)
```

### 4. ⚙️ **Configuración Avanzada con MCPServerConfig**

```python
from deepseek_mcp_client import MCPServerConfig

# Configuración detallada para servidor HTTP
mercadolibre_config = MCPServerConfig(
    url='http://localhost:8000/mcp/',
    headers={
        'Authorization': 'Bearer tu-token-aqui',
        'X-Client-Version': '1.0.0'
    },
    transport_type='http',
    timeout=45.0
)

# Configuración detallada para servidor STDIO
analyzer_config = MCPServerConfig(
    command='python',
    args=['data_analyzer.py', '--mode', 'production'],
    env={
        'DATABASE_URL': 'postgresql://...',
        'LOG_LEVEL': 'INFO'
    },
    cwd='./analytics/',
    keep_alive=True,
    timeout=60.0
)

agent = DeepSeekClient(
    model='deepseek-chat',
    system_prompt='Analista de datos especializado.',
    mcp_servers=[mercadolibre_config, analyzer_config],
    enable_logging=True,
    enable_progress=True
)
```

---

## 📊 **Monitoreo y Logging**

### **Progress Monitoring en Tiempo Real**

```python
# El cliente automáticamente muestra progreso de operaciones largas
agent = DeepSeekClient(
    model='deepseek-chat',
    system_prompt='Asistente con operaciones largas.',
    mcp_servers=['http://localhost:8000/mcp/'],
    enable_progress=True,  # Habilitar monitoreo de progreso
    enable_logging=True,   # Habilitar logging detallado
    log_level="INFO"       # Nivel de logging
)

# Durante la ejecución verás logs como:
# 📊 Progreso: 25.0% - Procesando datos...
# 🔧 tool_name: 50.0% - Analizando resultados...
# 📊 Progreso: 100.0% - Completado
```

### **Message Handlers Automáticos**

```python
# El cliente automáticamente maneja:
# - Cambios en listas de herramientas
# - Actualizaciones de recursos
# - Notificaciones de progreso
# - Mensajes de log del servidor

# Logs automáticos:
# 🔄 Lista de herramientas actualizada
# 🔄 Lista de recursos actualizada
# 🔄 Refrescando cache de herramientas...
```

---

## 🛠️ **Casos de Uso Avanzados**

### **1. E-commerce con Análisis Local**

```python
agent = DeepSeekClient(
    model='deepseek-chat',
    system_prompt='Analista de e-commerce con herramientas web y locales.',
    mcp_servers=[
        'http://localhost:8000/mcp/',  # Búsqueda en MercadoLibre
        {                              # Análisis de datos local
            'command': 'python',
            'args': ['analytics_server.py'],
            'env': {'DATABASE_URL': 'sqlite:///products.db'}
        }
    ]
)

result = await agent.execute('''
Busca las 10 laptops más vendidas en MercadoLibre,
analiza sus precios históricamente en mi base de datos local,
y genera un reporte de tendencias.
''')
```

### **2. Generación de Documentos Científicos**

```python
agent = DeepSeekClient(
    model='deepseek-chat',
    system_prompt='Asistente para investigación científica.',
    mcp_servers=[
        'http://localhost:8001/mcp/',  # LaTeX MCP
        {                              # Procesador de datos científicos
            'command': 'python',
            'args': ['scientific_processor.py'],
            'env': {
                'PYTHON_PATH': './scientific_libs/',
                'MATPLOTLIB_BACKEND': 'Agg'
            }
        }
    ]
)

result = await agent.execute('''
Analiza los datos del archivo experimental.csv,
genera gráficos estadísticos,
y crea un paper en LaTeX con los resultados.
''')
```

### **3. Sistema de Trading Automatizado**

```python
import os

trading_config = MCPServerConfig(
    command='python',
    args=['trading_server.py', '--mode', 'live'],
    env={
        'BROKER_API_KEY': os.environ.get('BROKER_API_KEY'),
        'RISK_LEVEL': 'conservative',
        'MAX_POSITION_SIZE': '1000'
    },
    timeout=30.0
)

agent = DeepSeekClient(
    model='deepseek-chat',
    system_prompt='Asistente de trading con gestión de riesgo.',
    mcp_servers=[
        'http://localhost:8002/mcp/',  # Datos de mercado
        trading_config                 # Servidor de trading local seguro
    ]
)
```

---

## 🛡️ **Manejo de Errores y Recuperación**

```python
async def ejemplo_robusto():
    agent = DeepSeekClient(
        model='deepseek-chat',
        system_prompt='Asistente resiliente.',
        mcp_servers=[
            'http://localhost:8000/mcp/',      # Servidor que funciona
            'http://localhost:9999/mcp/',      # Servidor inexistente
            {'command': 'python', 'args': ['bad_server.py']}  # Archivo inexistente
        ]
    )
    
    try:
        result = await agent.execute('Hola')
        
        if result.success:
            print(f"✅ Respuesta: {result.output}")
            print(f"🔧 Servidores conectados: {result.metadata.get('servers_connected')}")
        else:
            print(f"❌ Error: {result.error}")
    
    except Exception as e:
        print(f"💥 Error crítico: {e}")
    
    finally:
        await agent.close()  # Limpieza automática

# Ejecutar ejemplo
asyncio.run(ejemplo_robusto())
```

---

## 📈 **Análisis de Rendimiento**

```python
# Metadata detallada en cada resultado
result = await agent.execute('Tu consulta')

print(f"Duración total: {result.metadata.get('duration'):.2f}s")
print(f"Herramientas ejecutadas: {result.metadata.get('tools_executed')}")
print(f"Servidores conectados: {result.metadata.get('servers_connected')}")
print(f"Tipos de transporte: {result.metadata.get('transport_types')}")
print(f"ID de ejecución: {result.execution_id}")
```

---

## 🔧 Troubleshooting

### **Problemas Comunes**

#### ❌ **Error: "DEEPSEEK_API_KEY no configurada"**
```bash
# Verificar variable de entorno
echo $DEEPSEEK_API_KEY

# Configurar temporalmente
export DEEPSEEK_API_KEY="tu_api_key_aquí"

# Configurar permanentemente en .env
echo "DEEPSEEK_API_KEY=tu_api_key_aquí" >> .env
```

#### ❌ **Error de conexión STDIO**
```python
# Verificar que el servidor existe y es ejecutable
import os
import stat

server_path = "mi_servidor.py"
if os.path.exists(server_path):
    print("✅ Archivo existe")
    if os.access(server_path, os.X_OK):
        print("✅ Archivo ejecutable")
    else:
        print("❌ Sin permisos de ejecución")
        # Dar permisos: chmod +x mi_servidor.py
else:
    print("❌ Archivo no encontrado")
```

#### ⏱️ **Timeouts en operaciones largas**
```python
# Configurar timeouts más largos
config = MCPServerConfig(
    url='http://localhost:8000/mcp/',
    timeout=120.0  # 2 minutos
)

# O sin timeout (usar con cuidado)
config = MCPServerConfig(
    command='python',
    args=['slow_server.py'],
    timeout=None  # Sin límite de tiempo
)
```

#### 🔄 **Problemas de cache de herramientas**
```python
# Forzar actualización del cache
await agent.refresh_tools()

# O reinicializar el cliente
await agent.close()
agent = DeepSeekClient(...)  # Recrear cliente
```

#### 🌐 **Problemas de conectividad HTTP**
```python
# Verificar conectividad
import httpx

async def test_connection():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8000/mcp/")
            print(f"✅ Servidor responde: {response.status_code}")
        except Exception as e:
            print(f"❌ Error de conexión: {e}")

asyncio.run(test_connection())
```

---

## 🏗️ **Arquitectura**

```
Usuario → DeepSeek API → MCP Client → [HTTP/STDIO/Memory] → MCP Servers
                           ↓                                      ↓
                    Message Handlers ←─────── Notifications ←─────┘
                           ↓
                    Progress Monitor ←─────── Progress Updates
                           ↓
                    Tool Execution ──────────→ Results
                           ↓
                    Formatted Response → Usuario
```

### **Componentes principales:**
- **DeepSeekClient**: Orquestador principal y interfaz de usuario
- **Transport Layer**: Adaptadores para HTTP/STDIO/Memory
- **Message Handlers**: Procesamiento automático de notificaciones
- **Progress Monitor**: Seguimiento en tiempo real de operaciones
- **Cache Manager**: Optimización y sincronización de herramientas

---

## 🔧 **Servidores MCP Compatibles**

### **Servidores de Producción**
- **[MercadoLibre MCP](https://github.com/CarlosMaroRuiz/MCP_MERCADOLIBRE)**: Búsqueda y análisis de productos
- **[LaTeX MCP](https://github.com/CarlosMaroRuiz/MCP_LATEX_BASIC)**: Generación de documentos PDF
- **Brave Search MCP**: Búsqueda web con API de Brave
- **Weather MCP**: Datos meteorológicos
- **Database MCP**: Conexión a bases de datos

### **Servidores de Desarrollo**
- **FastMCP Test Servers**: Servidores en memoria para testing
- **Local File MCP**: Procesamiento de archivos locales
- **Calculator MCP**: Operaciones matemáticas básicas

### **Crear tu propio servidor**
```python
# Ejemplo básico con FastMCP
from fastmcp import FastMCP

server = FastMCP("MyCustomServer")

@server.tool
def my_tool(param: str) -> str:
    """Herramienta personalizada"""
    return f"Procesado: {param}"

# Usar en cliente
agent = DeepSeekClient(
    model='deepseek-chat',
    system_prompt='Asistente con herramientas personalizadas.',
    mcp_servers=[server]  # Servidor in-memory
)
```

---

<div align="center">
  <p><strong>⭐ Si te gusta este proyecto, dale una estrella en GitHub ⭐</strong></p>

</div>