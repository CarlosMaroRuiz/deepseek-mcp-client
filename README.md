<!-- Logo/Banner Header -->
<div align="center">
  <h1>
    DeepSeek MCP Client
  </h1>
  
  <p><em>Conecta modelos DeepSeek con servidores MCP (Model Context Protocol)</em></p>

  <!-- Version Badge -->
  <p>
    <img src="https://img.shields.io/badge/version-1.0.0-blue?style=for-the-badge" alt="Version"/>
  </p>
  
  <br/>
  
  <p align="center">
    <a href="#introducción">Introducción</a> •
    <a href="#requisitos-previos">Requisitos</a> •
    <a href="#instalación">Instalación</a> •
    <a href="#configuración">Configuración</a> •
    <a href="#uso-básico">Uso</a> •
    <a href="#ejemplos-prácticos">Ejemplos</a>
  </p>
</div>

<hr/>

## 📋 Introducción

<div align="center">
  <table>
    <tr>
      <td>
        <b>deepseek-mcp-client</b> es una biblioteca Python que permite integrar los modelos DeepSeek con servidores MCP (Model Context Protocol). Esta integración facilita el acceso a herramientas externas desde modelos DeepSeek, ampliando sus capacidades con búsquedas web, análisis de datos y otras funcionalidades disponibles a través de servidores MCP.
      </td>
    </tr>
  </table>
</div>

## 🔍 Requisitos Previos

<div style="background-color: #f6f8fa; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
  <ul>
    <li>🐍 Python 3.8 o superior</li>
    <li>🔑 API key de DeepSeek</li>
    <li>🖥️ Uno o más servidores MCP operativos</li>
  </ul>
</div>

## 💾 Instalación

```bash
# Clonar el repositorio
git clone https://github.com/CarlosMaroRuiz/deepseek-mcp-client.git
cd deepseek-mcp-client

# Instalar dependencias
pip install -r requirements.txt
```

## ⚙️ Configuración

<div style="display: flex; gap: 20px; margin-bottom: 20px;">
  <div style="flex: 1; background-color: #f6f8fa; padding: 15px; border-radius: 5px;">
    <h3>1. Configurar Credenciales de API</h3>
    <p>Cree un archivo <code>.env</code> en la raíz del proyecto basado en el archivo <code>example.env</code>:</p>
    
```bash
cp example.env .env
```

<p>Edite el archivo <code>.env</code> para agregar su API key de DeepSeek:</p>

```
DEEPSEEK_API_KEY=su_api_key_aquí
```
  </div>
</div>

## 🚀 Uso Básico

### Ejemplo Mínimo

<div style="background-color: #f6f8fa; padding: 15px; border-radius: 5px; margin-bottom: 20px;">

```python
from deepseek_mcp_client import DeepSeekClient
import asyncio

# Crear cliente DeepSeek con acceso a MCP
agent = DeepSeekClient(
    model='deepseek-chat',
    system_prompt='Eres un asistente especializado en e-commerce.',
    mcp_servers=['http://localhost:8000/mcp/']
)

# Ejecutar consulta
async def main():
    result = await agent.execute('Busca laptops gamer económicas calidad precio')
    print(result.output)

if __name__ == "__main__":
    asyncio.run(main())
```
</div>

### Estructura del Resultado

<details open>
<summary><strong>Propiedades del objeto ClientResult</strong></summary>
<table>
  <tr>
    <th>Propiedad</th>
    <th>Descripción</th>
  </tr>
  <tr>
    <td><code>output</code></td>
    <td>Texto de respuesta generado por el modelo</td>
  </tr>
  <tr>
    <td><code>success</code></td>
    <td>Booleano que indica si la ejecución fue exitosa</td>
  </tr>
  <tr>
    <td><code>execution_id</code></td>
    <td>Identificador único de la ejecución</td>
  </tr>
  <tr>
    <td><code>timestamp</code></td>
    <td>Fecha y hora de inicio de la ejecución</td>
  </tr>
  <tr>
    <td><code>tools_used</code></td>
    <td>Lista de nombres de herramientas utilizadas</td>
  </tr>
  <tr>
    <td><code>metadata</code></td>
    <td>Diccionario con metadatos adicionales</td>
  </tr>
  <tr>
    <td><code>raw_response</code></td>
    <td>Respuesta completa sin procesar del modelo</td>
  </tr>
  <tr>
    <td><code>error</code></td>
    <td>Mensaje de error (si ocurrió alguno)</td>
  </tr>
