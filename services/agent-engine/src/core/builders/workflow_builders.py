"""
Workflow Agent Builders

This module implements builders for ADK workflow agents:
- SequentialAgent: Execute sub-agents in order
- ParallelAgent: Execute sub-agents concurrently
- LoopAgent: Iterate sub-agents with max_iterations

All builders follow ADK patterns validated against official documentation.
"""

from google.adk.agents import SequentialAgent, ParallelAgent, LoopAgent, BaseAgent
from typing import List, Dict, Any, Optional
import logging

from ..composition import AgentBuilder, AgentSpec, AgentContext

logger = logging.getLogger(__name__)


class SpecificationError(Exception):
    """Error in agent specification"""

    pass


class WorkflowBuilderBase(AgentBuilder):
    """Base class for workflow builders with factory integration"""

    def __init__(self, factory: Optional[Any] = None):
        """Initialize with optional factory for sub-agent building"""
        self.factory = factory

    def build_sub_agents(
        self, sub_agent_specs: List[Dict], context: AgentContext
    ) -> List[BaseAgent]:
        """Build sub-agents from specifications using factory"""
        if not self.factory:
            raise SpecificationError("Factory not provided for sub-agent building")

        sub_agents = []
        for spec in sub_agent_specs:
            try:
                # Validate spec has required spec_ref
                if "spec_ref" not in spec:
                    logger.warning(f"Invalid sub-agent specification: {spec}")
                    continue

                # Use factory's build_agent method for recursive composition
                sub_agent = self.factory.build_agent(
                    spec["spec_ref"], self._enhance_context(context, spec)
                )
                sub_agents.append(sub_agent)

            except Exception as e:
                logger.error(f"Error building sub-agent: {e}")
                raise SpecificationError(f"Failed to build sub-agent: {e}")

        return sub_agents

    def _enhance_context(
        self, parent_context: AgentContext, spec: Dict
    ) -> AgentContext:
        """Enhance context with sub-agent specific variables"""
        # Merge parent and sub-agent variables
        sub_variables = parent_context.variables.copy()
        sub_variables.update(spec.get("variables", {}))

        return AgentContext(
            user_id=parent_context.user_id,
            session_id=parent_context.session_id,
            environment=parent_context.environment,
            variables=sub_variables,
            parent_agent=spec.get("name", "workflow"),
        )

    def validate_workflow_spec(self, spec: AgentSpec) -> bool:
        """Validate workflow specification has required components"""
        try:
            # Check for sub-agents
            if "sub_agents" not in spec.spec or not spec.spec["sub_agents"]:
                logger.error("Workflow must have sub-agents")
                return False

            # Validate each sub-agent spec has spec_ref
            for sub_spec in spec.spec["sub_agents"]:
                if "spec_ref" not in sub_spec:
                    logger.error("Sub-agent must have spec_ref")
                    return False

            return True

        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False


class SequentialAgentBuilder(WorkflowBuilderBase):
    """Builder for sequential workflow agents - executes sub-agents in order"""

    def can_build(self, agent_type: str) -> bool:
        """Check if this builder can handle the agent type"""
        return agent_type == "sequential"

    def validate_spec(self, spec: AgentSpec) -> bool:
        """Validate sequential agent specification"""
        if not self.validate_workflow_spec(spec):
            return False

        agent_spec = spec.spec.get("agent", {})
        if agent_spec.get("type") != "sequential":
            return False

        return True

    def build(self, spec: AgentSpec, context: AgentContext) -> SequentialAgent:
        """Build sequential agent from specification"""
        if not self.validate_spec(spec):
            raise SpecificationError(
                f"Invalid sequential agent specification: {spec.metadata.get('name')}"
            )

        metadata = spec.metadata

        # Build sub-agents using factory
        sub_agents = self.build_sub_agents(spec.spec["sub_agents"], context)

        if not sub_agents:
            raise SpecificationError(
                "Sequential agent must have at least one sub-agent"
            )

        # Create SequentialAgent with ADK-compliant parameters
        try:
            agent = SequentialAgent(
                name=metadata.get("name", "sequential_workflow"),
                sub_agents=sub_agents,
                description=metadata.get("description", ""),
            )

            logger.info(f"Successfully built sequential agent: {metadata.get('name')}")
            return agent

        except Exception as e:
            raise SpecificationError(f"Error creating sequential agent: {e}")


