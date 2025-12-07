"""
Agentic AI: Practical Code Examples
====================================

This file contains practical implementations of various agentic AI patterns.
Each example demonstrates core concepts with working code.
"""

import json
import time
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


# =============================================================================
# EXAMPLE 1: Simple ReAct Agent
# =============================================================================

class ActionType(Enum):
    THINK = "think"
    ACT = "act"
    OBSERVE = "observe"
    FINISH = "finish"


@dataclass
class AgentAction:
    """Represents a single agent action in the ReAct loop"""
    type: ActionType
    content: str
    tool: Optional[str] = None
    tool_input: Optional[Dict[str, Any]] = None


class SimpleReActAgent:
    """
    A simple ReAct (Reasoning + Acting) agent implementation.
    
    The agent follows this loop:
    1. Think: Reason about what to do next
    2. Act: Execute a tool/action
    3. Observe: Process the result
    4. Repeat until goal is achieved
    """
    
    def __init__(self, tools: Dict[str, Callable]):
        self.tools = tools
        self.history: List[AgentAction] = []
        self.max_iterations = 10
    
    def run(self, goal: str) -> str:
        """Execute the agent loop to achieve the goal"""
        print(f"\n{'='*60}")
        print(f"GOAL: {goal}")
        print(f"{'='*60}\n")
        
        iteration = 0
        current_context = goal
        
        while iteration < self.max_iterations:
            iteration += 1
            print(f"\n--- Iteration {iteration} ---")
            
            # 1. THINK: Decide what to do
            thought = self._think(current_context)
            self.history.append(AgentAction(ActionType.THINK, thought))
            print(f"💭 Thought: {thought}")
            
            # Check if we're done
            if "goal achieved" in thought.lower() or "finished" in thought.lower():
                print(f"\n✅ Goal achieved!")
                break
            
            # 2. ACT: Execute an action
            action = self._decide_action(thought)
            self.history.append(action)
            
            if action.type == ActionType.FINISH:
                print(f"🏁 Finishing: {action.content}")
                break
            
            print(f"🔧 Action: Use tool '{action.tool}' with input: {action.tool_input}")
            
            # 3. OBSERVE: Get result from tool
            observation = self._execute_tool(action.tool, action.tool_input)
            self.history.append(AgentAction(ActionType.OBSERVE, observation))
            print(f"👁️  Observation: {observation}")
            
            # Update context for next iteration
            current_context = f"Goal: {goal}\nLast thought: {thought}\nLast observation: {observation}"
        
        # Generate final response
        final_response = self._generate_final_response()
        return final_response
    
    def _think(self, context: str) -> str:
        """Simulate LLM reasoning about next step"""
        # In a real implementation, this would call an LLM
        # For demonstration, we use simple heuristics
        
        if "weather" in context.lower():
            return "I need to search for weather information"
        elif "calculate" in context.lower():
            return "I need to perform a calculation"
        elif "search" in self.history[-1].content if self.history else False:
            return "I have the information I need. Goal achieved."
        else:
            return "I should search for the requested information"
    
    def _decide_action(self, thought: str) -> AgentAction:
        """Decide which tool to use based on thought"""
        if "weather" in thought.lower():
            return AgentAction(
                type=ActionType.ACT,
                content="Search for weather",
                tool="web_search",
                tool_input={"query": "current weather"}
            )
        elif "calculate" in thought.lower():
            return AgentAction(
                type=ActionType.ACT,
                content="Perform calculation",
                tool="calculator",
                tool_input={"expression": "2+2"}
            )
        elif "search" in thought.lower():
            return AgentAction(
                type=ActionType.ACT,
                content="Perform web search",
                tool="web_search",
                tool_input={"query": "information"}
            )
        else:
            return AgentAction(
                type=ActionType.FINISH,
                content="Task completed based on available information"
            )
    
    def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """Execute a tool and return the result"""
        if tool_name in self.tools:
            return self.tools[tool_name](**tool_input)
        else:
            return f"Error: Tool '{tool_name}' not found"
    
    def _generate_final_response(self) -> str:
        """Generate final response based on agent history"""
        observations = [a.content for a in self.history if a.type == ActionType.OBSERVE]
        if observations:
            return f"Based on my investigation: {observations[-1]}"
        return "Task completed"


# =============================================================================
# EXAMPLE 2: Planning Agent
# =============================================================================

