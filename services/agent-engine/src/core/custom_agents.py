"""
Built-in custom agent implementations following ADK patterns.
Implements R2-T04: Custom Agents with proper BaseAgent inheritance.
"""

from typing import AsyncGenerator, List, Dict, Any, Optional
import logging

# Real ADK imports for custom agent implementation - no fallbacks
from google.adk.agents import BaseAgent
from google.adk.events import Event
from google.adk.agents.invocation_context import InvocationContext

logger = logging.getLogger(__name__)


class AdaptiveOrchestrator(BaseAgent):
    """Example custom agent with adaptive orchestration logic.

    Follows ADK custom agent pattern with _run_async_impl implementation.
    """

    def __init__(
        self,
        name: str,
        sub_agents: List[BaseAgent] = None,
        orchestration_pattern: str = "adaptive",
        max_iterations: int = 3,
        description: str = "",
        **kwargs,
    ):
        """Initialize adaptive orchestrator.

        Follows ADK pattern: pass only allowed fields to super().__init__()
        """
        # Initialize with only ADK BaseAgent fields
        super().__init__(
            name=name,
            sub_agents=sub_agents or [],
            description=description,
            **{
                k: v
                for k, v in kwargs.items()
                if k
                in ["parent_agent", "before_agent_callback", "after_agent_callback"]
            },
        )

        # Store custom fields as instance attributes (not Pydantic fields)
        object.__setattr__(self, "orchestration_pattern", orchestration_pattern)
        object.__setattr__(self, "max_iterations", max_iterations)
        object.__setattr__(
            self, "agents", {agent.name: agent for agent in (sub_agents or [])}
        )

        logger.info(
            f"Created AdaptiveOrchestrator: {name} with {len(self.agents)} sub-agents"
        )

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """Implement adaptive orchestration logic.

        Correct method name and signature for Python ADK.
        """
        logger.info(f"Starting adaptive orchestration: {self.name}")
        iteration = 0

        while iteration < self.max_iterations:
            # Analyze current state
            state = ctx.session.state if hasattr(ctx.session, "state") else {}

            # Determine next agent based on state
            next_agent = self._select_next_agent(state, iteration)

            if not next_agent:
                logger.info(
                    f"No more agents to execute, stopping at iteration {iteration}"
                )
                break

            logger.info(f"Iteration {iteration}: executing agent {next_agent.name}")

            # Execute selected agent
            try:
                if hasattr(next_agent, "run_async"):
                    async for event in next_agent.run_async(ctx):
                        yield event

                        # Update state based on event
                        if event.type == "result":
                            if hasattr(ctx.session, "state"):
                                ctx.session.state["last_result"] = event.data
                            state["last_result"] = event.data
                else:
                    # Fallback for agents without run_async
                    yield Event(type="result", data=f"Executed {next_agent.name}")

            except Exception as e:
                logger.error(f"Error executing agent {next_agent.name}: {e}")
                yield Event(type="error", data=str(e))
                break

            iteration += 1

        # Final event
        logger.info(f"Adaptive orchestration completed after {iteration} iterations")
        yield Event(
            type="completion",
            data={
                "iterations": iteration,
                "orchestration_pattern": self.orchestration_pattern,
                "agents_executed": iteration,
            },
        )

    def _select_next_agent(
        self, state: Dict[Any, Any], iteration: int
    ) -> Optional[BaseAgent]:
        """Select next agent based on current state and pattern."""
        if self.orchestration_pattern == "adaptive":
            # Adaptive logic based on state
            if "error" in state:
                return self.agents.get("error_handler")
            elif iteration == 0:
                # First iteration: use analyzer if available
                return self.agents.get("analyzer") or self._get_first_agent()
            else:
                # Subsequent iterations: use processor if available
                return self.agents.get("processor") or self._get_next_agent(iteration)
        elif self.orchestration_pattern == "sequential":
            # Sequential execution of all agents
            agent_list = list(self.agents.values())
            if iteration < len(agent_list):
                return agent_list[iteration]

        return None

    def _get_first_agent(self) -> Optional[BaseAgent]:
        """Get the first available agent."""
        return next(iter(self.agents.values())) if self.agents else None

    def _get_next_agent(self, iteration: int) -> Optional[BaseAgent]:
        """Get next agent in sequence."""
        agent_list = list(self.agents.values())
        if iteration < len(agent_list):
            return agent_list[iteration]
        return None