</table>
</details>

Ejemplo de procesamiento del resultado:

```python
async def main():
    result = await agent.execute('Busca laptops gamer económicas calidad precio')
    
    if result.success:
        print(f"Respuesta: {result.output}")
        print(f"Herramientas utilizadas: {', '.join(result.tools_used)}")
        print(f"Tiempo de ejecución: {result.metadata.get('duration')} segundos")
    else:
        print(f"Error: {result.error}")

asyncio.run(main())
```

## 🔧 Configuración Avanzada

<div style="display: flex; flex-wrap: wrap; gap: 20px; margin-bottom: 20px;">
  <div style="flex: 1; min-width: 300px; background-color: #f6f8fa; padding: 15px; border-radius: 5px;">
    <h3>🔌 Conexión a Múltiples Servidores MCP</h3>
    <p>Puede conectar su cliente a varios servidores MCP simultáneamente para acceder a diversas herramientas:</p>
    
```python
agent = DeepSeekClient(
    model='deepseek-chat',
    system_prompt='Eres un asistente con acceso a múltiples fuentes de información.',
    mcp_servers=[
        'http://localhost:8000/mcp/',  # Servidor de búsqueda
        'http://localhost:8001/mcp/',  # Servidor de análisis de datos
        'http://localhost:8002/mcp/'   # Servidor de bases de datos
    ]
)
```
  </div>
  
  <div style="flex: 1; min-width: 300px; background-color: #f6f8fa; padding: 15px; border-radius: 5px;">
    <h3>💬 Personalización del Prompt del Sistema</h3>
    <p>El <code>system_prompt</code> define el comportamiento general del modelo. Puede personalizarlo según sus necesidades específicas:</p>
    
```python
agent = DeepSeekClient(
    model='deepseek-chat',
    system_prompt='''Eres un asistente especializado en investigación académica.
    Siempre citas tus fuentes y proporcionas información rigurosa y basada en evidencia.
    Cuando no estás seguro de algo, lo indicas claramente y explicas las limitaciones de tu conocimiento.''',
    mcp_servers=['http://localhost:8000/mcp/']
)
```
  </div>
</div>

## 📚 Ejemplos Prácticos

<div style="display: flex; flex-wrap: wrap; gap: 20px; margin-bottom: 20px;">
  <div style="flex: 1; min-width: 300px; background-color: #f6f8fa; padding: 15px; border-radius: 5px;">
    <h3>🛒 Asistente de Compras</h3>
    
```python
agent = DeepSeekClient(
    model='deepseek-chat',
    system_prompt='Eres un asistente de compras especializado en tecnología.',
    mcp_servers=['http://localhost:8000/mcp/']  # Servidor con herramientas de búsqueda
)

async def buscar_productos():
    queries = [
        'Encuentra las mejores laptops gaming por menos de $1000',
        'Compara los últimos smartphones de gama media',
        'Recomienda audífonos inalámbricos con cancelación de ruido'
    ]
    
    for query in queries:
        print(f"\n--- Consulta: {query} ---")
        result = await agent.execute(query)
        print(result.output)

asyncio.run(buscar_productos())
```
  </div>
  
  <div style="flex: 1; min-width: 300px; background-color: #f6f8fa; padding: 15px; border-radius: 5px;">
    <h3>📊 Analista de Datos</h3>
    
```python
agent = DeepSeekClient(
    model='deepseek-chat',
    system_prompt='Eres un analista de datos que proporciona insights claros y accionables.',
    mcp_servers=['http://localhost:8001/mcp/']  # Servidor con herramientas analíticas
)

async def analizar_tendencias():
    result = await agent.execute(
        'Analiza las tendencias de ventas del último trimestre y proporciona recomendaciones'
    )
    print(result.output)

asyncio.run(analizar_tendencias())
```
  </div>
</div>

---

<div align="center">
  <p>
    <a href="https://github.com/CarlosMaroRuiz/deepseek-mcp-client">
      <img src="https://img.shields.io/badge/GitHub-Repository-24292e.svg?style=for-the-badge&logo=github" alt="GitHub Repository"/>
    </a>
  </p>
  <br/>
  <p>
    <small>© 2025 Carlos Maro Ruiz. Todos los derechos reservados.</small>
  </p>
</div>