@dataclass
class Task:
    """Represents a task in a plan"""
    id: int
    description: str
    status: str = "pending"  # pending, in_progress, completed, failed
    dependencies: List[int] = field(default_factory=list)
    result: Optional[str] = None


class PlanningAgent:
    """
    An agent that creates a plan before execution.
    
    Steps:
    1. Analyze the goal
    2. Create a plan (list of tasks with dependencies)
    3. Execute tasks in order
    4. Handle failures and adapt
    """
    
    def __init__(self, tools: Dict[str, Callable]):
        self.tools = tools
        self.plan: List[Task] = []
    
    def run(self, goal: str) -> str:
        """Execute planned approach to achieve goal"""
        print(f"\n{'='*60}")
        print(f"PLANNING AGENT - GOAL: {goal}")
        print(f"{'='*60}\n")
        
        # Step 1: Create plan
        self._create_plan(goal)
        self._display_plan()
        
        # Step 2: Execute plan
        result = self._execute_plan()
        
        return result
    
    def _create_plan(self, goal: str):
        """Create a plan to achieve the goal"""
        # In a real implementation, an LLM would generate this plan
        # For demonstration, we create a simple plan based on the goal
        
        if "build" in goal.lower() and "app" in goal.lower():
            self.plan = [
                Task(1, "Research requirements", dependencies=[]),
                Task(2, "Design architecture", dependencies=[1]),
                Task(3, "Implement backend", dependencies=[2]),
                Task(4, "Implement frontend", dependencies=[2]),
                Task(5, "Write tests", dependencies=[3, 4]),
                Task(6, "Deploy application", dependencies=[5])
            ]
        elif "research" in goal.lower():
            self.plan = [
                Task(1, "Identify information sources", dependencies=[]),
                Task(2, "Gather information", dependencies=[1]),
                Task(3, "Analyze findings", dependencies=[2]),
                Task(4, "Synthesize report", dependencies=[3])
            ]
        else:
            self.plan = [
                Task(1, "Understand requirements", dependencies=[]),
                Task(2, "Execute main task", dependencies=[1]),
                Task(3, "Verify results", dependencies=[2])
            ]
    
    def _display_plan(self):
        """Display the plan"""
        print("📋 PLAN:")
        for task in self.plan:
            deps = f"(depends on: {task.dependencies})" if task.dependencies else ""
            print(f"  {task.id}. {task.description} {deps}")
        print()
    
    def _execute_plan(self) -> str:
        """Execute the plan task by task"""
        print("🚀 EXECUTING PLAN:\n")
        
        while any(task.status == "pending" for task in self.plan):
            # Find next executable task (all dependencies completed)
            next_task = self._get_next_task()
            
            if next_task is None:
                print("❌ No more executable tasks. Checking for blockers...")
                break
            
            # Execute task
            self._execute_task(next_task)
        
        # Check if all tasks completed
        completed = all(task.status == "completed" for task in self.plan)
        
        if completed:
            return "✅ All tasks completed successfully!"
        else:
            failed = [t for t in self.plan if t.status == "failed"]
            return f"⚠️  Plan partially completed. {len(failed)} tasks failed."
    
    def _get_next_task(self) -> Optional[Task]:
        """Get the next task that can be executed"""
        for task in self.plan:
            if task.status != "pending":
                continue
            
            # Check if all dependencies are completed
            deps_completed = all(
                self.plan[dep_id - 1].status == "completed"
                for dep_id in task.dependencies
            )
            
            if deps_completed:
                return task
        
        return None
    
    def _execute_task(self, task: Task):
        """Execute a single task"""
        print(f"▶️  Executing Task {task.id}: {task.description}")
        task.status = "in_progress"
        
        # Simulate task execution
        time.sleep(0.5)
        
        # In a real implementation, this would use tools and LLM
        # For demo, we simulate success
        task.status = "completed"
        task.result = f"Completed: {task.description}"
        print(f"   ✓ Task {task.id} completed\n")


# =============================================================================
# EXAMPLE 3: Reflection Agent
# =============================================================================

