# Hands-On Exercises: Agentic AI and MCP

This guide contains practical exercises to help you master agentic AI and MCP concepts through hands-on practice.

## Table of Contents
1. [Beginner Exercises](#beginner-exercises)
2. [Intermediate Exercises](#intermediate-exercises)
3. [Advanced Projects](#advanced-projects)
4. [Challenge Projects](#challenge-projects)

---

## Beginner Exercises

### Exercise 1: Build a Simple Tool-Using Agent

**Objective**: Create an agent that can use basic tools to answer questions.

**Requirements**:
- Implement a simple agent loop
- Create 3 tools: calculator, web_search (mock), get_time
- Agent should decide which tool to use based on user query

**Starter Code**:
```python
class SimpleAgent:
    def __init__(self, tools):
        self.tools = tools
    
    def run(self, query):
        # TODO: Implement agent logic
        # 1. Analyze query
        # 2. Select appropriate tool
        # 3. Execute tool
        # 4. Return result
        pass

# Define your tools
def calculator(expression):
    # TODO: Implement
    pass

def web_search(query):
    # TODO: Implement mock search
    pass

def get_time():
    # TODO: Implement
    pass
```

**Test Cases**:
```python
agent = SimpleAgent(tools)
agent.run("What is 25 * 4?")  # Should use calculator
agent.run("What time is it?")  # Should use get_time
agent.run("Latest news about AI")  # Should use web_search
```

**Expected Output**:
- Agent correctly identifies which tool to use
- Tools execute and return results
- Agent formats response appropriately

---

### Exercise 2: Create Your First MCP Server

**Objective**: Build a basic MCP server that exposes a simple tool.

**Requirements**:
- Create an MCP server with one tool
- Tool should perform a useful function (e.g., text analysis)
- Properly implement the MCP protocol

**Tasks**:
1. Set up MCP server boilerplate
2. Implement `list_tools()` handler
3. Implement `call_tool()` handler
4. Create a "text_analyzer" tool that counts words, sentences, characters

**Success Criteria**:
- Server starts without errors
- Tool appears in `list_tools()` response
- Tool executes correctly when called
- Proper error handling

**Test**:
```bash
# Run your server
python my_mcp_server.py

# Test with MCP Inspector or client
```

---

### Exercise 3: Build a Planning Agent

**Objective**: Create an agent that plans before executing.

**Requirements**:
- Agent should break down complex tasks into steps
- Display the plan before execution
- Execute steps in order
- Handle dependencies between steps

**Example Task**: "Create a simple Python web app"

**Expected Plan**:
1. Set up project structure
2. Create requirements.txt
3. Write main application file
4. Create HTML template
5. Test the application

**Implementation Tips**:
- Use a Task dataclass to represent each step
- Track task status (pending, in_progress, completed)
- Check dependencies before executing each task

---

## Intermediate Exercises

### Exercise 4: ReAct Agent with Real APIs

**Objective**: Build a ReAct agent that uses real APIs.

**Requirements**:
- Implement full ReAct loop (Thought, Action, Observation)
- Integrate with at least 2 real APIs (e.g., weather, news)
- Handle API errors gracefully
- Limit iterations to prevent infinite loops

**APIs to Use** (free options):
- Weather: OpenWeatherMap
- News: NewsAPI
- Currency: ExchangeRate-API
- Facts: REST Countries API

**Example Interaction**:
```
User: What's the weather in Tokyo and what's the latest news there?

Thought: I need to get weather for Tokyo
Action: call_weather_api("Tokyo")
Observation: Temperature is 22°C, sunny

Thought: Now I need news about Tokyo
Action: call_news_api("Tokyo")
Observation: [News articles...]

Thought: I have all information
Final Answer: [Complete response with weather and news]
```

---

### Exercise 5: Multi-Resource MCP Server

**Objective**: Create an MCP server with resources, tools, and prompts.

**Requirements**:
- Expose at least 3 different types of resources
- Implement at least 2 tools
- Create at least 1 prompt template
- Implement resource updates/notifications

**Resources to Expose**:
1. Configuration files
2. Log files
3. Database records (mock or real)

**Tools to Implement**:
1. Search resources
2. Aggregate data from multiple resources
3. Generate report

**Prompt to Create**:
- Data analysis prompt that uses the resources

---

### Exercise 6: Agent with Memory

**Objective**: Build an agent that remembers past interactions.

**Requirements**:
- Implement short-term memory (last N interactions)
- Implement long-term memory (persistent storage)
- Use memory to provide context-aware responses
- Allow memory querying

**Features**:
- Store user preferences
- Remember past actions and outcomes
- Retrieve relevant memories for current task
- Summarize old memories to save space

**Test Scenarios**:
```python
agent.run("My favorite color is blue")
agent.run("What's my favorite color?")  # Should remember

agent.run("Calculate 15 * 8")
agent.run("What was the last calculation I did?")  # Should recall
```

---

## Advanced Projects

### Project 1: Code Review Agent

**Objective**: Build a comprehensive code review agent using MCP.

**Components**:
1. **MCP Server**: Exposes code files as resources
2. **Agent**: Analyzes code and provides feedback
3. **Tools**: 
   - Static analysis (pylint, flake8)
   - Complexity metrics
   - Security scanning

**Features**:
- Read code files from repository
- Perform automated checks
- Generate detailed review report
- Suggest improvements
- Track issues across versions

**Deliverables**:
- MCP server for code access
- Agent implementation
- Review report template
- CLI interface

---

### Project 2: Multi-Agent Research System

**Objective**: Create a system where multiple agents collaborate on research tasks.

**Agents**:
1. **Researcher**: Gathers information from multiple sources
2. **Analyzer**: Analyzes gathered data
3. **Synthesizer**: Creates coherent report
4. **Reviewer**: Validates and improves report

**Communication**:
- Agents communicate via message passing
- Each agent has specialized capabilities
- Coordinator orchestrates the workflow

**Use Case**: "Research the current state of renewable energy technology"

**Expected Output**:
- Comprehensive research report
- Citations and sources
- Analysis and insights
- Recommendations

---

### Project 3: Personal Assistant with MCP

**Objective**: Build a personal assistant that uses MCP to access various data sources.

**MCP Servers** (create separate servers):
1. **Calendar Server**: Access to calendar events
2. **Email Server**: Read/send emails (mock or real)
3. **Task Server**: Todo list management
4. **Notes Server**: Personal notes and documents

**Agent Capabilities**:
- Schedule meetings
- Summarize emails
- Manage tasks
- Search notes
- Answer questions about your schedule

**Example Interactions**:
```
"What's on my calendar tomorrow?"
"Summarize unread emails from this week"
"Add a task to review the quarterly report"
"Find my notes about the project meeting"
```

---

### Project 4: Autonomous Debugging Agent

**Objective**: Create an agent that can debug code autonomously.

**Process**:
1. Read code and error messages
2. Form hypotheses about the bug
3. Test hypotheses (run code, check outputs)
4. Propose fixes
5. Validate fixes

**Tools Needed**:
- Code execution sandbox
- File system access
- Testing framework integration
- Version control (git)

**Challenges**:
- Understanding error messages
- Tracing execution flow
- Identifying root causes
- Avoiding breaking changes

---

## Challenge Projects

### Challenge 1: Agentic Code Generator

**Objective**: Build an agent that generates entire applications from descriptions.

**Requirements**:
- Natural language specification
- Generate project structure
- Write code for all components
- Create tests
- Generate documentation
- Make it runnable

**Example**: "Create a REST API for a todo list application with user authentication"

**Agent Should**:
1. Plan the architecture
2. Generate all necessary files
3. Write functional code
4. Create comprehensive tests
5. Generate README and docs
6. Verify the application works

---

### Challenge 2: Multi-Modal MCP Server

**Objective**: Create an MCP server that handles multiple data types.

**Data Types**:
- Text documents
- Images (analyze with vision models)
- Audio files (transcription)
- Video (extract frames, analyze)
- Structured data (CSV, JSON)

**Tools**:
- Multi-modal search
- Cross-reference different types
- Generate summaries
- Extract insights

---

### Challenge 3: Self-Improving Agent

**Objective**: Create an agent that learns and improves from experience.

**Features**:
- Track success/failure of actions
- Adjust strategy based on outcomes
- Store learned patterns
- Self-evaluate performance
- Update its own prompts/instructions

**Metrics**:
- Task success rate
- Time to completion
- Resource efficiency
- User satisfaction

---

### Challenge 4: Distributed Agent System

**Objective**: Build a system where agents run on different machines.

**Architecture**:
- Multiple MCP servers on different hosts
- Agents can discover and use remote servers
- Load balancing and failover
- Secure communication

**Use Case**: Large-scale data processing or research

---

## Exercise Solutions Guide

### Solution Hints

#### Exercise 1 Solution Approach:
```python
def run(self, query):
    # 1. Identify intent
    if any(op in query for op in ['+', '-', '*', '/', 'calculate']):
        return self.tools['calculator'](extract_expression(query))
    elif 'time' in query.lower():
        return self.tools['get_time']()
    else:
        return self.tools['web_search'](query)
```

#### Exercise 2 Key Points:
- Use `@server.list_tools()` decorator
- Return list of `types.Tool` objects
- Tool input schema must be valid JSON Schema
- Return `types.TextContent` from tool execution

#### Exercise 3 Planning Structure:
```python
@dataclass
class Task:
    id: int
    description: str
    dependencies: List[int]
    status: str = "pending"
    
def create_plan(goal: str) -> List[Task]:
    # Use LLM or rule-based approach to generate tasks
    # Ensure proper dependency ordering
    pass
```

---

## Testing Your Solutions

### Unit Testing
```python
import pytest

def test_agent_calculator():
    agent = SimpleAgent(tools)
    result = agent.run("What is 5 + 3?")
    assert "8" in result

def test_mcp_server_tools():
    # Test tool listing
    tools = await server.list_tools()
    assert len(tools) > 0
    
    # Test tool execution
    result = await server.call_tool("my_tool", {"param": "value"})
    assert result is not None
```

### Integration Testing
```python
async def test_mcp_client_server():
    # Start server
    server = start_server()
    
    # Connect client
    client = MCPClient(server)
    await client.connect()
    
    # Test interaction
    result = await client.call_tool("test_tool", {})
    assert result is not None
    
    # Cleanup
    await client.disconnect()
```

---

## Evaluation Rubric

### Agent Quality
- [ ] Handles errors gracefully
- [ ] Makes reasonable decisions
- [ ] Efficient tool usage
- [ ] Clear reasoning process
- [ ] Achieves goals consistently

### Code Quality
- [ ] Well-documented
- [ ] Follows best practices
- [ ] Proper error handling
- [ ] Type hints used
- [ ] Modular design

### MCP Implementation
- [ ] Correct protocol usage
- [ ] Proper resource/tool definitions
- [ ] Security considerations
- [ ] Performance optimization
- [ ] Clear documentation

---

## Resources for Exercises

### Datasets
- Public APIs: https://github.com/public-apis/public-apis
- Sample datasets: Kaggle, UCI ML Repository
- Mock data generators: Faker library

### Tools & Libraries
- MCP SDK: `pip install mcp`
- Testing: `pytest`, `pytest-asyncio`
- HTTP clients: `httpx`, `aiohttp`
- LLM APIs: OpenAI, Anthropic, local models

### Documentation
- MCP Specification: https://modelcontextprotocol.io/
- JSON-RPC 2.0: https://www.jsonrpc.org/specification
- Python asyncio: https://docs.python.org/3/library/asyncio.html

---

## Next Steps

After completing these exercises:

1. **Share Your Work**: Publish your agents and MCP servers on GitHub
2. **Contribute**: Add to the MCP ecosystem with new servers
3. **Experiment**: Try combining multiple patterns
4. **Scale Up**: Build production-ready agentic systems
5. **Teach Others**: Write about your learnings

---

## Getting Help

### Debugging Tips
- Use logging extensively
- Test components in isolation
- Start simple, add complexity gradually
- Review protocol specifications carefully

### Common Issues
- **Connection errors**: Check server is running
- **Tool not found**: Verify tool registration
- **Timeout issues**: Increase timeout limits
- **Memory leaks**: Proper cleanup in async code

### Community Resources
- MCP Discord community
- GitHub Discussions
- Stack Overflow (tag: model-context-protocol)
- Reddit: r/MachineLearning

---

Happy coding! Remember: Start simple, test frequently, and iterate based on results. The best way to learn agentic AI and MCP is by building!
