import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from deepseek_mcp_client import DeepSeekClient, MCPServerConfig


class TestDeepSeekClient:
    
    def test_basic_initialization(self, monkeypatch):
        """Test que el cliente se inicializa correctamente con parámetros mínimos"""
        # Configurar variable de entorno
        monkeypatch.setenv("DEEPSEEK_API_KEY", "test_api_key")
        
        with patch("deepseek_mcp_client.client.deepseek_client.OpenAI") as mock_openai:
            # Configurar mock
            mock_openai_instance = MagicMock()
            mock_openai.return_value = mock_openai_instance
            
            # Crear cliente con parámetros mínimos
            client = DeepSeekClient(model="deepseek-chat")
            
            # Verificaciones
            assert client.model == "deepseek-chat"
            assert client.system_prompt == "You are a helpful and friendly assistant."
            assert client.mcp_servers == []
            assert client.enable_logging == False
            assert client.enable_progress == False
            
            # Verificar inicialización de OpenAI
            mock_openai.assert_called_once_with(
                api_key="test_api_key",
                base_url="https://api.deepseek.com"
            )
    
    def test_initialization_with_all_parameters(self, monkeypatch):
        """Test inicialización con todos los parámetros"""
        monkeypatch.setenv("DEEPSEEK_API_KEY", "test_api_key")
        
        with patch("deepseek_mcp_client.client.deepseek_client.OpenAI"):
            client = DeepSeekClient(
                model="deepseek-chat",
                system_prompt="Custom prompt",
                mcp_servers=["http://localhost:8000/mcp/"],
                enable_logging=True,
                enable_progress=True,
                log_level="DEBUG"
            )
            
            assert client.model == "deepseek-chat"
            assert client.system_prompt == "Custom prompt"
            assert len(client.mcp_servers) == 1
            assert client.enable_logging == True
            assert client.enable_progress == True
    
    def test_parse_server_config_http(self, monkeypatch):
        """Test que las URLs HTTP se parsean correctamente"""
        monkeypatch.setenv("DEEPSEEK_API_KEY", "test_api_key")
        
        with patch("deepseek_mcp_client.client.deepseek_client.OpenAI"):
            client = DeepSeekClient(model="deepseek-chat")
            config = client._parse_server_config("http://localhost:8000/mcp/")
            
            assert config.url == "http://localhost:8000/mcp/"
            assert config.transport_type == "http"
    
    def test_parse_server_config_dict(self, monkeypatch):
        """Test que los diccionarios se parsean correctamente"""
        monkeypatch.setenv("DEEPSEEK_API_KEY", "test_api_key")
        
        with patch("deepseek_mcp_client.client.deepseek_client.OpenAI"):
            client = DeepSeekClient(model="deepseek-chat")
            config = client._parse_server_config({
                'url': 'http://localhost:8000/mcp/',
                'headers': {'X-Test': 'test'},
                'timeout': 30.0
            })
            
            assert config.url == "http://localhost:8000/mcp/"
            assert config.headers == {'X-Test': 'test'}
            assert config.timeout == 30.0
            assert config.transport_type == "http"
    
    def test_parse_server_config_stdio(self, monkeypatch):
        """Test que las configuraciones STDIO se parsean correctamente"""
        monkeypatch.setenv("DEEPSEEK_API_KEY", "test_api_key")
        
        with patch("deepseek_mcp_client.client.deepseek_client.OpenAI"):
            client = DeepSeekClient(model="deepseek-chat")
            config = client._parse_server_config({
                'command': 'python',
                'args': ['server.py'],
                'env': {'TEST': 'value'}
            })
            
            assert config.command == "python"
            assert config.args == ['server.py']
            assert config.env == {'TEST': 'value'}
            assert config.transport_type == "stdio"
    
    def test_parse_server_config_invalid(self, monkeypatch):
        """Test que configuraciones inválidas lanzan excepciones"""
        monkeypatch.setenv("DEEPSEEK_API_KEY", "test_api_key")
        
        with patch("deepseek_mcp_client.client.deepseek_client.OpenAI"):
            client = DeepSeekClient(model="deepseek-chat")
            
            with pytest.raises(ValueError):
                client._parse_server_config(123)  # Tipo inválido
    
    @pytest.mark.asyncio
    async def test_execute_direct_mode(self, monkeypatch):
        """Test ejecución en modo directo sin MCP"""
        monkeypatch.setenv("DEEPSEEK_API_KEY", "test_api_key")
        
        # Create mock OpenAI response
        mock_message = MagicMock()
        mock_message.content = "Test response"
        mock_message.tool_calls = []
        
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        
        # Patch the _execute_initial_call method directly
        with patch.object(DeepSeekClient, '_execute_initial_call') as mock_execute:
            # Use AsyncMock to return a value directly
            mock_execute.return_value = mock_response
            
            # Create client and execute
            client = DeepSeekClient(model="deepseek-chat")
            result = await client.execute("Test query")
            
            # Verify results
            assert result.success == True
            assert result.output == "Test response"
            assert len(result.tools_used) == 0
    
    @pytest.mark.asyncio
    async def test_execute_with_tools(self, monkeypatch):
        """Test ejecución con herramientas MCP"""
        monkeypatch.setenv("DEEPSEEK_API_KEY", "test_api_key")
        
        # Create initial response with tool calls
        initial_tool_call = MagicMock()
        initial_tool_call.id = "tool123"
        initial_tool_call.function.name = "test_tool"
        initial_tool_call.function.arguments = '{"param": "test_value"}'
        
        initial_message = MagicMock()
        initial_message.content = "Calling tool"
        initial_message.tool_calls = [initial_tool_call]
        
        initial_choice = MagicMock()
        initial_choice.message = initial_message
        
        initial_response = MagicMock()
        initial_response.choices = [initial_choice]
        
        # Create final response
        final_message = MagicMock()
        final_message.content = "Tool executed successfully"
        final_message.tool_calls = []
        
        final_choice = MagicMock()
        final_choice.message = final_message
        
        final_response = MagicMock()
        final_response.choices = [final_choice]
        
        # Patch the initial call to return our initial response
        with patch.object(DeepSeekClient, '_execute_initial_call') as mock_initial:
            mock_initial.return_value = initial_response
            
            # Patch _execute_tool to avoid real API calls
            with patch.object(DeepSeekClient, '_execute_tool') as mock_tool:
                mock_tool.return_value = "Tool result"
                
                # Patch the final OpenAI call
                with patch.object(DeepSeekClient, '_execute_tools_and_get_final_response') as mock_final:
                    mock_final.return_value = final_response
                    
                    # Create client with test configuration
                    client = DeepSeekClient(model="deepseek-chat")
                    client._connected = True
                    client.all_tools = [{
                        "type": "function", 
                        "function": {
                            "name": "test_tool",
                            "description": "Test tool", 
                            "parameters": {"type": "object", "properties": {}}
                        }
                    }]
                    client.tool_to_client = {"test_tool": MagicMock()}
                    
                    # Execute
                    result = await client.execute("Test query with tools")
                    
                    # Verify
                    assert result.success == True
                    assert result.output == "Tool executed successfully"
    
    @pytest.mark.asyncio
    async def test_connect_mcp_servers(self, monkeypatch):
        """Test conexión a servidores MCP"""
        monkeypatch.setenv("DEEPSEEK_API_KEY", "test_api_key")
        
        with patch("deepseek_mcp_client.client.deepseek_client.OpenAI"):
            # Create a mock client
            mock_client = MagicMock()
            
            # Mock the _create_client method
            with patch.object(DeepSeekClient, '_create_client') as mock_create:
                mock_create.return_value = mock_client
                
                # Mock _connect_single_server to directly add the client
                with patch.object(DeepSeekClient, '_connect_single_server') as mock_connect:
                    async def fake_connect(index, config):
                        # Add the mock client to the clients list
                        client.clients.append(mock_client)
                    
                    mock_connect.side_effect = fake_connect
                    
                    # Mock _load_tools_from_client to do nothing
                    with patch.object(DeepSeekClient, '_load_tools_from_client') as mock_load:
                        mock_load.return_value = None
                        
                        # Create client with test configuration
                        client = DeepSeekClient(
                            model="deepseek-chat",
                            mcp_servers=["http://localhost:8000/mcp/"]
                        )
                        
                        # Reset state
                        client.all_tools = []
                        client.clients = []
                        client.tool_to_client = {}
                        client._connected = False
                        
                        # Execute
                        await client._connect_mcp_servers()
                        
                        # Verify
                        assert client._connected == True
                        assert len(client.clients) == 1
    
    @pytest.mark.asyncio
    async def test_connect_error_handling(self, monkeypatch):
        monkeypatch.setenv("DEEPSEEK_API_KEY", "test_api_key")
        with patch("deepseek_mcp_client.client.deepseek_client.OpenAI"):
            with patch.object(DeepSeekClient, '_parse_server_config') as mock_parse:
                mock_config = MCPServerConfig(url='http://test', transport_type='http')
                mock_parse.return_value = mock_config
            
                with patch.object(DeepSeekClient, '_create_client') as mock_create:
                    mock_create.side_effect = Exception("Connection error")
                
                
                    client = DeepSeekClient(
                    model="deepseek-chat",
                    mcp_servers=["http://localhost:8000/mcp/"]
                    )
                
               
                    client.clients = []
                    client._connected = False
                
                    await client._connect_mcp_servers()
                
        
                    assert client._connected == True
                    assert len(client.clients) == 0
                
               
                    mock_create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_tool(self, monkeypatch):
        """Test ejecución de herramienta individual"""
        monkeypatch.setenv("DEEPSEEK_API_KEY", "test_api_key")
        
        with patch("deepseek_mcp_client.client.deepseek_client.OpenAI"):
            # Create a mock client with AsyncMock for context manager methods
            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            
            # Mock the call_tool method to return a fixed result
            mock_client.call_tool = AsyncMock(return_value="Tool result")
            
            # Create client with the mock
            client = DeepSeekClient(model="deepseek-chat")
            client.tool_to_client = {"test_tool": mock_client}
            
            # Execute
            result = await client._execute_tool("test_tool", {"param": "value"})
            
            # Verify
            assert result == "Tool result"
    
    @pytest.mark.asyncio
    async def test_execute_tool_error(self, monkeypatch):
        """Test manejo de errores en ejecución de herramienta"""
        monkeypatch.setenv("DEEPSEEK_API_KEY", "test_api_key")
        
        with patch("deepseek_mcp_client.client.deepseek_client.OpenAI"):
            # Create a mock client with AsyncMock for context manager methods
            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            
            # Mock the call_tool method to raise an exception
            mock_client.call_tool = AsyncMock(side_effect=Exception("Tool error"))
            
            # Create client with the mock
            client = DeepSeekClient(model="deepseek-chat")
            client.tool_to_client = {"test_tool": mock_client}
            
            # Execute
            result = await client._execute_tool("test_tool", {"param": "value"})
            
            # Verify
            assert "Error" in result
            assert "Tool error" in result
    
    @pytest.mark.asyncio
    async def test_close(self, monkeypatch):
        """Test cierre de conexiones"""
        monkeypatch.setenv("DEEPSEEK_API_KEY", "test_api_key")
        
        with patch("deepseek_mcp_client.client.deepseek_client.OpenAI"):
            # Create client
            client = DeepSeekClient(model="deepseek-chat")
            
            # Add mock clients
            mock_client1 = MagicMock()
            mock_client2 = MagicMock()
            client.clients = [mock_client1, mock_client2]
            client._connected = True
            
            # Close connections
            await client.close()
            
            # Verify
            assert client._connected == False
            assert len(client.clients) == 0
    
    def test_get_available_tools(self, monkeypatch):
        """Test get_available_tools"""
        monkeypatch.setenv("DEEPSEEK_API_KEY", "test_api_key")
        
        with patch("deepseek_mcp_client.client.deepseek_client.OpenAI"):
            # Create client
            client = DeepSeekClient(model="deepseek-chat")
            
            # Add tools
            client.all_tools = [
                {"function": {"name": "tool1"}},
                {"function": {"name": "tool2"}}
            ]
            
            # Verify
            tools = client.get_available_tools()
            assert len(tools) == 2
            assert "tool1" in tools
            assert "tool2" in tools
    
    def test_get_stats(self, monkeypatch):
        """Test get_stats"""
        monkeypatch.setenv("DEEPSEEK_API_KEY", "test_api_key")
        
        with patch("deepseek_mcp_client.client.deepseek_client.OpenAI"):
            # Create client
            client = DeepSeekClient(model="deepseek-chat")
            
            # Configure state
            client.mcp_servers = ["http://server1", "http://server2"]
            client.clients = [MagicMock()]
            client.all_tools = [{"function": {"name": "tool1"}}]
            client._connected = True
            
            # Verify
            stats = client.get_stats()
            assert stats["servers_configured"] == 2
            assert stats["servers_connected"] == 1
            assert stats["tools_available"] == 1
            assert stats["is_connected"] == True