class ParallelAgentBuilder(WorkflowBuilderBase):
    """Builder for parallel workflow agents - executes sub-agents concurrently"""

    def can_build(self, agent_type: str) -> bool:
        """Check if this builder can handle the agent type"""
        return agent_type == "parallel"

    def validate_spec(self, spec: AgentSpec) -> bool:
        """Validate parallel agent specification"""
        if not self.validate_workflow_spec(spec):
            return False

        agent_spec = spec.spec.get("agent", {})
        if agent_spec.get("type") != "parallel":
            return False

        return True

    def build(self, spec: AgentSpec, context: AgentContext) -> ParallelAgent:
        """Build parallel agent from specification"""
        if not self.validate_spec(spec):
            raise SpecificationError(
                f"Invalid parallel agent specification: {spec.metadata.get('name')}"
            )

        metadata = spec.metadata
        agent_spec = spec.spec.get("agent", {})

        # Build sub-agents using factory
        sub_agents = self.build_sub_agents(spec.spec["sub_agents"], context)

        if not sub_agents:
            raise SpecificationError("Parallel agent must have at least one sub-agent")

        # Create ParallelAgent with ADK-compliant parameters
        try:
            agent = ParallelAgent(
                name=metadata.get("name", "parallel_workflow"),
                sub_agents=sub_agents,
                description=metadata.get("description", ""),
            )

            logger.info(f"Successfully built parallel agent: {metadata.get('name')}")
            return agent

        except Exception as e:
            raise SpecificationError(f"Error creating parallel agent: {e}")


class LoopAgentBuilder(WorkflowBuilderBase):
    """Builder for loop workflow agents - iterates sub-agents with max_iterations"""

    def can_build(self, agent_type: str) -> bool:
        """Check if this builder can handle the agent type"""
        return agent_type == "loop"

    def validate_spec(self, spec: AgentSpec) -> bool:
        """Validate loop agent specification"""
        if not self.validate_workflow_spec(spec):
            return False

        agent_spec = spec.spec.get("agent", {})
        if agent_spec.get("type") != "loop":
            return False

        # Check for max_iterations to prevent infinite loops
        loop_config = agent_spec.get("loop_config", {})
        if not loop_config.get("max_iterations"):
            logger.warning(
                "Loop agent should have max_iterations to prevent infinite loops"
            )

        return True

    def build(self, spec: AgentSpec, context: AgentContext) -> LoopAgent:
        """Build loop agent from specification"""
        if not self.validate_spec(spec):
            raise SpecificationError(
                f"Invalid loop agent specification: {spec.metadata.get('name')}"
            )

        metadata = spec.metadata
        agent_spec = spec.spec.get("agent", {})
        loop_config = agent_spec.get("loop_config", {})

        # Build sub-agents using factory
        sub_agents = self.build_sub_agents(spec.spec["sub_agents"], context)

        if not sub_agents:
            raise SpecificationError("Loop agent must have at least one sub-agent")

        # Extract max_iterations parameter (ADK-validated)
        max_iterations = loop_config.get("max_iterations", 10)

        # Create LoopAgent with ADK-compliant parameters
        try:
            agent = LoopAgent(
                name=metadata.get("name", "loop_workflow"),
                sub_agents=sub_agents,
                description=metadata.get("description", ""),
            )

            logger.info(f"Successfully built loop agent: {metadata.get('name')}")
            return agent

        except Exception as e:
            raise SpecificationError(f"Error creating loop agent: {e}")