class ReflectionAgent:
    """
    An agent that reflects on and improves its outputs.
    
    Process:
    1. Generate initial response
    2. Reflect on response quality
    3. Identify improvements
    4. Generate improved response
    5. Repeat until satisfied
    """
    
    def __init__(self, max_reflections: int = 3):
        self.max_reflections = max_reflections
        self.iterations: List[Dict[str, str]] = []
    
    def run(self, task: str) -> str:
        """Execute task with reflection"""
        print(f"\n{'='*60}")
        print(f"REFLECTION AGENT - TASK: {task}")
        print(f"{'='*60}\n")
        
        current_response = self._generate_initial_response(task)
        
        for i in range(self.max_reflections):
            print(f"\n--- Reflection Iteration {i + 1} ---\n")
            
            # Display current response
            print(f"📝 Current Response:\n{current_response}\n")
            
            # Reflect on response
            reflection = self._reflect(task, current_response)
            print(f"🤔 Reflection:\n{reflection}\n")
            
            # Check if satisfied
            if "satisfied" in reflection.lower() or "no improvements" in reflection.lower():
                print("✅ Satisfied with response!")
                break
            
            # Generate improved response
            current_response = self._improve(task, current_response, reflection)
            
            self.iterations.append({
                "iteration": i + 1,
                "response": current_response,
                "reflection": reflection
            })
        
        return current_response
    
    def _generate_initial_response(self, task: str) -> str:
        """Generate initial response to the task"""
        # Simulate a basic response
        return f"This is a basic response to: {task}. It addresses the main point."
    
    def _reflect(self, task: str, response: str) -> str:
        """Reflect on the quality of the response"""
        # In a real implementation, this would use an LLM to critique the response
        # For demo, we simulate reflection
        
        if len(self.iterations) == 0:
            return "The response is too brief. It should include more detail and examples."
        elif len(self.iterations) == 1:
            return "Better, but could be more structured. Consider adding sections."
        else:
            return "Response is now satisfactory. No improvements needed."
    
    def _improve(self, task: str, previous_response: str, reflection: str) -> str:
        """Generate improved response based on reflection"""
        # In a real implementation, this would use an LLM
        # For demo, we simulate improvement
        
        if "more detail" in reflection:
            return f"{previous_response}\n\nAdditional details:\n- Point 1: Detailed explanation\n- Point 2: With examples\n- Point 3: With context"
        elif "structured" in reflection:
            return f"## Response to: {task}\n\n### Overview\n{previous_response}\n\n### Details\n- Structured point 1\n- Structured point 2\n\n### Conclusion\nComprehensive answer provided."
        else:
            return previous_response


# =============================================================================
# EXAMPLE 4: Multi-Agent System
# =============================================================================

class AgentRole(Enum):
    RESEARCHER = "researcher"
    PLANNER = "planner"
    EXECUTOR = "executor"
    REVIEWER = "reviewer"


@dataclass
class Message:
    """Message passed between agents"""
    sender: AgentRole
    recipient: AgentRole
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseAgent:
    """Base class for specialized agents"""
    
    def __init__(self, role: AgentRole):
        self.role = role
        self.inbox: List[Message] = []
    
    def receive_message(self, message: Message):
        """Receive a message from another agent"""
        self.inbox.append(message)
    
    def process_messages(self) -> List[Message]:
        """Process inbox and return responses"""
        responses = []
        for message in self.inbox:
            response = self.handle_message(message)
            if response:
                responses.append(response)
        self.inbox.clear()
        return responses
    
    def handle_message(self, message: Message) -> Optional[Message]:
        """Handle a single message - to be implemented by subclasses"""
        raise NotImplementedError


class ResearcherAgent(BaseAgent):
    """Agent specialized in gathering information"""
    
    def __init__(self):
        super().__init__(AgentRole.RESEARCHER)
    
    def handle_message(self, message: Message) -> Optional[Message]:
        print(f"🔍 Researcher: Received request - {message.content}")
        
        # Simulate research
        research_findings = f"Research findings on: {message.content}\n" \
                          f"- Finding 1: Key information\n" \
                          f"- Finding 2: Supporting data\n" \
                          f"- Finding 3: Additional context"
        
        return Message(
            sender=self.role,
            recipient=message.sender,
            content=research_findings,
            metadata={"type": "research_results"}
        )


class PlannerAgentSpecialized(BaseAgent):
    """Agent specialized in creating plans"""
    
    def __init__(self):
        super().__init__(AgentRole.PLANNER)
    
    def handle_message(self, message: Message) -> Optional[Message]:
        print(f"📋 Planner: Creating plan based on - {message.content[:50]}...")
        
        # Simulate planning
        plan = "EXECUTION PLAN:\n" \
               "1. Prepare resources\n" \
               "2. Execute main task\n" \
               "3. Validate results\n" \
               "4. Report completion"
        
        return Message(
            sender=self.role,
            recipient=AgentRole.EXECUTOR,
            content=plan,
            metadata={"type": "execution_plan"}
        )


