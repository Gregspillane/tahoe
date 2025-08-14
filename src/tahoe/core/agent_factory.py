"""
Factory for creating ADK agents from configurations
"""

from typing import Dict, Any, List, Optional
from google.adk.agents import (
    BaseAgent, LlmAgent, SequentialAgent, 
    ParallelAgent, LoopAgent
)
from google.adk.tools import FunctionTool, AgentTool
import logging

logger = logging.getLogger(__name__)


class AgentFactory:
    """Creates ADK agents from configuration specifications"""
    
    def __init__(self):
        """Initialize the agent factory"""
        self._agent_registry: Dict[str, BaseAgent] = {}
        self._tool_registry: Dict[str, Any] = {}
    
    def create_agent(self, config: Dict[str, Any]) -> BaseAgent:
        """
        Create an agent from configuration
        
        Args:
            config: Agent configuration dictionary
            
        Returns:
            Configured ADK agent instance
        """
        agent_type = config.get('type', 'llm')
        name = config.get('name', 'UnnamedAgent')
        
        logger.info(f"Creating agent: {name} (type: {agent_type})")
        
        # Route to appropriate creation method
        if agent_type == 'llm':
            agent = self._create_llm_agent(config)
        elif agent_type == 'sequential':
            agent = self._create_sequential_agent(config)
        elif agent_type == 'parallel':
            agent = self._create_parallel_agent(config)
        elif agent_type == 'loop':
            agent = self._create_loop_agent(config)
        elif agent_type == 'custom':
            agent = self._create_custom_agent(config)
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        # Register agent for future reference
        self._agent_registry[name] = agent
        return agent
    
    def _create_llm_agent(self, config: Dict[str, Any]) -> LlmAgent:
        """Create an LLM agent"""
        agent_config = config.get('config', {})
        
        # Extract configuration
        name = config.get('name', 'LLMAgent')
        description = config.get('description', '')
        model = agent_config.get('model', 'gemini-2.5-flash-lite')
        instruction = agent_config.get('instruction', '')
        output_key = agent_config.get('output_key')
        
        # Process tools if specified
        tools = self._process_tools(agent_config.get('tools', []))
        
        # Process sub-agents if specified
        sub_agents = self._process_sub_agents(agent_config.get('sub_agents', []))
        
        # Create agent
        agent = LlmAgent(
            name=name,
            description=description,
            model=model,
            instruction=instruction,
            tools=tools,
            sub_agents=sub_agents,
            output_key=output_key
        )
        
        logger.debug(f"Created LLM agent: {name} with model {model}")
        return agent
    
    def _create_sequential_agent(self, config: Dict[str, Any]) -> SequentialAgent:
        """Create a sequential workflow agent"""
        agent_config = config.get('config', {})
        name = config.get('name', 'SequentialAgent')
        description = config.get('description', '')
        
        # Process sub-agents (required for sequential)
        sub_agent_configs = agent_config.get('sub_agents', [])
        if not sub_agent_configs:
            raise ValueError(f"Sequential agent {name} requires sub_agents")
        
        sub_agents = self._process_sub_agents(sub_agent_configs)
        
        agent = SequentialAgent(
            name=name,
            description=description,
            sub_agents=sub_agents
        )
        
        logger.debug(f"Created Sequential agent: {name} with {len(sub_agents)} sub-agents")
        return agent
    
    def _create_parallel_agent(self, config: Dict[str, Any]) -> ParallelAgent:
        """Create a parallel workflow agent"""
        agent_config = config.get('config', {})
        name = config.get('name', 'ParallelAgent')
        description = config.get('description', '')
        
        # Process sub-agents (required for parallel)
        sub_agent_configs = agent_config.get('sub_agents', [])
        if not sub_agent_configs:
            raise ValueError(f"Parallel agent {name} requires sub_agents")
        
        sub_agents = self._process_sub_agents(sub_agent_configs)
        
        agent = ParallelAgent(
            name=name,
            description=description,
            sub_agents=sub_agents
        )
        
        logger.debug(f"Created Parallel agent: {name} with {len(sub_agents)} sub-agents")
        return agent
    
    def _create_loop_agent(self, config: Dict[str, Any]) -> LoopAgent:
        """Create a loop workflow agent"""
        agent_config = config.get('config', {})
        name = config.get('name', 'LoopAgent')
        description = config.get('description', '')
        max_iterations = agent_config.get('max_iterations', 10)
        
        # Process sub-agents (required for loop)
        sub_agent_configs = agent_config.get('sub_agents', [])
        if not sub_agent_configs:
            raise ValueError(f"Loop agent {name} requires sub_agents")
        
        sub_agents = self._process_sub_agents(sub_agent_configs)
        
        agent = LoopAgent(
            name=name,
            description=description,
            sub_agents=sub_agents,
            max_iterations=max_iterations
        )
        
        logger.debug(f"Created Loop agent: {name} with {len(sub_agents)} sub-agents, max_iterations={max_iterations}")
        return agent
    
    def _create_custom_agent(self, config: Dict[str, Any]) -> BaseAgent:
        """Create a custom agent (placeholder for user-defined agents)"""
        # This would load and instantiate custom agent classes
        # For now, raise an error
        raise NotImplementedError("Custom agent creation not yet implemented")
    
    def _process_tools(self, tool_configs: List[Any]) -> List[Any]:
        """Process tool configurations into ADK tools"""
        tools = []
        
        for tool_config in tool_configs:
            if isinstance(tool_config, str):
                # Reference to existing tool
                if tool_config in self._tool_registry:
                    tools.append(self._tool_registry[tool_config])
                else:
                    logger.warning(f"Tool not found in registry: {tool_config}")
            elif isinstance(tool_config, dict):
                # Inline tool definition
                tool_type = tool_config.get('type', 'function')
                
                if tool_type == 'agent':
                    # AgentTool - wrap another agent as a tool
                    agent_name = tool_config.get('agent')
                    if agent_name in self._agent_registry:
                        agent = self._agent_registry[agent_name]
                        tools.append(AgentTool(agent=agent))
                    else:
                        logger.warning(f"Agent not found for AgentTool: {agent_name}")
                elif tool_type == 'function':
                    # FunctionTool - would need to load actual function
                    logger.warning("Function tool loading not yet implemented")
                else:
                    logger.warning(f"Unknown tool type: {tool_type}")
        
        return tools
    
    def _process_sub_agents(self, sub_agent_configs: List[Any]) -> List[BaseAgent]:
        """Process sub-agent configurations"""
        sub_agents = []
        
        for sub_config in sub_agent_configs:
            if isinstance(sub_config, str):
                # Reference to existing agent
                if sub_config in self._agent_registry:
                    sub_agents.append(self._agent_registry[sub_config])
                else:
                    logger.warning(f"Sub-agent not found in registry: {sub_config}")
            elif isinstance(sub_config, dict):
                # Inline agent definition
                sub_agent = self.create_agent(sub_config)
                sub_agents.append(sub_agent)
        
        return sub_agents
    
    def register_tool(self, name: str, tool: Any):
        """Register a tool for use by agents"""
        self._tool_registry[name] = tool
        logger.debug(f"Registered tool: {name}")
    
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get a registered agent by name"""
        return self._agent_registry.get(name)