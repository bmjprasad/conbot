"""
MCP Client Example: Using the File System and Calculator Server
===============================================================

This demonstrates how to build an MCP client that connects to an MCP server
and uses its capabilities (resources, tools, prompts).

Requirements:
    pip install mcp anthropic-mcp
"""

import asyncio
from typing import Optional
import json
import logging

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-client")


# =============================================================================
# MCP CLIENT CLASS
# =============================================================================

class MCPClient:
    """
    A client for interacting with MCP servers.
    
    This client can:
    1. Connect to MCP servers
    2. List available resources, tools, and prompts
    3. Read resources
    4. Call tools
    5. Use prompts
    """
    
    def __init__(self, server_script_path: str):
        """
        Initialize MCP client.
        
        Args:
            server_script_path: Path to the MCP server script
        """
        self.server_params = StdioServerParameters(
            command="python",
            args=[server_script_path],
            env=None
        )
        self.session: Optional[ClientSession] = None
    
    async def connect(self):
        """Establish connection to MCP server"""
        logger.info("Connecting to MCP server...")
        
        # Create stdio connection to server
        self.read, self.write = await stdio_client(self.server_params).__aenter__()
        
        # Create session
        self.session = ClientSession(self.read, self.write)
        await self.session.__aenter__()
        
        # Initialize the connection
        await self.session.initialize()
        
        logger.info("✓ Connected to MCP server")
    
    async def disconnect(self):
        """Close connection to MCP server"""
        if self.session:
            await self.session.__aexit__(None, None, None)
            logger.info("Disconnected from MCP server")
    
    async def list_resources(self):
        """List all available resources"""
        logger.info("\n📚 Listing Resources...")
        
        try:
            response = await self.session.list_resources()
            
            if response.resources:
                print(f"\nFound {len(response.resources)} resources:")
                for resource in response.resources[:10]:  # Show first 10
                    print(f"  📄 {resource.name}")
                    print(f"     URI: {resource.uri}")
                    if resource.description:
                        print(f"     Description: {resource.description}")
                    print()
                
                if len(response.resources) > 10:
                    print(f"  ... and {len(response.resources) - 10} more")
            else:
                print("No resources available")
            
            return response.resources
        
        except Exception as e:
            logger.error(f"Error listing resources: {e}")
            return []
    
    async def read_resource(self, uri: str):
        """
        Read a specific resource.
        
        Args:
            uri: The URI of the resource to read
        """
        logger.info(f"\n📖 Reading Resource: {uri}")
        
        try:
            response = await self.session.read_resource(uri)
            
            if response.contents:
                for content in response.contents:
                    if hasattr(content, 'text'):
                        print(f"\nContent ({len(content.text)} characters):")
                        # Show first 500 characters
                        preview = content.text[:500]
                        print(preview)
                        if len(content.text) > 500:
                            print(f"\n... ({len(content.text) - 500} more characters)")
                    
                    return content.text if hasattr(content, 'text') else str(content)
            else:
                print("No content returned")
                return None
        
        except Exception as e:
            logger.error(f"Error reading resource: {e}")
            return None
    
    async def list_tools(self):
        """List all available tools"""
        logger.info("\n🔧 Listing Tools...")
        
        try:
            response = await self.session.list_tools()
            
            if response.tools:
                print(f"\nFound {len(response.tools)} tools:")
                for tool in response.tools:
                    print(f"\n  🛠️  {tool.name}")
                    print(f"     {tool.description}")
                    
                    # Show input schema
                    if tool.inputSchema:
                        props = tool.inputSchema.get('properties', {})
                        required = tool.inputSchema.get('required', [])
                        
                        if props:
                            print(f"     Parameters:")
                            for param_name, param_info in props.items():
                                req_marker = "required" if param_name in required else "optional"
                                param_desc = param_info.get('description', 'No description')
                                print(f"       - {param_name} ({req_marker}): {param_desc}")
            else:
                print("No tools available")
            
            return response.tools
        
        except Exception as e:
            logger.error(f"Error listing tools: {e}")
            return []
    
    async def call_tool(self, tool_name: str, arguments: dict):
        """
        Call a tool with given arguments.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Dictionary of arguments for the tool
        """
        logger.info(f"\n⚙️  Calling Tool: {tool_name}")
        logger.info(f"Arguments: {json.dumps(arguments, indent=2)}")
        
        try:
            response = await self.session.call_tool(tool_name, arguments)
            
            if response.content:
                print(f"\n✓ Tool Result:")
                for content in response.content:
                    if hasattr(content, 'text'):
                        print(content.text)
                    else:
                        print(str(content))
                
                return response.content
            else:
                print("No result returned")
                return None
        
        except Exception as e:
            logger.error(f"Error calling tool: {e}")
            return None
    
    async def list_prompts(self):
        """List all available prompts"""
        logger.info("\n💬 Listing Prompts...")
        
        try:
            response = await self.session.list_prompts()
            
            if response.prompts:
                print(f"\nFound {len(response.prompts)} prompts:")
                for prompt in response.prompts:
                    print(f"\n  📝 {prompt.name}")
                    print(f"     {prompt.description}")
                    
                    if prompt.arguments:
                        print(f"     Arguments:")
                        for arg in prompt.arguments:
                            req_marker = "required" if arg.required else "optional"
                            print(f"       - {arg.name} ({req_marker}): {arg.description}")
            else:
                print("No prompts available")
            
            return response.prompts
        
        except Exception as e:
            logger.error(f"Error listing prompts: {e}")
            return []
    
    async def get_prompt(self, prompt_name: str, arguments: dict = None):
        """
        Get a populated prompt.
        
        Args:
            prompt_name: Name of the prompt
            arguments: Arguments to populate the prompt
        """
        logger.info(f"\n📋 Getting Prompt: {prompt_name}")
        if arguments:
            logger.info(f"Arguments: {json.dumps(arguments, indent=2)}")
        
        try:
            response = await self.session.get_prompt(prompt_name, arguments or {})
            
            print(f"\n✓ Prompt: {response.description}")
            if response.messages:
                for msg in response.messages:
                    print(f"\nRole: {msg.role}")
                    if hasattr(msg.content, 'text'):
                        print(f"Content:\n{msg.content.text}")
                    else:
                        print(f"Content: {msg.content}")
            
            return response
        
        except Exception as e:
            logger.error(f"Error getting prompt: {e}")
            return None