class ExecutorAgent(BaseAgent):
    """Agent specialized in executing tasks"""
    
    def __init__(self):
        super().__init__(AgentRole.EXECUTOR)
    
    def handle_message(self, message: Message) -> Optional[Message]:
        print(f"⚙️  Executor: Executing plan - {message.content[:50]}...")
        
        # Simulate execution
        result = "EXECUTION RESULTS:\n" \
                "✓ All steps completed successfully\n" \
                "✓ No errors encountered\n" \
                "✓ Output generated"
        
        return Message(
            sender=self.role,
            recipient=AgentRole.REVIEWER,
            content=result,
            metadata={"type": "execution_results"}
        )


class ReviewerAgent(BaseAgent):
    """Agent specialized in reviewing work"""
    
    def __init__(self):
        super().__init__(AgentRole.REVIEWER)
    
    def handle_message(self, message: Message) -> Optional[Message]:
        print(f"✅ Reviewer: Reviewing - {message.content[:50]}...")
        
        # Simulate review
        review = "REVIEW RESULTS:\n" \
                "✓ Quality: Excellent\n" \
                "✓ Completeness: All requirements met\n" \
                "✓ Recommendation: Approve"
        
        return Message(
            sender=self.role,
            recipient=message.sender,
            content=review,
            metadata={"type": "review_results", "approved": True}
        )


class MultiAgentOrchestrator:
    """Orchestrates communication between multiple agents"""
    
    def __init__(self):
        self.agents: Dict[AgentRole, BaseAgent] = {
            AgentRole.RESEARCHER: ResearcherAgent(),
            AgentRole.PLANNER: PlannerAgentSpecialized(),
            AgentRole.EXECUTOR: ExecutorAgent(),
            AgentRole.REVIEWER: ReviewerAgent()
        }
    
    def run(self, task: str) -> str:
        """Execute a task using multiple agents"""
        print(f"\n{'='*60}")
        print(f"MULTI-AGENT SYSTEM - TASK: {task}")
        print(f"{'='*60}\n")
        
        # Phase 1: Research
        print("\n--- Phase 1: Research ---")
        research_msg = Message(
            sender=AgentRole.PLANNER,
            recipient=AgentRole.RESEARCHER,
            content=task
        )
        self.agents[AgentRole.RESEARCHER].receive_message(research_msg)
        research_results = self.agents[AgentRole.RESEARCHER].process_messages()
        
        # Phase 2: Planning
        print("\n--- Phase 2: Planning ---")
        if research_results:
            self.agents[AgentRole.PLANNER].receive_message(research_results[0])
            plan = self.agents[AgentRole.PLANNER].process_messages()
            
            # Phase 3: Execution
            print("\n--- Phase 3: Execution ---")
            if plan:
                self.agents[AgentRole.EXECUTOR].receive_message(plan[0])
                execution_results = self.agents[AgentRole.EXECUTOR].process_messages()
                
                # Phase 4: Review
                print("\n--- Phase 4: Review ---")
                if execution_results:
                    self.agents[AgentRole.REVIEWER].receive_message(execution_results[0])
                    review = self.agents[AgentRole.REVIEWER].process_messages()
                    
                    if review and review[0].metadata.get("approved"):
                        return "\n✅ TASK COMPLETED SUCCESSFULLY!\n\nAll agents have completed their work."
        
        return "\n⚠️  Task completed with issues."


# =============================================================================
# EXAMPLE 5: Agent with Memory
# =============================================================================

