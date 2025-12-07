"""
MCP Server Example: File System and Calculator Server
=====================================================

This is a complete, working example of an MCP server that provides:
1. File system resources (read/list files)
2. Calculator tool (perform calculations)
3. Code analysis prompts (templates for code review)

Requirements:
    pip install mcp anthropic-mcp
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Any, Optional
import logging

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-server")

# =============================================================================
# SERVER SETUP
# =============================================================================

# Create server instance with a name
server = Server("example-filesystem-calculator-server")

# Directory to expose via MCP (change this to your desired directory)
BASE_DIR = Path.home() / "Documents"  # or use Path("/workspace") for this environment


# =============================================================================
# RESOURCES: File System Access
# =============================================================================

@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """
    List all available resources (files) in the base directory.
    
    Resources represent data that AI can read. In this case, we expose
    all text files in the base directory.
    """
    logger.info(f"Listing resources in {BASE_DIR}")
    
    resources = []
    
    try:
        # List all files in base directory
        if BASE_DIR.exists() and BASE_DIR.is_dir():
            for file_path in BASE_DIR.rglob("*"):
                if file_path.is_file():
                    # Only expose text-based files for safety
                    if file_path.suffix in ['.txt', '.md', '.py', '.js', '.json', '.yaml', '.yml']:
                        # Create resource URI
                        uri = f"file://{file_path}"
                        
                        # Determine MIME type
                        mime_type = get_mime_type(file_path.suffix)
                        
                        resources.append(types.Resource(
                            uri=uri,
                            name=file_path.name,
                            description=f"File: {file_path.relative_to(BASE_DIR)}",
                            mimeType=mime_type
                        ))
        
        logger.info(f"Found {len(resources)} resources")
        
    except Exception as e:
        logger.error(f"Error listing resources: {e}")
    
    return resources


@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """
    Read the content of a specific resource.
    
    Args:
        uri: The URI of the resource (e.g., "file:///path/to/file.txt")
    
    Returns:
        The content of the file as a string
    """
    logger.info(f"Reading resource: {uri}")
    
    try:
        # Extract file path from URI
        if uri.startswith("file://"):
            file_path = Path(uri[7:])  # Remove "file://" prefix
            
            # Security check: ensure file is within BASE_DIR
            if not is_safe_path(file_path):
                raise ValueError(f"Access denied: {file_path} is outside allowed directory")
            
            # Read file content
            if file_path.exists() and file_path.is_file():
                content = file_path.read_text(encoding='utf-8')
                logger.info(f"Successfully read {len(content)} characters from {file_path.name}")
                return content
            else:
                raise ValueError(f"File not found: {file_path}")
        else:
            raise ValueError(f"Unsupported URI scheme: {uri}")
    
    except Exception as e:
        logger.error(f"Error reading resource: {e}")
        raise


# =============================================================================
# TOOLS: Calculator and File Operations
# =============================================================================

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List all available tools that the AI can use.
    
    Tools are functions that can perform actions or computations.
    """
    logger.info("Listing available tools")
    
    return [
        types.Tool(
            name="calculate",
            description="Perform mathematical calculations. Supports basic arithmetic (+, -, *, /), exponents (**), and common math functions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The mathematical expression to evaluate (e.g., '2 + 2', '10 ** 2', 'sqrt(16)')"
                    }
                },
                "required": ["expression"]
            }
        ),
        types.Tool(
            name="search_files",
            description="Search for files containing specific text in their content or filename",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Text to search for"
                    },
                    "search_content": {
                        "type": "boolean",
                        "description": "If true, search file contents. If false, only search filenames.",
                        "default": True
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="file_info",
            description="Get detailed information about a file (size, modification time, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file (relative to base directory)"
                    }
                },
                "required": ["path"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str,
    arguments: dict[str, Any]
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Execute a tool with given arguments.
    
    Args:
        name: Name of the tool to execute
        arguments: Dictionary of arguments for the tool
    
    Returns:
        List of content items (text, images, or embedded resources)
    """
    logger.info(f"Calling tool: {name} with arguments: {arguments}")
    
    try:
        if name == "calculate":
            result = await tool_calculate(arguments["expression"])
            return [types.TextContent(
                type="text",
                text=result
            )]
        
        elif name == "search_files":
            results = await tool_search_files(
                arguments["query"],
                arguments.get("search_content", True)
            )
            return [types.TextContent(
                type="text",
                text=results
            )]
        
        elif name == "file_info":
            info = await tool_file_info(arguments["path"])
            return [types.TextContent(
                type="text",
                text=info
            )]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


# =============================================================================
# PROMPTS: Reusable Templates
# =============================================================================

@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    """
    List available prompt templates.
    
    Prompts are reusable templates that can be parameterized.
    """
    logger.info("Listing available prompts")
    
    return [
        types.Prompt(
            name="code_review",
            description="Review code for potential issues, best practices, and improvements",
            arguments=[
                types.PromptArgument(
                    name="code",
                    description="The code to review",
                    required=True
                ),
                types.PromptArgument(
                    name="language",
                    description="Programming language (e.g., 'python', 'javascript')",
                    required=False
                )
            ]
        ),
        types.Prompt(
            name="summarize_file",
            description="Summarize the contents of a file",
            arguments=[
                types.PromptArgument(
                    name="filepath",
                    description="Path to the file to summarize",
                    required=True
                ),
                types.PromptArgument(
                    name="detail_level",
                    description="Level of detail: 'brief', 'moderate', or 'detailed'",
                    required=False
                )
            ]
        )
    ]


@server.get_prompt()
async def handle_get_prompt(
    name: str,
    arguments: dict[str, str] | None
) -> types.GetPromptResult:
    """
    Get a populated prompt template.
    
    Args:
        name: Name of the prompt template
        arguments: Arguments to populate the template
    
    Returns:
        GetPromptResult with populated messages
    """
    logger.info(f"Getting prompt: {name} with arguments: {arguments}")
    
    if not arguments:
        arguments = {}
    
    if name == "code_review":
        code = arguments.get("code", "")
        language = arguments.get("language", "unknown")
        
        return types.GetPromptResult(
            description=f"Code review for {language}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"""Please review the following {language} code for:
1. Potential bugs or errors
2. Code quality and best practices
3. Performance issues
4. Security concerns
5. Suggestions for improvement

Code:
```{language}
{code}
```

Provide a detailed analysis with specific recommendations."""
                    )
                )
            ]
        )
    
    elif name == "summarize_file":
        filepath = arguments.get("filepath", "")
        detail_level = arguments.get("detail_level", "moderate")
        
        # Read file content
        try:
            full_path = BASE_DIR / filepath
            if is_safe_path(full_path):
                content = full_path.read_text(encoding='utf-8')
                
                detail_instructions = {
                    "brief": "Provide a 2-3 sentence summary",
                    "moderate": "Provide a paragraph summary with key points",
                    "detailed": "Provide a comprehensive summary with main topics, key details, and structure"
                }
                
                instruction = detail_instructions.get(detail_level, detail_instructions["moderate"])
                
                return types.GetPromptResult(
                    description=f"Summarize file: {filepath}",
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(
                                type="text",
                                text=f"""{instruction}:

File: {filepath}

Content:
{content}"""
                            )
                        )
                    ]
                )
        except Exception as e:
            logger.error(f"Error reading file for prompt: {e}")
    
    raise ValueError(f"Unknown prompt: {name}")


# =============================================================================
# TOOL IMPLEMENTATIONS
# =============================================================================

async def tool_calculate(expression: str) -> str:
    """
    Evaluate a mathematical expression safely.
    """
    import math
    
    # Create safe namespace with math functions
    safe_namespace = {
        'abs': abs, 'round': round, 'min': min, 'max': max,
        'sum': sum, 'pow': pow,
        'sqrt': math.sqrt, 'sin': math.sin, 'cos': math.cos,
        'tan': math.tan, 'log': math.log, 'log10': math.log10,
        'exp': math.exp, 'pi': math.pi, 'e': math.e
    }
    
    try:
        # Evaluate expression in safe namespace
        result = eval(expression, {"__builtins__": {}}, safe_namespace)
        return f"Result: {result}"
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"


async def tool_search_files(query: str, search_content: bool = True) -> str:
    """
    Search for files by name or content.
    """
    results = []
    
    try:
        if BASE_DIR.exists() and BASE_DIR.is_dir():
            for file_path in BASE_DIR.rglob("*"):
                if file_path.is_file():
                    # Skip non-text files
                    if file_path.suffix not in ['.txt', '.md', '.py', '.js', '.json', '.yaml', '.yml']:
                        continue
                    
                    # Search in filename
                    if query.lower() in file_path.name.lower():
                        results.append(f"📄 {file_path.relative_to(BASE_DIR)} (filename match)")
                        continue
                    
                    # Search in content if requested
                    if search_content:
                        try:
                            content = file_path.read_text(encoding='utf-8')
                            if query.lower() in content.lower():
                                results.append(f"📄 {file_path.relative_to(BASE_DIR)} (content match)")
                        except:
                            pass
        
        if results:
            return f"Found {len(results)} matching files:\n" + "\n".join(results[:20])
        else:
            return f"No files found matching '{query}'"
    
    except Exception as e:
        return f"Error searching files: {str(e)}"


async def tool_file_info(path: str) -> str:
    """
    Get detailed information about a file.
    """
    import datetime
    
    try:
        file_path = BASE_DIR / path
        
        if not is_safe_path(file_path):
            return "Error: Access denied"
        
        if not file_path.exists():
            return f"Error: File not found: {path}"
        
        stat = file_path.stat()
        
        info = f"""File Information: {path}
        
📁 Name: {file_path.name}
📂 Directory: {file_path.parent.relative_to(BASE_DIR)}
📊 Size: {format_size(stat.st_size)}
📅 Modified: {datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}
📅 Created: {datetime.datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')}
🔖 Type: {file_path.suffix or 'no extension'}
"""
        return info
    
    except Exception as e:
        return f"Error getting file info: {str(e)}"


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_mime_type(extension: str) -> str:
    """Get MIME type for file extension"""
    mime_types = {
        '.txt': 'text/plain',
        '.md': 'text/markdown',
        '.py': 'text/x-python',
        '.js': 'text/javascript',
        '.json': 'application/json',
        '.yaml': 'application/x-yaml',
        '.yml': 'application/x-yaml',
        '.html': 'text/html',
        '.css': 'text/css',
    }
    return mime_types.get(extension.lower(), 'text/plain')


def is_safe_path(path: Path) -> bool:
    """
    Check if path is within allowed directory.
    Prevents directory traversal attacks.
    """
    try:
        # Resolve to absolute path
        abs_path = path.resolve()
        abs_base = BASE_DIR.resolve()
        
        # Check if path starts with base directory
        return str(abs_path).startswith(str(abs_base))
    except:
        return False


def format_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


# =============================================================================
# MAIN SERVER ENTRY POINT
# =============================================================================

async def main():
    """Run the MCP server"""
    logger.info(f"Starting MCP server...")
    logger.info(f"Base directory: {BASE_DIR}")
    
    # Run server using stdio transport
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="example-filesystem-calculator-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    # Run the server
    asyncio.run(main())