class ConditionalRouter(BaseAgent):
    """Custom agent that routes to sub-agents based on conditions.

    Another example of custom agent pattern with conditional logic.
    """

    def __init__(
        self,
        name: str,
        sub_agents: List[BaseAgent] = None,
        routing_rules: Dict[str, str] = None,
        description: str = "",
        **kwargs,
    ):
        """Initialize conditional router."""
        # Initialize with only ADK BaseAgent fields
        super().__init__(
            name=name,
            sub_agents=sub_agents or [],
            description=description,
            **{
                k: v
                for k, v in kwargs.items()
                if k
                in ["parent_agent", "before_agent_callback", "after_agent_callback"]
            },
        )

        # Store custom fields as instance attributes
        object.__setattr__(self, "routing_rules", routing_rules or {})
        object.__setattr__(
            self, "agents", {agent.name: agent for agent in (sub_agents or [])}
        )

        logger.info(
            f"Created ConditionalRouter: {name} with {len(self.routing_rules)} rules"
        )

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """Route to agents based on conditions."""
        logger.info(f"Starting conditional routing: {self.name}")
        input_data = ctx.input if hasattr(ctx, "input") else {}

        executed_agents = []

        for condition, agent_name in self.routing_rules.items():
            if self._evaluate_condition(condition, input_data):
                agent = self.agents.get(agent_name)
                if agent:
                    logger.info(
                        f"Condition '{condition}' matched, executing agent: {agent_name}"
                    )
                    executed_agents.append(agent_name)

                    try:
                        if hasattr(agent, "run_async"):
                            async for event in agent.run_async(ctx):
                                yield event
                        else:
                            # Fallback for agents without run_async
                            yield Event(type="result", data=f"Executed {agent_name}")
                    except Exception as e:
                        logger.error(f"Error executing agent {agent_name}: {e}")
                        yield Event(type="error", data=str(e))

                    break  # Execute only the first matching condition
                else:
                    logger.warning(
                        f"Agent '{agent_name}' not found for condition '{condition}'"
                    )

        if not executed_agents:
            logger.warning("No conditions matched, no agents executed")
            yield Event(type="no_match", data="No routing conditions matched")

        # Final routing summary
        yield Event(
            type="routing_complete",
            data={
                "executed_agents": executed_agents,
                "total_rules": len(self.routing_rules),
                "input_evaluated": bool(input_data),
            },
        )

    def _evaluate_condition(self, condition: str, data: Any) -> bool:
        """Evaluate routing condition safely."""
        try:
            # Simple evaluation logic (can be extended)
            # Support basic patterns like: input.type == 'text', input.priority > 5
            if condition == "true":
                return True
            elif condition == "false":
                return False
            elif "input." in condition:
                # Basic input property checks
                if hasattr(data, "__getitem__"):
                    # Handle dict-like input
                    if condition.startswith("input.type"):
                        return data.get("type") is not None
                    elif condition.startswith("input.priority"):
                        return data.get("priority") is not None

            # Fallback: use eval with limited namespace for safety
            safe_namespace = {
                "input": data,
                "len": len,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
            }
            return bool(eval(condition, {"__builtins__": {}}, safe_namespace))
        except Exception as e:
            logger.warning(f"Error evaluating condition '{condition}': {e}")
            return False


