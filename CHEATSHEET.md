# Agentic AI & MCP Cheat Sheet

Quick reference guide for building agentic AI systems and working with MCP.

---

## 🤖 Agentic AI Patterns

### ReAct (Reasoning + Acting)
```python
while not done:
    thought = agent.think(context)      # Reason about next action
    action = agent.decide(thought)       # Choose action
    observation = agent.act(action)      # Execute action
    context = update(observation)        # Update context
    done = agent.is_complete(context)    # Check if done
```

**When to use**: Tasks requiring step-by-step reasoning and tool use.

### Planning
```python
plan = agent.create_plan(goal)          # Create task list
for task in plan:
    if dependencies_met(task):
        result = execute(task)
        mark_complete(task)
```

**When to use**: Complex tasks with clear subtasks and dependencies.

### Reflection
```python
response = agent.generate(task)
while iterations < max_iterations:
    critique = agent.reflect(response)
    if satisfactory(critique):
        break
    response = agent.improve(response, critique)
```

**When to use**: Tasks requiring quality iteration and self-improvement.

### Multi-Agent
```python
agents = [researcher, planner, executor, reviewer]
for agent in agents:
    result = agent.process(previous_result)
    pass_to_next_agent(result)
```

**When to use**: Complex tasks benefiting from specialized expertise.

---

## 🔧 Tool Definition Template

```python
def my_tool(param1: str, param2: int) -> str:
    """
    Clear description of what the tool does.
    
    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2
    
    Returns:
        Description of return value
    """
    # Implementation
    result = do_something(param1, param2)
    return result
```

**Best Practices**:
- Single responsibility
- Clear documentation
- Type hints
- Error handling
- Predictable behavior

---

## 📡 MCP Quick Reference

### MCP Server Structure

```python
from mcp.server import Server
import mcp.types as types

server = Server("my-server")

# List resources
@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    return [types.Resource(
        uri="resource://unique-id",
        name="Display Name",
        mimeType="text/plain",
        description="What this resource contains"
    )]

# Read resource
@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    return get_resource_content(uri)

# List tools
@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [types.Tool(
        name="tool_name",
        description="What the tool does",
        inputSchema={
            "type": "object",
            "properties": {
                "param": {"type": "string"}
            },
            "required": ["param"]
        }
    )]

# Call tool
@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    result = execute_tool(name, arguments)
    return [types.TextContent(type="text", text=result)]
```

### MCP Client Structure

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Configure server
server_params = StdioServerParameters(
    command="python",
    args=["server.py"]
)

# Connect and use
async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        # Initialize
        await session.initialize()
        
        # List resources
        resources = await session.list_resources()
        
        # Read resource
        content = await session.read_resource(uri)
        
        # List tools
        tools = await session.list_tools()
        
        # Call tool
        result = await session.call_tool(name, arguments)
```

---

## 🎯 Common Patterns

### Agent Loop with Error Handling
```python
def agent_loop(goal: str, max_iterations: int = 10):
    iteration = 0
    context = {"goal": goal, "history": []}
    
    while iteration < max_iterations:
        try:
            # Think
            thought = llm.think(context)
            context["history"].append({"type": "thought", "content": thought})
            
            # Check completion
            if is_goal_achieved(thought, context):
                return generate_response(context)
            
            # Act
            action = llm.decide_action(thought)
            result = execute_action(action)
            context["history"].append({"type": "action", "content": result})
            
            iteration += 1
            
        except Exception as e:
            handle_error(e, context)
            
    return generate_partial_response(context)
```

### Resource Caching
```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedResourceServer:
    def __init__(self):
        self.cache = {}
        self.cache_duration = timedelta(minutes=5)
    
    async def get_resource(self, uri: str) -> str:
        if uri in self.cache:
            cached_time, content = self.cache[uri]
            if datetime.now() - cached_time < self.cache_duration:
                return content
        
        # Fetch fresh content
        content = await fetch_resource(uri)
        self.cache[uri] = (datetime.now(), content)
        return content
```

### Tool Retry Logic
```python
import asyncio

async def call_tool_with_retry(
    tool_name: str,
    arguments: dict,
    max_retries: int = 3,
    backoff: float = 1.0
):
    for attempt in range(max_retries):
        try:
            return await call_tool(tool_name, arguments)
        except TransientError as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(backoff * (2 ** attempt))
        except FatalError:
            raise