# =============================================================================
# EXAMPLE USAGE SCENARIOS
# =============================================================================

async def scenario_1_explore_server(client: MCPClient):
    """Scenario 1: Explore what the server offers"""
    print("\n" + "="*60)
    print("SCENARIO 1: Explore Server Capabilities")
    print("="*60)
    
    # List all capabilities
    await client.list_resources()
    await client.list_tools()
    await client.list_prompts()


async def scenario_2_use_calculator(client: MCPClient):
    """Scenario 2: Use the calculator tool"""
    print("\n" + "="*60)
    print("SCENARIO 2: Use Calculator Tool")
    print("="*60)
    
    # Perform some calculations
    calculations = [
        {"expression": "2 + 2"},
        {"expression": "10 ** 2"},
        {"expression": "sqrt(144)"},
        {"expression": "sin(pi / 2)"}
    ]
    
    for calc in calculations:
        await client.call_tool("calculate", calc)
        await asyncio.sleep(0.5)  # Small delay for readability


async def scenario_3_search_and_read_files(client: MCPClient):
    """Scenario 3: Search for files and read them"""
    print("\n" + "="*60)
    print("SCENARIO 3: Search and Read Files")
    print("="*60)
    
    # Search for Python files
    await client.call_tool("search_files", {
        "query": "python",
        "search_content": False  # Search only filenames
    })
    
    # List resources to find a specific file
    resources = await client.list_resources()
    
    # Read the first resource if available
    if resources:
        first_resource = resources[0]
        await client.read_resource(first_resource.uri)


async def scenario_4_use_prompts(client: MCPClient):
    """Scenario 4: Use prompt templates"""
    print("\n" + "="*60)
    print("SCENARIO 4: Use Prompt Templates")
    print("="*60)
    
    # Use code review prompt
    sample_code = """
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total = total + num
    return total / len(numbers)
"""
    
    await client.get_prompt("code_review", {
        "code": sample_code,
        "language": "python"
    })


async def scenario_5_file_info(client: MCPClient):
    """Scenario 5: Get file information"""
    print("\n" + "="*60)
    print("SCENARIO 5: Get File Information")
    print("="*60)
    
    # Get info about a specific file
    await client.call_tool("file_info", {
        "path": "example.txt"  # Change to an actual file in your base directory
    })


async def scenario_6_agentic_workflow(client: MCPClient):
    """
    Scenario 6: Simulate an agentic workflow
    
    This demonstrates how an AI agent might use MCP:
    1. List available tools
    2. Decide which tools to use
    3. Execute tools in sequence
    4. Process results
    """
    print("\n" + "="*60)
    print("SCENARIO 6: Agentic Workflow")
    print("="*60)
    
    print("\n🤖 Agent Task: 'Calculate the square root of 256 and then search for related files'")
    
    # Step 1: Agent lists available tools
    print("\n[Agent] Listing available tools to understand capabilities...")
    tools = await client.list_tools()
    
    # Step 2: Agent performs calculation
    print("\n[Agent] Using calculator tool to find square root of 256...")
    calc_result = await client.call_tool("calculate", {"expression": "sqrt(256)"})
    
    # Step 3: Agent searches files
    print("\n[Agent] Searching for files related to calculations...")
    search_result = await client.call_tool("search_files", {
        "query": "calculate",
        "search_content": True
    })
    
    # Step 4: Agent reports completion
    print("\n[Agent] ✓ Task completed! I calculated sqrt(256) = 16 and found related files.")


