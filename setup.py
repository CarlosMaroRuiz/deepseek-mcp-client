from setuptools import setup, find_packages
import os


try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "Cliente para conectar modelos DeepSeek con servidores MCP"

# Leer requirements.txt
try:
    with open("requirements.txt", "r", encoding="utf-8") as f:
        requirements = f.read().splitlines()
except FileNotFoundError:
    requirements = [
        "python-dotenv>=1.0.0",
        "requests>=2.31.0", 
        "mcp>=1.0.0",
        "uvicorn>=0.32.1",
        "openai>=1.67.0",
        "httpx",
        "fastmcp"
    ]

setup(
    name="deepseek-mcp-client",
    version="1.1.0",
    author="Carlos Ruiz",
    author_email="car06ma15@gmail.com",
    description="Cliente para conectar modelos DeepSeek con servidores MCP (Model Context Protocol)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CarlosMaroRuiz/deepseek-mcp-client",
    project_urls={
        "Bug Tracker": "https://github.com/CarlosMaroRuiz/deepseek-mcp-client/issues",
        "Documentation": "https://github.com/CarlosMaroRuiz/deepseek-mcp-client#readme",
        "Source Code": "https://github.com/CarlosMaroRuiz/deepseek-mcp-client",
    },
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",  # ACTUALIZADO
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License", 
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": ["pytest>=6.0", "black>=22.0", "flake8>=4.0", "isort>=5.0"],
        "docs": ["sphinx>=4.0", "sphinx-rtd-theme>=1.0"],
        "test": ["pytest>=6.0", "pytest-asyncio>=0.20", "pytest-cov>=3.0"],
    },
    keywords=[
        "deepseek", "mcp", "client", "ai", "llm", "model context protocol", 
        "tools", "agent", "language model", "fastmcp", "artificial intelligence"
    ],
    zip_safe=False,
)