```

---

## 🔐 Security Checklist

### For Tools
- [ ] Input validation (type, range, format)
- [ ] Path traversal prevention
- [ ] SQL injection prevention
- [ ] Rate limiting
- [ ] Permission checks
- [ ] Audit logging

### For MCP Servers
- [ ] URI validation
- [ ] Sandboxed execution
- [ ] Resource access control
- [ ] Secure credential handling
- [ ] Request size limits
- [ ] Timeout enforcement

### For Agents
- [ ] Goal validation
- [ ] Action approval for critical operations
- [ ] Budget limits (tokens, API calls)
- [ ] Scope restrictions
- [ ] Output sanitization
- [ ] Privacy protection

---

## 📊 Testing Templates

### Unit Test for Tool
```python
import pytest

def test_calculator_tool():
    result = calculator("2 + 2")
    assert "4" in result

def test_calculator_error_handling():
    result = calculator("invalid")
    assert "error" in result.lower()
```

### Integration Test for MCP
```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_mcp_server_tools():
    # Setup
    server = create_test_server()
    
    # Test tool listing
    tools = await server.list_tools()
    assert len(tools) > 0
    assert tools[0].name == "expected_tool"
    
    # Test tool execution
    result = await server.call_tool("expected_tool", {"param": "value"})
    assert result is not None
```

### Test Agent Behavior
```python
def test_agent_goal_achievement():
    agent = SimpleAgent(mock_tools)
    result = agent.run("Calculate 2 + 2")
    assert agent.goal_achieved
    assert "4" in result
```

---

## 🎨 Prompt Templates

### Tool Selection Prompt
```
Given the following tools and task, select the most appropriate tool:

Tools:
{tool_list}

Task: {task_description}

Which tool should be used? Respond with just the tool name.
```

### ReAct Prompt
```
You are an autonomous agent. Follow this format:

Thought: Reason about what to do next
Action: tool_name(arguments)
Observation: [Tool output will be inserted here]
... (repeat as needed)
Thought: I now know the final answer
Final Answer: [Your response]

Task: {task}
```

### Planning Prompt
```
Break down this task into concrete, actionable steps:

Task: {task}

Provide a numbered list of steps with clear completion criteria.
Identify dependencies between steps.
```

---

## 🚀 Performance Tips

### Reduce Latency
- Use streaming for LLM responses
- Batch multiple tool calls when possible
- Cache frequently accessed resources
- Parallelize independent operations

### Optimize Tokens
- Compress conversation history
- Summarize older context
- Remove redundant information
- Use shorter, clearer prompts

### Scale Efficiently
- Connection pooling for databases
- Rate limiting to prevent abuse
- Async/await throughout
- Lazy loading of resources

---

## 🐛 Debugging Checklist

### Agent Not Working?
- [ ] Check tool definitions (correct schema?)
- [ ] Verify tool execution (returns expected format?)
- [ ] Review agent prompts (clear instructions?)
- [ ] Check max iterations (hitting limit?)
- [ ] Examine error logs (what's failing?)

### MCP Connection Issues?
- [ ] Server running? (check process)
- [ ] Correct server path? (verify in config)
- [ ] Protocol version match? (client and server)
- [ ] Logs showing errors? (check stderr)
- [ ] Timeout too short? (increase if needed)

### Tool Execution Failures?
- [ ] Valid arguments? (check schema)
- [ ] Permission issues? (file/network access)
- [ ] Timeout exceeded? (long-running operation)
- [ ] Dependencies missing? (imports working?)
- [ ] Error handling? (try-except blocks)

---

## 📚 Quick Commands

### Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install mcp httpx aiohttp

# Run examples
python 03-agentic-ai-examples.py
```

### MCP Testing
```bash
# Start server
python mcp-server.py

# Test with client (in another terminal)
python mcp-client.py

# Test with MCP Inspector
npx @modelcontextprotocol/inspector python mcp-server.py
```

### Common Git Commands
```bash
# Save your work
git add .
git commit -m "Add agent implementation"
git push

# Check status
git status
git log --oneline
```

---

## 🔗 Essential Links

- **MCP Spec**: https://modelcontextprotocol.io/
- **MCP GitHub**: https://github.com/modelcontextprotocol
- **Python MCP SDK**: https://pypi.org/project/mcp/
- **Claude API**: https://docs.anthropic.com/
- **OpenAI API**: https://platform.openai.com/docs

---

## 💡 Pro Tips

1. **Start Simple**: Build basic agent before adding complexity
2. **Test Incrementally**: Test each component separately
3. **Log Everything**: Comprehensive logging saves debugging time
4. **Use Type Hints**: Catches errors early, improves IDE support
5. **Handle Errors**: Graceful degradation > crashing
6. **Document Well**: Future you will thank present you
7. **Security First**: Validate inputs, limit permissions
8. **Iterate Fast**: Quick prototypes > perfect first attempts

---

**Remember**: The best agent is one that works reliably and safely. Focus on fundamentals before optimizing!

---

*Keep this handy while building your agentic AI systems!* 🚀