# =============================================================================
# MAIN DEMO
# =============================================================================

async def main():
    """Run all client examples"""
    
    print("\n" + "="*60)
    print("MCP CLIENT DEMO")
    print("="*60)
    print("\nThis demo shows how to use an MCP client to interact with")
    print("an MCP server that provides file system access and calculator tools.")
    print("\nNOTE: Make sure the MCP server script path is correct!")
    print("="*60)
    
    # Initialize client
    # IMPORTANT: Update this path to point to your actual server script
    server_script = "04-mcp-server-example.py"
    client = MCPClient(server_script)
    
    try:
        # Connect to server
        await client.connect()
        
        # Run scenarios
        await scenario_1_explore_server(client)
        await asyncio.sleep(1)
        
        await scenario_2_use_calculator(client)
        await asyncio.sleep(1)
        
        # Note: Scenarios 3, 4, 5 may fail if files don't exist
        # Uncomment to try them:
        # await scenario_3_search_and_read_files(client)
        # await asyncio.sleep(1)
        
        # await scenario_4_use_prompts(client)
        # await asyncio.sleep(1)
        
        # await scenario_5_file_info(client)
        # await asyncio.sleep(1)
        
        await scenario_6_agentic_workflow(client)
        
        print("\n" + "="*60)
        print("DEMO COMPLETE!")
        print("="*60)
    
    except Exception as e:
        logger.error(f"Error in demo: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Disconnect
        await client.disconnect()


# =============================================================================
# INTEGRATION WITH AI AGENT
# =============================================================================

class AgenticMCPClient:
    """
    An MCP client designed for use by AI agents.
    
    This wraps the MCP client with higher-level methods that
    an AI agent can easily use to accomplish tasks.
    """
    
    def __init__(self, server_script_path: str):
        self.client = MCPClient(server_script_path)
        self.connected = False
    
    async def initialize(self):
        """Initialize connection to MCP server"""
        await self.client.connect()
        self.connected = True
    
    async def shutdown(self):
        """Shutdown connection"""
        await self.client.disconnect()
        self.connected = False
    
    async def discover_capabilities(self) -> dict:
        """
        Discover what the MCP server can do.
        
        Returns:
            Dictionary with lists of resources, tools, and prompts
        """
        resources = await self.client.list_resources()
        tools = await self.client.list_tools()
        prompts = await self.client.list_prompts()
        
        return {
            "resources": resources,
            "tools": tools,
            "prompts": prompts
        }
    
    async def execute_action(self, action_type: str, **kwargs):
        """
        Execute an action on the MCP server.
        
        Args:
            action_type: Type of action ('read_resource', 'call_tool', 'get_prompt')
            **kwargs: Arguments for the action
        """
        if action_type == "read_resource":
            return await self.client.read_resource(kwargs["uri"])
        
        elif action_type == "call_tool":
            return await self.client.call_tool(
                kwargs["tool_name"],
                kwargs["arguments"]
            )
        
        elif action_type == "get_prompt":
            return await self.client.get_prompt(
                kwargs["prompt_name"],
                kwargs.get("arguments")
            )
        
        else:
            raise ValueError(f"Unknown action type: {action_type}")


async def demo_agentic_mcp():
    """
    Demonstrate how an AI agent would use MCP.
    
    This shows the integration between agentic AI patterns
    and MCP for accessing external tools and data.
    """
    print("\n" + "="*60)
    print("AGENTIC AI + MCP INTEGRATION DEMO")
    print("="*60)
    
    # Initialize agentic MCP client
    agentic_client = AgenticMCPClient("04-mcp-server-example.py")
    
    try:
        await agentic_client.initialize()
        
        # Agent discovers capabilities
        print("\n🤖 [Agent] Discovering server capabilities...")
        capabilities = await agentic_client.discover_capabilities()
        
        print(f"\n[Agent] Found:")
        print(f"  - {len(capabilities['resources'])} resources")
        print(f"  - {len(capabilities['tools'])} tools")
        print(f"  - {len(capabilities['prompts'])} prompts")
        
        # Agent decides to use calculator
        print("\n🤖 [Agent] I'll use the calculator tool to solve a problem...")
        result = await agentic_client.execute_action(
            "call_tool",
            tool_name="calculate",
            arguments={"expression": "2 ** 10"}
        )
        
        print(f"\n[Agent] Calculation complete!")
        
        # Agent could continue with more actions based on results...
        print("\n✓ Agentic MCP integration successful!")
    
    finally:
        await agentic_client.shutdown()


if __name__ == "__main__":
    # Run the main demo
    asyncio.run(main())
    
    # Uncomment to run agentic demo:
    # asyncio.run(demo_agentic_mcp())