class StatefulWorkflow(BaseAgent):
    """Example custom agent that maintains state across executions.

    Demonstrates state management patterns in custom agents.
    """

    def __init__(
        self,
        name: str,
        sub_agents: List[BaseAgent] = None,
        workflow_steps: List[str] = None,
        allow_restart: bool = True,
        description: str = "",
        **kwargs,
    ):
        """Initialize stateful workflow."""
        # Initialize with only ADK BaseAgent fields
        super().__init__(
            name=name,
            sub_agents=sub_agents or [],
            description=description,
            **{
                k: v
                for k, v in kwargs.items()
                if k
                in ["parent_agent", "before_agent_callback", "after_agent_callback"]
            },
        )

        # Store custom fields as instance attributes
        object.__setattr__(self, "workflow_steps", workflow_steps or [])
        object.__setattr__(self, "allow_restart", allow_restart)
        object.__setattr__(
            self, "agents", {agent.name: agent for agent in (sub_agents or [])}
        )

        logger.info(
            f"Created StatefulWorkflow: {name} with {len(self.workflow_steps)} steps"
        )

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """Execute workflow with state management."""
        logger.info(f"Starting stateful workflow: {self.name}")

        # Get or initialize workflow state
        state = getattr(ctx.session, "state", {}) if hasattr(ctx, "session") else {}
        workflow_state = state.get(
            f"workflow_{self.name}",
            {
                "current_step": 0,
                "completed_steps": [],
                "failed_steps": [],
                "restart_count": 0,
            },
        )

        current_step = workflow_state["current_step"]

        # Check if workflow was previously failed and restart is allowed
        if workflow_state.get("failed_steps") and self.allow_restart:
            logger.info(f"Restarting workflow from step {current_step}")
            workflow_state["restart_count"] += 1
            yield Event(
                type="workflow_restart",
                data={
                    "restart_count": workflow_state["restart_count"],
                    "failed_steps": workflow_state["failed_steps"],
                },
            )

        # Execute workflow steps
        while current_step < len(self.workflow_steps):
            step_name = self.workflow_steps[current_step]
            agent = self.agents.get(step_name)

            if not agent:
                logger.error(f"Agent not found for step: {step_name}")
                workflow_state["failed_steps"].append(step_name)
                yield Event(
                    type="step_failed",
                    data={"step": step_name, "reason": "Agent not found"},
                )
                break

            logger.info(
                f"Executing workflow step {current_step + 1}/{len(self.workflow_steps)}: {step_name}"
            )

            try:
                if hasattr(agent, "run_async"):
                    async for event in agent.run_async(ctx):
                        yield event

                        # Check for step failure
                        if event.type == "error":
                            workflow_state["failed_steps"].append(step_name)
                            raise Exception(f"Step failed: {event.data}")
                else:
                    # Fallback for agents without run_async
                    yield Event(type="result", data=f"Executed step {step_name}")

                # Mark step as completed
                workflow_state["completed_steps"].append(step_name)
                current_step += 1
                workflow_state["current_step"] = current_step

                yield Event(
                    type="step_completed",
                    data={
                        "step": step_name,
                        "step_number": current_step,
                        "total_steps": len(self.workflow_steps),
                    },
                )

            except Exception as e:
                logger.error(f"Error in workflow step {step_name}: {e}")
                workflow_state["failed_steps"].append(step_name)
                yield Event(
                    type="step_failed", data={"step": step_name, "error": str(e)}
                )
                break

        # Update session state
        if hasattr(ctx, "session") and hasattr(ctx.session, "state"):
            ctx.session.state[f"workflow_{self.name}"] = workflow_state

        # Final workflow status
        is_complete = current_step >= len(self.workflow_steps)
        yield Event(
            type="workflow_complete" if is_complete else "workflow_failed",
            data={
                "completed_steps": workflow_state["completed_steps"],
                "failed_steps": workflow_state["failed_steps"],
                "total_steps": len(self.workflow_steps),
                "restart_count": workflow_state["restart_count"],
                "success": is_complete,
            },
        )


# Registry of built-in custom agents
BUILT_IN_CUSTOM_AGENTS = {
    "AdaptiveOrchestrator": AdaptiveOrchestrator,
    "ConditionalRouter": ConditionalRouter,
    "StatefulWorkflow": StatefulWorkflow,
}


def register_built_in_agents(factory):
    """Register all built-in custom agents with the factory."""
    for name, agent_class in BUILT_IN_CUSTOM_AGENTS.items():
        try:
            factory.register_custom_agent(name, agent_class)
            logger.info(f"Registered built-in custom agent: {name}")
        except Exception as e:
            logger.error(f"Failed to register built-in custom agent {name}: {e}")
