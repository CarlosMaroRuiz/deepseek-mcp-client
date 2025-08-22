# verify_structure.py - Ejecuta este archivo primero
import os

def verify_structure():
    """Verificar que la estructura de archivos sea correcta"""
    print("🔍 Verificando estructura de archivos...")
    
    # Estructura requerida
    required_files = {
        "deepseek_mcp_client/__init__.py": "Main package init",
        "deepseek_mcp_client/models/__init__.py": "Models package init", 
        "deepseek_mcp_client/models/client_result.py": "ClientResult class",
        "deepseek_mcp_client/models/server_config.py": "MCPServerConfig class",
        "deepseek_mcp_client/handlers/__init__.py": "Handlers package init",
        "deepseek_mcp_client/handlers/message_handler.py": "DeepSeekMessageHandler class",
        "deepseek_mcp_client/client/__init__.py": "Client package init",
        "deepseek_mcp_client/client/deepseek_client.py": "DeepSeekClient class",
        "deepseek_mcp_client/utils/__init__.py": "Utils package init",
        "deepseek_mcp_client/utils/logging_config.py": "Logging utilities"
    }
    
    missing_files = []
    existing_files = []
    
    for file_path, description in required_files.items():
        if os.path.exists(file_path):
            existing_files.append((file_path, description))
            print(f"✅ {file_path}")
        else:
            missing_files.append((file_path, description))
            print(f"❌ {file_path} - MISSING")
    
    print(f"\n📊 Results:")
    print(f"✅ Existing: {len(existing_files)}")
    print(f"❌ Missing: {len(missing_files)}")
    
    if missing_files:
        print(f"\n🚨 Missing files that need to be created:")
        for file_path, description in missing_files:
            print(f"   - {file_path} ({description})")
        return False
    else:
        print(f"\n🎉 All files exist! Structure is correct.")
        return True

def check_imports():
    """Verificar que los imports funcionen"""
    print(f"\n🔍 Testing imports...")
    
    try:
        # Test individual imports
        from deepseek_mcp_client.models.client_result import ClientResult
        print("✅ ClientResult import works")
        
        from deepseek_mcp_client.models.server_config import MCPServerConfig  
        print("✅ MCPServerConfig import works")
        
        from deepseek_mcp_client.handlers.message_handler import DeepSeekMessageHandler
        print("✅ DeepSeekMessageHandler import works")
        
        from deepseek_mcp_client.client.deepseek_client import DeepSeekClient
        print("✅ DeepSeekClient import works")
        
        # Test main imports
        from deepseek_mcp_client import DeepSeekClient, ClientResult, MCPServerConfig
        print("✅ Main package imports work")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 STRUCTURE AND IMPORT VERIFICATION")
    print("=" * 50)
    
    structure_ok = verify_structure()
    if structure_ok:
        imports_ok = check_imports()
        if imports_ok:
            print("\n🎉 EVERYTHING IS WORKING!")
            print("Your refactored structure is correct.")
        else:
            print("\n🚨 IMPORTS FAILING!")
            print("Files exist but imports don't work.")
    else:
        print("\n🚨 STRUCTURE INCOMPLETE!")
        print("You need to create the missing files.")
    
    print("\nNext steps:")
    if not structure_ok:
        print("1. Create the missing files listed above")
        print("2. Run this script again")
    elif not imports_ok:
        print("1. Check the content of the files")
        print("2. Ensure __init__.py files have correct exports")
    else:
        print("1. Test your main code!")
        print("2. Everything should work now")