class AgentMemory:
    """Memory system for an agent"""
    
    def __init__(self):
        self.short_term: List[Dict[str, Any]] = []  # Recent interactions
        self.long_term: Dict[str, Any] = {}  # Persistent knowledge
        self.working_memory: Dict[str, Any] = {}  # Current task context
    
    def add_to_short_term(self, interaction: Dict[str, Any]):
        """Add to short-term memory (limited size)"""
        self.short_term.append(interaction)
        # Keep only last 10 interactions
        if len(self.short_term) > 10:
            self.short_term.pop(0)
    
    def store_long_term(self, key: str, value: Any):
        """Store in long-term memory"""
        self.long_term[key] = value
    
    def retrieve_long_term(self, key: str) -> Optional[Any]:
        """Retrieve from long-term memory"""
        return self.long_term.get(key)
    
    def update_working_memory(self, updates: Dict[str, Any]):
        """Update working memory for current task"""
        self.working_memory.update(updates)
    
    def clear_working_memory(self):
        """Clear working memory (task completed)"""
        self.working_memory.clear()
    
    def get_relevant_context(self, query: str) -> List[Dict[str, Any]]:
        """Retrieve relevant memories for a query"""
        # In a real implementation, this would use semantic search
        # For demo, return recent memories
        return self.short_term[-3:] if self.short_term else []


class MemoryAgent:
    """Agent with memory capabilities"""
    
    def __init__(self, tools: Dict[str, Callable]):
        self.tools = tools
        self.memory = AgentMemory()
    
    def run(self, task: str) -> str:
        """Execute task using memory"""
        print(f"\n{'='*60}")
        print(f"MEMORY AGENT - TASK: {task}")
        print(f"{'='*60}\n")
        
        # Retrieve relevant context from memory
        context = self.memory.get_relevant_context(task)
        print(f"📚 Retrieved {len(context)} relevant memories")
        
        # Setup working memory for this task
        self.memory.update_working_memory({
            "current_task": task,
            "start_time": time.time()
        })
        
        # Execute task
        result = self._execute_with_memory(task, context)
        
        # Store interaction in memory
        self.memory.add_to_short_term({
            "task": task,
            "result": result,
            "timestamp": time.time()
        })
        
        # Store any learned information in long-term memory
        if "user prefers" in result.lower():
            self.memory.store_long_term("user_preference", result)
        
        # Clear working memory
        self.memory.clear_working_memory()
        
        return result
    
    def _execute_with_memory(self, task: str, context: List[Dict[str, Any]]) -> str:
        """Execute task considering memory context"""
        # Use context to inform execution
        context_summary = f"Based on {len(context)} previous interactions, "
        
        # Simulate execution
        result = f"{context_summary}I've completed: {task}"
        
        return result


# =============================================================================
# TOOL DEFINITIONS (for use by agents)
# =============================================================================

def web_search(query: str) -> str:
    """Simulate web search"""
    return f"Search results for '{query}': [Mock result 1, Mock result 2, Mock result 3]"


def calculator(expression: str) -> str:
    """Evaluate mathematical expression"""
    try:
        result = eval(expression)  # In production, use safer evaluation
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"


def read_file(path: str) -> str:
    """Read file contents"""
    try:
        with open(path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


def write_file(path: str, content: str) -> str:
    """Write content to file"""
    try:
        with open(path, 'w') as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


# =============================================================================
# MAIN DEMO
# =============================================================================

def main():
    """Run all agent examples"""
    
    # Tools available to agents
    tools = {
        "web_search": web_search,
        "calculator": calculator,
        "read_file": read_file,
        "write_file": write_file
    }
    
    print("\n" + "="*60)
    print("AGENTIC AI PATTERNS - INTERACTIVE DEMO")
    print("="*60)
    
    # Example 1: ReAct Agent
    print("\n\n1️⃣  REACT AGENT EXAMPLE")
    react_agent = SimpleReActAgent(tools)
    react_agent.run("What's the weather today?")
    
    # Example 2: Planning Agent
    print("\n\n2️⃣  PLANNING AGENT EXAMPLE")
    planning_agent = PlanningAgent(tools)
    planning_agent.run("Build a web application")
    
    # Example 3: Reflection Agent
    print("\n\n3️⃣  REFLECTION AGENT EXAMPLE")
    reflection_agent = ReflectionAgent(max_reflections=3)
    reflection_agent.run("Explain quantum computing")
    
    # Example 4: Multi-Agent System
    print("\n\n4️⃣  MULTI-AGENT SYSTEM EXAMPLE")
    orchestrator = MultiAgentOrchestrator()
    orchestrator.run("Develop a new feature for the product")
    
    # Example 5: Agent with Memory
    print("\n\n5️⃣  MEMORY AGENT EXAMPLE")
    memory_agent = MemoryAgent(tools)
    memory_agent.run("Summarize today's meetings")
    memory_agent.run("What did I ask about earlier?")  # Uses memory
    
    print("\n\n" + "="*60)
    print("DEMO COMPLETE!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
