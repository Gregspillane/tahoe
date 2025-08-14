# Custom agents - Agent Development Kit

*Source: https://google.github.io/adk-docs/agents/custom-agents/*

Advanced Concept

Building custom agents by directly implementing `_run_async_impl` (or its equivalent in other languages) provides powerful control but is more complex than using the predefined `LlmAgent` or standard `WorkflowAgent` types. We recommend understanding those foundational agent types first before tackling custom orchestration logic.

`_run_async_impl`

`LlmAgent`

`WorkflowAgent`

# Custom agents

Custom agents provide the ultimate flexibility in ADK, allowing you to define **arbitrary orchestration logic** by inheriting directly from `BaseAgent` and implementing your own control flow. This goes beyond the predefined patterns of `SequentialAgent`, `LoopAgent`, and `ParallelAgent`, enabling you to build highly specific and complex agentic workflows.

`BaseAgent`

`SequentialAgent`

`LoopAgent`

`ParallelAgent`

## Introduction: Beyond Predefined Workflows

### What is a Custom Agent?

A Custom Agent is essentially any class you create that inherits from `google.adk.agents.BaseAgent` and implements its core execution logic within the `_run_async_impl` asynchronous method. You have complete control over how this method calls other agents (sub-agents), manages state, and handles events.

`google.adk.agents.BaseAgent`

`_run_async_impl`

Note

The specific method name for implementing an agent's core asynchronous logic may vary slightly by SDK language (e.g., `runAsyncImpl` in Java, `_run_async_impl` in Python). Refer to the language-specific API documentation for details.

`runAsyncImpl`

`_run_async_impl`

### Why Use Them?

While the standard [Workflow Agents](../workflow-agents/) (`SequentialAgent`, `LoopAgent`, `ParallelAgent`) cover common orchestration patterns, you'll need a Custom agent when your requirements include:

`SequentialAgent`

`LoopAgent`

`ParallelAgent`

- **Conditional Logic:** Executing different sub-agents or taking different paths based on runtime conditions or the results of previous steps.
- **Complex State Management:** Implementing intricate logic for maintaining and updating state throughout the workflow beyond simple sequential passing.
- **External Integrations:** Incorporating calls to external APIs, databases, or custom libraries directly within the orchestration flow control.
- **Dynamic Agent Selection:** Choosing which sub-agent(s) to run next based on dynamic evaluation of the situation or input.
- **Unique Workflow Patterns:** Implementing orchestration logic that doesn't fit the standard sequential, parallel, or loop structures.



## Implementing Custom Logic:

The core of any custom agent is the method where you define its unique asynchronous behavior. This method allows you to orchestrate sub-agents and manage the flow of execution.

The heart of any custom agent is the `_run_async_impl` method. This is where you define its unique behavior.

`_run_async_impl`

- **Signature:** `async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:`
- **Asynchronous Generator:** It must be an `async def` function and return an `AsyncGenerator`. This allows it to `yield` events produced by sub-agents or its own logic back to the runner.
- **ctx (InvocationContext):** Provides access to crucial runtime information, most importantly `ctx.session.state`, which is the primary way to share data between steps orchestrated by your custom agent.

`async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:`

`async def`

`AsyncGenerator`

`yield`

`ctx`

`ctx.session.state`

The heart of any custom agent is the `runAsyncImpl` method, which you override from `BaseAgent`.

`runAsyncImpl`

`BaseAgent`

- **Signature:** `protected Flowable<Event> runAsyncImpl(InvocationContext ctx)`
- **Reactive Stream (Flowable):** It must return an `io.reactivex.rxjava3.core.Flowable<Event>`. This `Flowable` represents a stream of events that will be produced by the custom agent's logic, often by combining or transforming multiple `Flowable` from sub-agents.
- **ctx (InvocationContext):** Provides access to crucial runtime information, most importantly `ctx.session().state()`, which is a `java.util.concurrent.ConcurrentMap<String, Object>`. This is the primary way to share data between steps orchestrated by your custom agent.

`protected Flowable<Event> runAsyncImpl(InvocationContext ctx)`

`Flowable`

`io.reactivex.rxjava3.core.Flowable<Event>`

`Flowable`

`Flowable`

`ctx`

`ctx.session().state()`

`java.util.concurrent.ConcurrentMap<String, Object>`

**Key Capabilities within the Core Asynchronous Method:**

1. Calling Sub-Agents: You invoke sub-agents (which are typically stored as instance attributes like self.my_llm_agent) using their run_async method and yield their events:
async for event in self.some_sub_agent.run_async(ctx):
    # Optionally inspect or log the event
    yield event # Pass the event up
1. Managing State: Read from and write to the session state dictionary (ctx.session.state) to pass data between sub-agent calls or make decisions:
      # Read data set by a previous agent
previous_result = ctx.session.state.get("some_key")

# Make a decision based on state
if previous_result == "some_value":
    # ... call a specific sub-agent ...
else:
    # ... call another sub-agent ...

# Store a result for a later step (often done via a sub-agent's output_key)
# ctx.session.state["my_custom_result"] = "calculated_value"
1. Implementing Control Flow: Use standard Python constructs (if/elif/else, for/while loops, try/except) to create sophisticated, conditional, or iterative workflows involving your sub-agents.

**Calling Sub-Agents:** You invoke sub-agents (which are typically stored as instance attributes like `self.my_llm_agent`) using their `run_async` method and yield their events:

`self.my_llm_agent`

`run_async`

```
async for event in self.some_sub_agent.run_async(ctx):
    # Optionally inspect or log the event
    yield event # Pass the event up

```

async for event in self.some_sub_agent.run_async(ctx):
    # Optionally inspect or log the event
    yield event # Pass the event up

**Managing State:** Read from and write to the session state dictionary (`ctx.session.state`) to pass data between sub-agent calls or make decisions:
      # Read data set by a previous agent
previous_result = ctx.session.state.get("some_key")

# Make a decision based on state
if previous_result == "some_value":
    # ... call a specific sub-agent ...
else:
    # ... call another sub-agent ...

# Store a result for a later step (often done via a sub-agent's output_key)
# ctx.session.state["my_custom_result"] = "calculated_value"

`ctx.session.state`

```
# Read data set by a previous agent
previous_result = ctx.session.state.get("some_key")

# Make a decision based on state
if previous_result == "some_value":
    # ... call a specific sub-agent ...
else:
    # ... call another sub-agent ...

# Store a result for a later step (often done via a sub-agent's output_key)
# ctx.session.state["my_custom_result"] = "calculated_value"

```

# Read data set by a previous agent
previous_result = ctx.session.state.get("some_key")

# Make a decision based on state
if previous_result == "some_value":
    # ... call a specific sub-agent ...
else:
    # ... call another sub-agent ...

# Store a result for a later step (often done via a sub-agent's output_key)
# ctx.session.state["my_custom_result"] = "calculated_value"

**Implementing Control Flow:** Use standard Python constructs (`if`/`elif`/`else`, `for`/`while` loops, `try`/`except`) to create sophisticated, conditional, or iterative workflows involving your sub-agents.

`if`

`elif`

`else`

`for`

`while`

`try`

`except`

1. Calling Sub-Agents: You invoke sub-agents (which are typically stored as instance attributes or objects) using their asynchronous run method and return their event streams:
You typically chain Flowables from sub-agents using RxJava operators like concatWith, flatMapPublisher, or concatArray.
// Example: Running one sub-agent
// return someSubAgent.runAsync(ctx);

// Example: Running sub-agents sequentially
Flowable<Event> firstAgentEvents = someSubAgent1.runAsync(ctx)
    .doOnNext(event -> System.out.println("Event from agent 1: " + event.id()));

Flowable<Event> secondAgentEvents = Flowable.defer(() ->
    someSubAgent2.runAsync(ctx)
        .doOnNext(event -> System.out.println("Event from agent 2: " + event.id()))
);

return firstAgentEvents.concatWith(secondAgentEvents);

   The Flowable.defer() is often used for subsequent stages if their execution depends on the completion or state after prior stages.
1. Managing State: Read from and write to the session state to pass data between sub-agent calls or make decisions. The session state is a java.util.concurrent.ConcurrentMap<String, Object> obtained via ctx.session().state().
// Read data set by a previous agent
Object previousResult = ctx.session().state().get("some_key");

// Make a decision based on state
if ("some_value".equals(previousResult)) {
    // ... logic to include a specific sub-agent's Flowable ...
} else {
    // ... logic to include another sub-agent's Flowable ...
}

// Store a result for a later step (often done via a sub-agent's output_key)
// ctx.session().state().put("my_custom_result", "calculated_value");
1. Implementing Control Flow: Use standard language constructs (if/else, loops, try/catch) combined with reactive operators (RxJava) to create sophisticated workflows.

Conditional: Flowable.defer() to choose which Flowable to subscribe to based on a condition, or filter() if you're filtering events within a stream.
Iterative: Operators like repeat(), retry(), or by structuring your Flowable chain to recursively call parts of itself based on conditions (often managed with flatMapPublisher or concatMap).

**Calling Sub-Agents:** You invoke sub-agents (which are typically stored as instance attributes or objects) using their asynchronous run method and return their event streams:

You typically chain `Flowable`s from sub-agents using RxJava operators like `concatWith`, `flatMapPublisher`, or `concatArray`.

`Flowable`

`concatWith`

`flatMapPublisher`

`concatArray`

// Example: Running one sub-agent
// return someSubAgent.runAsync(ctx);

// Example: Running sub-agents sequentially
Flowable<Event> firstAgentEvents = someSubAgent1.runAsync(ctx)
    .doOnNext(event -> System.out.println("Event from agent 1: " + event.id()));

Flowable<Event> secondAgentEvents = Flowable.defer(() ->
    someSubAgent2.runAsync(ctx)
        .doOnNext(event -> System.out.println("Event from agent 2: " + event.id()))
);

return firstAgentEvents.concatWith(secondAgentEvents);

   The `Flowable.defer()` is often used for subsequent stages if their execution depends on the completion or state after prior stages.

```
// Example: Running one sub-agent
// return someSubAgent.runAsync(ctx);

// Example: Running sub-agents sequentially
Flowable<Event> firstAgentEvents = someSubAgent1.runAsync(ctx)
    .doOnNext(event -> System.out.println("Event from agent 1: " + event.id()));

Flowable<Event> secondAgentEvents = Flowable.defer(() ->
    someSubAgent2.runAsync(ctx)
        .doOnNext(event -> System.out.println("Event from agent 2: " + event.id()))
);

return firstAgentEvents.concatWith(secondAgentEvents);

```

// Example: Running one sub-agent
// return someSubAgent.runAsync(ctx);

// Example: Running sub-agents sequentially
Flowable<Event> firstAgentEvents = someSubAgent1.runAsync(ctx)
    .doOnNext(event -> System.out.println("Event from agent 1: " + event.id()));

Flowable<Event> secondAgentEvents = Flowable.defer(() ->
    someSubAgent2.runAsync(ctx)
        .doOnNext(event -> System.out.println("Event from agent 2: " + event.id()))
);

return firstAgentEvents.concatWith(secondAgentEvents);

`Flowable.defer()`

**Managing State:** Read from and write to the session state to pass data between sub-agent calls or make decisions. The session state is a `java.util.concurrent.ConcurrentMap<String, Object>` obtained via `ctx.session().state()`.

`java.util.concurrent.ConcurrentMap<String, Object>`

`ctx.session().state()`

```
// Read data set by a previous agent
Object previousResult = ctx.session().state().get("some_key");

// Make a decision based on state
if ("some_value".equals(previousResult)) {
    // ... logic to include a specific sub-agent's Flowable ...
} else {
    // ... logic to include another sub-agent's Flowable ...
}

// Store a result for a later step (often done via a sub-agent's output_key)
// ctx.session().state().put("my_custom_result", "calculated_value");

```

// Read data set by a previous agent
Object previousResult = ctx.session().state().get("some_key");

// Make a decision based on state
if ("some_value".equals(previousResult)) {
    // ... logic to include a specific sub-agent's Flowable ...
} else {
    // ... logic to include another sub-agent's Flowable ...
}

// Store a result for a later step (often done via a sub-agent's output_key)
// ctx.session().state().put("my_custom_result", "calculated_value");

**Implementing Control Flow:** Use standard language constructs (`if`/`else`, loops, `try`/`catch`) combined with reactive operators (RxJava) to create sophisticated workflows.

`if`

`else`

`try`

`catch`

- **Conditional:** `Flowable.defer()` to choose which `Flowable` to subscribe to based on a condition, or `filter()` if you're filtering events within a stream.
- **Iterative:** Operators like `repeat()`, `retry()`, or by structuring your `Flowable` chain to recursively call parts of itself based on conditions (often managed with `flatMapPublisher` or `concatMap`).

`Flowable.defer()`

`Flowable`

`filter()`

`repeat()`

`retry()`

`Flowable`

`flatMapPublisher`

`concatMap`

## Managing Sub-Agents and State

Typically, a custom agent orchestrates other agents (like `LlmAgent`, `LoopAgent`, etc.).

`LlmAgent`

`LoopAgent`

- **Initialization:** You usually pass instances of these sub-agents into your custom agent's constructor and store them as instance fields/attributes (e.g., `this.story_generator = story_generator_instance` or `self.story_generator = story_generator_instance`). This makes them accessible within the custom agent's core asynchronous execution logic (such as: `_run_async_impl` method).
- **Sub Agents List:** When initializing the `BaseAgent` using it's `super()` constructor, you should pass a `sub agents` list. This list tells the ADK framework about the agents that are part of this custom agent's immediate hierarchy. It's important for framework features like lifecycle management, introspection, and potentially future routing capabilities, even if your core execution logic (`_run_async_impl`) calls the agents directly via `self.xxx_agent`. Include the agents that your custom logic directly invokes at the top level.
- **State:** As mentioned, `ctx.session.state` is the standard way sub-agents (especially `LlmAgent`s using `output key`) communicate results back to the orchestrator and how the orchestrator passes necessary inputs down.

`this.story_generator = story_generator_instance`

`self.story_generator = story_generator_instance`

`_run_async_impl`

`BaseAgent`

`super()`

`sub agents`

`_run_async_impl`

`self.xxx_agent`

`ctx.session.state`

`LlmAgent`

`output key`

## Design Pattern Example: StoryFlowAgent

`StoryFlowAgent`

Let's illustrate the power of custom agents with an example pattern: a multi-stage content generation workflow with conditional logic.

**Goal:** Create a system that generates a story, iteratively refines it through critique and revision, performs final checks, and crucially, *regenerates the story if the final tone check fails*.

**Why Custom?** The core requirement driving the need for a custom agent here is the **conditional regeneration based on the tone check**. Standard workflow agents don't have built-in conditional branching based on the outcome of a sub-agent's task. We need custom logic (`if tone == "negative": ...`) within the orchestrator.

`if tone == "negative": ...`

### Part 1: Simplified custom agent Initialization

We define the `StoryFlowAgent` inheriting from `BaseAgent`. In `__init__`, we store the necessary sub-agents (passed in) as instance attributes and tell the `BaseAgent` framework about the top-level agents this custom agent will directly orchestrate.

`StoryFlowAgent`

`BaseAgent`

`__init__`

`BaseAgent`

```
class StoryFlowAgent(BaseAgent):
    """
    Custom agent for a story generation and refinement workflow.

    This agent orchestrates a sequence of LLM agents to generate a story,
    critique it, revise it, check grammar and tone, and potentially
    regenerate the story if the tone is negative.
    """

    # --- Field Declarations for Pydantic ---
    # Declare the agents passed during initialization as class attributes with type hints
    story_generator: LlmAgent
    critic: LlmAgent
    reviser: LlmAgent
    grammar_check: LlmAgent
    tone_check: LlmAgent

    loop_agent: LoopAgent
    sequential_agent: SequentialAgent

    # model_config allows setting Pydantic configurations if needed, e.g., arbitrary_types_allowed
    model_config = {"arbitrary_types_allowed": True}

    def __init__(
        self,
        name: str,
        story_generator: LlmAgent,
        critic: LlmAgent,
        reviser: LlmAgent,
        grammar_check: LlmAgent,
        tone_check: LlmAgent,
    ):
        """
        Initializes the StoryFlowAgent.

        Args:
            name: The name of the agent.
            story_generator: An LlmAgent to generate the initial story.
            critic: An LlmAgent to critique the story.
            reviser: An LlmAgent to revise the story based on criticism.
            grammar_check: An LlmAgent to check the grammar.
            tone_check: An LlmAgent to analyze the tone.
        """
        # Create internal agents *before* calling super().__init__
        loop_agent = LoopAgent(
            name="CriticReviserLoop", sub_agents=[critic, reviser], max_iterations=2
        )
        sequential_agent = SequentialAgent(
            name="PostProcessing", sub_agents=[grammar_check, tone_check]
        )

        # Define the sub_agents list for the framework
        sub_agents_list = [
            story_generator,
            loop_agent,
            sequential_agent,
        ]

        # Pydantic will validate and assign them based on the class annotations.
        super().__init__(
            name=name,
            story_generator=story_generator,
            critic=critic,
            reviser=reviser,
            grammar_check=grammar_check,
            tone_check=tone_check,
            loop_agent=loop_agent,
            sequential_agent=sequential_agent,
            sub_agents=sub_agents_list, # Pass the sub_agents list directly
        )

```

class StoryFlowAgent(BaseAgent):
    """
    Custom agent for a story generation and refinement workflow.

    This agent orchestrates a sequence of LLM agents to generate a story,
    critique it, revise it, check grammar and tone, and potentially
    regenerate the story if the tone is negative.
    """

    # --- Field Declarations for Pydantic ---
    # Declare the agents passed during initialization as class attributes with type hints
    story_generator: LlmAgent
    critic: LlmAgent
    reviser: LlmAgent
    grammar_check: LlmAgent
    tone_check: LlmAgent

    loop_agent: LoopAgent
    sequential_agent: SequentialAgent

    # model_config allows setting Pydantic configurations if needed, e.g., arbitrary_types_allowed
    model_config = {"arbitrary_types_allowed": True}

    def __init__(
        self,
        name: str,
        story_generator: LlmAgent,
        critic: LlmAgent,
        reviser: LlmAgent,
        grammar_check: LlmAgent,
        tone_check: LlmAgent,
    ):
        """
        Initializes the StoryFlowAgent.

        Args:
            name: The name of the agent.
            story_generator: An LlmAgent to generate the initial story.
            critic: An LlmAgent to critique the story.
            reviser: An LlmAgent to revise the story based on criticism.
            grammar_check: An LlmAgent to check the grammar.
            tone_check: An LlmAgent to analyze the tone.
        """
        # Create internal agents *before* calling super().__init__
        loop_agent = LoopAgent(
            name="CriticReviserLoop", sub_agents=[critic, reviser], max_iterations=2
        )
        sequential_agent = SequentialAgent(
            name="PostProcessing", sub_agents=[grammar_check, tone_check]
        )

        # Define the sub_agents list for the framework
        sub_agents_list = [
            story_generator,
            loop_agent,
            sequential_agent,
        ]

        # Pydantic will validate and assign them based on the class annotations.
        super().__init__(
            name=name,
            story_generator=story_generator,
            critic=critic,
            reviser=reviser,
            grammar_check=grammar_check,
            tone_check=tone_check,
            loop_agent=loop_agent,
            sequential_agent=sequential_agent,
            sub_agents=sub_agents_list, # Pass the sub_agents list directly
        )

We define the `StoryFlowAgentExample` by extending `BaseAgent`. In its **constructor**, we store the necessary sub-agent instances (passed as parameters) as instance fields. These top-level sub-agents, which this custom agent will directly orchestrate, are also passed to the `super` constructor of `BaseAgent` as a list.

`StoryFlowAgentExample`

`BaseAgent`

`super`

`BaseAgent`

```
private final LlmAgent storyGenerator;
private final LoopAgent loopAgent;
private final SequentialAgent sequentialAgent;

public StoryFlowAgentExample(
    String name, LlmAgent storyGenerator, LoopAgent loopAgent, SequentialAgent sequentialAgent) {
  super(
      name,
      "Orchestrates story generation, critique, revision, and checks.",
      List.of(storyGenerator, loopAgent, sequentialAgent),
      null,
      null);

  this.storyGenerator = storyGenerator;
  this.loopAgent = loopAgent;
  this.sequentialAgent = sequentialAgent;
}

```

private final LlmAgent storyGenerator;
private final LoopAgent loopAgent;
private final SequentialAgent sequentialAgent;

public StoryFlowAgentExample(
    String name, LlmAgent storyGenerator, LoopAgent loopAgent, SequentialAgent sequentialAgent) {
  super(
      name,
      "Orchestrates story generation, critique, revision, and checks.",
      List.of(storyGenerator, loopAgent, sequentialAgent),
      null,
      null);

  this.storyGenerator = storyGenerator;
  this.loopAgent = loopAgent;
  this.sequentialAgent = sequentialAgent;
}

### Part 2: Defining the Custom Execution Logic

This method orchestrates the sub-agents using standard Python async/await and control flow.

@override
async def _run_async_impl(
    self, ctx: InvocationContext
) -> AsyncGenerator[Event, None]:
    """
    Implements the custom orchestration logic for the story workflow.
    Uses the instance attributes assigned by Pydantic (e.g., self.story_generator).
    """
    logger.info(f"[{self.name}] Starting story generation workflow.")

    # 1. Initial Story Generation
    logger.info(f"[{self.name}] Running StoryGenerator...")
    async for event in self.story_generator.run_async(ctx):
        logger.info(f"[{self.name}] Event from StoryGenerator: {event.model_dump_json(indent=2, exclude_none=True)}")
        yield event

    # Check if story was generated before proceeding
    if "current_story" not in ctx.session.state or not ctx.session.state["current_story"]:
         logger.error(f"[{self.name}] Failed to generate initial story. Aborting workflow.")
         return # Stop processing if initial story failed

    logger.info(f"[{self.name}] Story state after generator: {ctx.session.state.get('current_story')}")


    # 2. Critic-Reviser Loop
    logger.info(f"[{self.name}] Running CriticReviserLoop...")
    # Use the loop_agent instance attribute assigned during init
    async for event in self.loop_agent.run_async(ctx):
        logger.info(f"[{self.name}] Event from CriticReviserLoop: {event.model_dump_json(indent=2, exclude_none=True)}")
        yield event

    logger.info(f"[{self.name}] Story state after loop: {ctx.session.state.get('current_story')}")

    # 3. Sequential Post-Processing (Grammar and Tone Check)
    logger.info(f"[{self.name}] Running PostProcessing...")
    # Use the sequential_agent instance attribute assigned during init
    async for event in self.sequential_agent.run_async(ctx):
        logger.info(f"[{self.name}] Event from PostProcessing: {event.model_dump_json(indent=2, exclude_none=True)}")
        yield event

    # 4. Tone-Based Conditional Logic
    tone_check_result = ctx.session.state.get("tone_check_result")
    logger.info(f"[{self.name}] Tone check result: {tone_check_result}")

    if tone_check_result == "negative":
        logger.info(f"[{self.name}] Tone is negative. Regenerating story...")
        async for event in self.story_generator.run_async(ctx):
            logger.info(f"[{self.name}] Event from StoryGenerator (Regen): {event.model_dump_json(indent=2, exclude_none=True)}")
            yield event
    else:
        logger.info(f"[{self.name}] Tone is not negative. Keeping current story.")
        pass

    logger.info(f"[{self.name}] Workflow finished.")

**Explanation of Logic:**

```
@override
async def _run_async_impl(
    self, ctx: InvocationContext
) -> AsyncGenerator[Event, None]:
    """
    Implements the custom orchestration logic for the story workflow.
    Uses the instance attributes assigned by Pydantic (e.g., self.story_generator).
    """
    logger.info(f"[{self.name}] Starting story generation workflow.")

    # 1. Initial Story Generation
    logger.info(f"[{self.name}] Running StoryGenerator...")
    async for event in self.story_generator.run_async(ctx):
        logger.info(f"[{self.name}] Event from StoryGenerator: {event.model_dump_json(indent=2, exclude_none=True)}")
        yield event

    # Check if story was generated before proceeding
    if "current_story" not in ctx.session.state or not ctx.session.state["current_story"]:
         logger.error(f"[{self.name}] Failed to generate initial story. Aborting workflow.")
         return # Stop processing if initial story failed

    logger.info(f"[{self.name}] Story state after generator: {ctx.session.state.get('current_story')}")


    # 2. Critic-Reviser Loop
    logger.info(f"[{self.name}] Running CriticReviserLoop...")
    # Use the loop_agent instance attribute assigned during init
    async for event in self.loop_agent.run_async(ctx):
        logger.info(f"[{self.name}] Event from CriticReviserLoop: {event.model_dump_json(indent=2, exclude_none=True)}")
        yield event

    logger.info(f"[{self.name}] Story state after loop: {ctx.session.state.get('current_story')}")

    # 3. Sequential Post-Processing (Grammar and Tone Check)
    logger.info(f"[{self.name}] Running PostProcessing...")
    # Use the sequential_agent instance attribute assigned during init
    async for event in self.sequential_agent.run_async(ctx):
        logger.info(f"[{self.name}] Event from PostProcessing: {event.model_dump_json(indent=2, exclude_none=True)}")
        yield event

    # 4. Tone-Based Conditional Logic
    tone_check_result = ctx.session.state.get("tone_check_result")
    logger.info(f"[{self.name}] Tone check result: {tone_check_result}")

    if tone_check_result == "negative":
        logger.info(f"[{self.name}] Tone is negative. Regenerating story...")
        async for event in self.story_generator.run_async(ctx):
            logger.info(f"[{self.name}] Event from StoryGenerator (Regen): {event.model_dump_json(indent=2, exclude_none=True)}")
            yield event
    else:
        logger.info(f"[{self.name}] Tone is not negative. Keeping current story.")
        pass

    logger.info(f"[{self.name}] Workflow finished.")

```

@override
async def _run_async_impl(
    self, ctx: InvocationContext
) -> AsyncGenerator[Event, None]:
    """
    Implements the custom orchestration logic for the story workflow.
    Uses the instance attributes assigned by Pydantic (e.g., self.story_generator).
    """
    logger.info(f"[{self.name}] Starting story generation workflow.")

    # 1. Initial Story Generation
    logger.info(f"[{self.name}] Running StoryGenerator...")
    async for event in self.story_generator.run_async(ctx):
        logger.info(f"[{self.name}] Event from StoryGenerator: {event.model_dump_json(indent=2, exclude_none=True)}")
        yield event

    # Check if story was generated before proceeding
    if "current_story" not in ctx.session.state or not ctx.session.state["current_story"]:
         logger.error(f"[{self.name}] Failed to generate initial story. Aborting workflow.")
         return # Stop processing if initial story failed

    logger.info(f"[{self.name}] Story state after generator: {ctx.session.state.get('current_story')}")


    # 2. Critic-Reviser Loop
    logger.info(f"[{self.name}] Running CriticReviserLoop...")
    # Use the loop_agent instance attribute assigned during init
    async for event in self.loop_agent.run_async(ctx):
        logger.info(f"[{self.name}] Event from CriticReviserLoop: {event.model_dump_json(indent=2, exclude_none=True)}")
        yield event

    logger.info(f"[{self.name}] Story state after loop: {ctx.session.state.get('current_story')}")

    # 3. Sequential Post-Processing (Grammar and Tone Check)
    logger.info(f"[{self.name}] Running PostProcessing...")
    # Use the sequential_agent instance attribute assigned during init
    async for event in self.sequential_agent.run_async(ctx):
        logger.info(f"[{self.name}] Event from PostProcessing: {event.model_dump_json(indent=2, exclude_none=True)}")
        yield event

    # 4. Tone-Based Conditional Logic
    tone_check_result = ctx.session.state.get("tone_check_result")
    logger.info(f"[{self.name}] Tone check result: {tone_check_result}")

    if tone_check_result == "negative":
        logger.info(f"[{self.name}] Tone is negative. Regenerating story...")
        async for event in self.story_generator.run_async(ctx):
            logger.info(f"[{self.name}] Event from StoryGenerator (Regen): {event.model_dump_json(indent=2, exclude_none=True)}")
            yield event
    else:
        logger.info(f"[{self.name}] Tone is not negative. Keeping current story.")
        pass

    logger.info(f"[{self.name}] Workflow finished.")

1. The initial `story_generator` runs. Its output is expected to be in `ctx.session.state["current_story"]`.
1. The `loop_agent` runs, which internally calls the `critic` and `reviser` sequentially for `max_iterations` times. They read/write `current_story` and `criticism` from/to the state.
1. The `sequential_agent` runs, calling `grammar_check` then `tone_check`, reading `current_story` and writing `grammar_suggestions` and `tone_check_result` to the state.
1. **Custom Part:** The `if` statement checks the `tone_check_result` from the state. If it's "negative", the `story_generator` is called *again*, overwriting the `current_story` in the state. Otherwise, the flow ends.

`story_generator`

`ctx.session.state["current_story"]`

`loop_agent`

`critic`

`reviser`

`max_iterations`

`current_story`

`criticism`

`sequential_agent`

`grammar_check`

`tone_check`

`current_story`

`grammar_suggestions`

`tone_check_result`

`if`

`tone_check_result`

`story_generator`

`current_story`

The `runAsyncImpl` method orchestrates the sub-agents using RxJava's Flowable streams and operators for asynchronous control flow.

`runAsyncImpl`

@Override
protected Flowable<Event> runAsyncImpl(InvocationContext invocationContext) {
  // Implements the custom orchestration logic for the story workflow.
  // Uses the instance attributes assigned by Pydantic (e.g., self.story_generator).
  logger.log(Level.INFO, () -> String.format("[%s] Starting story generation workflow.", name()));

  // Stage 1. Initial Story Generation
  Flowable<Event> storyGenFlow = runStage(storyGenerator, invocationContext, "StoryGenerator");

  // Stage 2: Critic-Reviser Loop (runs after story generation completes)
  Flowable<Event> criticReviserFlow = Flowable.defer(() -> {
    if (!isStoryGenerated(invocationContext)) {
      logger.log(Level.SEVERE,() ->
          String.format("[%s] Failed to generate initial story. Aborting after StoryGenerator.",
              name()));
      return Flowable.empty(); // Stop further processing if no story
    }
      logger.log(Level.INFO, () ->
          String.format("[%s] Story state after generator: %s",
              name(), invocationContext.session().state().get("current_story")));
      return runStage(loopAgent, invocationContext, "CriticReviserLoop");
  });

  // Stage 3: Post-Processing (runs after critic-reviser loop completes)
  Flowable<Event> postProcessingFlow = Flowable.defer(() -> {
    logger.log(Level.INFO, () ->
        String.format("[%s] Story state after loop: %s",
            name(), invocationContext.session().state().get("current_story")));
    return runStage(sequentialAgent, invocationContext, "PostProcessing");
  });

  // Stage 4: Conditional Regeneration (runs after post-processing completes)
  Flowable<Event> conditionalRegenFlow = Flowable.defer(() -> {
    String toneCheckResult = (String) invocationContext.session().state().get("tone_check_result");
    logger.log(Level.INFO, () -> String.format("[%s] Tone check result: %s", name(), toneCheckResult));

    if ("negative".equalsIgnoreCase(toneCheckResult)) {
      logger.log(Level.INFO, () ->
          String.format("[%s] Tone is negative. Regenerating story...", name()));
      return runStage(storyGenerator, invocationContext, "StoryGenerator (Regen)");
    } else {
      logger.log(Level.INFO, () ->
          String.format("[%s] Tone is not negative. Keeping current story.", name()));
      return Flowable.empty(); // No regeneration needed
    }
  });

  return Flowable.concatArray(storyGenFlow, criticReviserFlow, postProcessingFlow, conditionalRegenFlow)
      .doOnComplete(() -> logger.log(Level.INFO, () -> String.format("[%s] Workflow finished.", name())));
}

// Helper method for a single agent run stage with logging
private Flowable<Event> runStage(BaseAgent agentToRun, InvocationContext ctx, String stageName) {
  logger.log(Level.INFO, () -> String.format("[%s] Running %s...", name(), stageName));
  return agentToRun
      .runAsync(ctx)
      .doOnNext(event ->
          logger.log(Level.INFO,() ->
              String.format("[%s] Event from %s: %s", name(), stageName, event.toJson())))
      .doOnError(err ->
          logger.log(Level.SEVERE,
              String.format("[%s] Error in %s", name(), stageName), err))
      .doOnComplete(() ->
          logger.log(Level.INFO, () ->
              String.format("[%s] %s finished.", name(), stageName)));
}

**Explanation of Logic:**

```
@Override
protected Flowable<Event> runAsyncImpl(InvocationContext invocationContext) {
  // Implements the custom orchestration logic for the story workflow.
  // Uses the instance attributes assigned by Pydantic (e.g., self.story_generator).
  logger.log(Level.INFO, () -> String.format("[%s] Starting story generation workflow.", name()));

  // Stage 1. Initial Story Generation
  Flowable<Event> storyGenFlow = runStage(storyGenerator, invocationContext, "StoryGenerator");

  // Stage 2: Critic-Reviser Loop (runs after story generation completes)
  Flowable<Event> criticReviserFlow = Flowable.defer(() -> {
    if (!isStoryGenerated(invocationContext)) {
      logger.log(Level.SEVERE,() ->
          String.format("[%s] Failed to generate initial story. Aborting after StoryGenerator.",
              name()));
      return Flowable.empty(); // Stop further processing if no story
    }
      logger.log(Level.INFO, () ->
          String.format("[%s] Story state after generator: %s",
              name(), invocationContext.session().state().get("current_story")));
      return runStage(loopAgent, invocationContext, "CriticReviserLoop");
  });

  // Stage 3: Post-Processing (runs after critic-reviser loop completes)
  Flowable<Event> postProcessingFlow = Flowable.defer(() -> {
    logger.log(Level.INFO, () ->
        String.format("[%s] Story state after loop: %s",
            name(), invocationContext.session().state().get("current_story")));
    return runStage(sequentialAgent, invocationContext, "PostProcessing");
  });

  // Stage 4: Conditional Regeneration (runs after post-processing completes)
  Flowable<Event> conditionalRegenFlow = Flowable.defer(() -> {
    String toneCheckResult = (String) invocationContext.session().state().get("tone_check_result");
    logger.log(Level.INFO, () -> String.format("[%s] Tone check result: %s", name(), toneCheckResult));

    if ("negative".equalsIgnoreCase(toneCheckResult)) {
      logger.log(Level.INFO, () ->
          String.format("[%s] Tone is negative. Regenerating story...", name()));
      return runStage(storyGenerator, invocationContext, "StoryGenerator (Regen)");
    } else {
      logger.log(Level.INFO, () ->
          String.format("[%s] Tone is not negative. Keeping current story.", name()));
      return Flowable.empty(); // No regeneration needed
    }
  });

  return Flowable.concatArray(storyGenFlow, criticReviserFlow, postProcessingFlow, conditionalRegenFlow)
      .doOnComplete(() -> logger.log(Level.INFO, () -> String.format("[%s] Workflow finished.", name())));
}

// Helper method for a single agent run stage with logging
private Flowable<Event> runStage(BaseAgent agentToRun, InvocationContext ctx, String stageName) {
  logger.log(Level.INFO, () -> String.format("[%s] Running %s...", name(), stageName));
  return agentToRun
      .runAsync(ctx)
      .doOnNext(event ->
          logger.log(Level.INFO,() ->
              String.format("[%s] Event from %s: %s", name(), stageName, event.toJson())))
      .doOnError(err ->
          logger.log(Level.SEVERE,
              String.format("[%s] Error in %s", name(), stageName), err))
      .doOnComplete(() ->
          logger.log(Level.INFO, () ->
              String.format("[%s] %s finished.", name(), stageName)));
}

```

@Override
protected Flowable<Event> runAsyncImpl(InvocationContext invocationContext) {
  // Implements the custom orchestration logic for the story workflow.
  // Uses the instance attributes assigned by Pydantic (e.g., self.story_generator).
  logger.log(Level.INFO, () -> String.format("[%s] Starting story generation workflow.", name()));

  // Stage 1. Initial Story Generation
  Flowable<Event> storyGenFlow = runStage(storyGenerator, invocationContext, "StoryGenerator");

  // Stage 2: Critic-Reviser Loop (runs after story generation completes)
  Flowable<Event> criticReviserFlow = Flowable.defer(() -> {
    if (!isStoryGenerated(invocationContext)) {
      logger.log(Level.SEVERE,() ->
          String.format("[%s] Failed to generate initial story. Aborting after StoryGenerator.",
              name()));
      return Flowable.empty(); // Stop further processing if no story
    }
      logger.log(Level.INFO, () ->
          String.format("[%s] Story state after generator: %s",
              name(), invocationContext.session().state().get("current_story")));
      return runStage(loopAgent, invocationContext, "CriticReviserLoop");
  });

  // Stage 3: Post-Processing (runs after critic-reviser loop completes)
  Flowable<Event> postProcessingFlow = Flowable.defer(() -> {
    logger.log(Level.INFO, () ->
        String.format("[%s] Story state after loop: %s",
            name(), invocationContext.session().state().get("current_story")));
    return runStage(sequentialAgent, invocationContext, "PostProcessing");
  });

  // Stage 4: Conditional Regeneration (runs after post-processing completes)
  Flowable<Event> conditionalRegenFlow = Flowable.defer(() -> {
    String toneCheckResult = (String) invocationContext.session().state().get("tone_check_result");
    logger.log(Level.INFO, () -> String.format("[%s] Tone check result: %s", name(), toneCheckResult));

    if ("negative".equalsIgnoreCase(toneCheckResult)) {
      logger.log(Level.INFO, () ->
          String.format("[%s] Tone is negative. Regenerating story...", name()));
      return runStage(storyGenerator, invocationContext, "StoryGenerator (Regen)");
    } else {
      logger.log(Level.INFO, () ->
          String.format("[%s] Tone is not negative. Keeping current story.", name()));
      return Flowable.empty(); // No regeneration needed
    }
  });

  return Flowable.concatArray(storyGenFlow, criticReviserFlow, postProcessingFlow, conditionalRegenFlow)
      .doOnComplete(() -> logger.log(Level.INFO, () -> String.format("[%s] Workflow finished.", name())));
}

// Helper method for a single agent run stage with logging
private Flowable<Event> runStage(BaseAgent agentToRun, InvocationContext ctx, String stageName) {
  logger.log(Level.INFO, () -> String.format("[%s] Running %s...", name(), stageName));
  return agentToRun
      .runAsync(ctx)
      .doOnNext(event ->
          logger.log(Level.INFO,() ->
              String.format("[%s] Event from %s: %s", name(), stageName, event.toJson())))
      .doOnError(err ->
          logger.log(Level.SEVERE,
              String.format("[%s] Error in %s", name(), stageName), err))
      .doOnComplete(() ->
          logger.log(Level.INFO, () ->
              String.format("[%s] %s finished.", name(), stageName)));
}

1. The initial `storyGenerator.runAsync(invocationContext)` Flowable is executed. Its output is expected to be in `invocationContext.session().state().get("current_story")`.
1. The `loopAgent's` Flowable runs next (due to `Flowable.concatArray` and `Flowable.defer`). The LoopAgent internally calls the `critic` and `reviser` sub-agents sequentially for up to `maxIterations`. They read/write `current_story` and `criticism` from/to the state.
1. Then, the `sequentialAgent's` Flowable executes. It calls the `grammar_check` then `tone_check`, reading `current_story` and writing `grammar_suggestions` and `tone_check_result` to the state.
1. **Custom Part:** After the sequentialAgent completes, logic within a `Flowable.defer` checks the "tone_check_result" from `invocationContext.session().state()`. If it's "negative", the `storyGenerator` Flowable is *conditionally concatenated* and executed again, overwriting "current_story". Otherwise, an empty Flowable is used, and the overall workflow proceeds to completion.

`storyGenerator.runAsync(invocationContext)`

`invocationContext.session().state().get("current_story")`

`loopAgent's`

`Flowable.concatArray`

`Flowable.defer`

`critic`

`reviser`

`maxIterations`

`current_story`

`criticism`

`sequentialAgent's`

`grammar_check`

`tone_check`

`current_story`

`grammar_suggestions`

`tone_check_result`

`Flowable.defer`

`invocationContext.session().state()`

`storyGenerator`

### Part 3: Defining the LLM Sub-Agents

These are standard `LlmAgent` definitions, responsible for specific tasks. Their `output key` parameter is crucial for placing results into the `session.state` where other agents or the custom orchestrator can access them.

`LlmAgent`

`output key`

`session.state`

Direct State Injection in Instructions

Notice the `story_generator`'s instruction. The `{var}` syntax is a placeholder. Before the instruction is sent to the LLM, the ADK framework automatically replaces (Example:`{topic}`) with the value of `session.state['topic']`. This is the recommended way to provide context to an agent, using templating in the instructions. For more details, see the [State documentation](../../sessions/state/#accessing-session-state-in-agent-instructions).

`story_generator`

`{var}`

`{topic}`

`session.state['topic']`

```
GEMINI_2_FLASH = "gemini-2.0-flash" # Define model constant
# --- Define the individual LLM agents ---
story_generator = LlmAgent(
    name="StoryGenerator",
    model=GEMINI_2_FLASH,
    instruction="""You are a story writer. Write a short story (around 100 words), on the following topic: {topic}""",
    input_schema=None,
    output_key="current_story",  # Key for storing output in session state
)

critic = LlmAgent(
    name="Critic",
    model=GEMINI_2_FLASH,
    instruction="""You are a story critic. Review the story provided: {{current_story}}. Provide 1-2 sentences of constructive criticism
on how to improve it. Focus on plot or character.""",
    input_schema=None,
    output_key="criticism",  # Key for storing criticism in session state
)

reviser = LlmAgent(
    name="Reviser",
    model=GEMINI_2_FLASH,
    instruction="""You are a story reviser. Revise the story provided: {{current_story}}, based on the criticism in
{{criticism}}. Output only the revised story.""",
    input_schema=None,
    output_key="current_story",  # Overwrites the original story
)

grammar_check = LlmAgent(
    name="GrammarCheck",
    model=GEMINI_2_FLASH,
    instruction="""You are a grammar checker. Check the grammar of the story provided: {current_story}. Output only the suggested
corrections as a list, or output 'Grammar is good!' if there are no errors.""",
    input_schema=None,
    output_key="grammar_suggestions",
)

tone_check = LlmAgent(
    name="ToneCheck",
    model=GEMINI_2_FLASH,
    instruction="""You are a tone analyzer. Analyze the tone of the story provided: {current_story}. Output only one word: 'positive' if
the tone is generally positive, 'negative' if the tone is generally negative, or 'neutral'
otherwise.""",
    input_schema=None,
    output_key="tone_check_result", # This agent's output determines the conditional flow
)

```

GEMINI_2_FLASH = "gemini-2.0-flash" # Define model constant
# --- Define the individual LLM agents ---
story_generator = LlmAgent(
    name="StoryGenerator",
    model=GEMINI_2_FLASH,
    instruction="""You are a story writer. Write a short story (around 100 words), on the following topic: {topic}""",
    input_schema=None,
    output_key="current_story",  # Key for storing output in session state
)

critic = LlmAgent(
    name="Critic",
    model=GEMINI_2_FLASH,
    instruction="""You are a story critic. Review the story provided: {{current_story}}. Provide 1-2 sentences of constructive criticism
on how to improve it. Focus on plot or character.""",
    input_schema=None,
    output_key="criticism",  # Key for storing criticism in session state
)

reviser = LlmAgent(
    name="Reviser",
    model=GEMINI_2_FLASH,
    instruction="""You are a story reviser. Revise the story provided: {{current_story}}, based on the criticism in
{{criticism}}. Output only the revised story.""",
    input_schema=None,
    output_key="current_story",  # Overwrites the original story
)

grammar_check = LlmAgent(
    name="GrammarCheck",
    model=GEMINI_2_FLASH,
    instruction="""You are a grammar checker. Check the grammar of the story provided: {current_story}. Output only the suggested
corrections as a list, or output 'Grammar is good!' if there are no errors.""",
    input_schema=None,
    output_key="grammar_suggestions",
)

tone_check = LlmAgent(
    name="ToneCheck",
    model=GEMINI_2_FLASH,
    instruction="""You are a tone analyzer. Analyze the tone of the story provided: {current_story}. Output only one word: 'positive' if
the tone is generally positive, 'negative' if the tone is generally negative, or 'neutral'
otherwise.""",
    input_schema=None,
    output_key="tone_check_result", # This agent's output determines the conditional flow
)

```
// --- Define the individual LLM agents ---
LlmAgent storyGenerator =
    LlmAgent.builder()
        .name("StoryGenerator")
        .model(MODEL_NAME)
        .description("Generates the initial story.")
        .instruction(
            """
          You are a story writer. Write a short story (around 100 words) about a cat,
          based on the topic: {topic}
          """)
        .inputSchema(null)
        .outputKey("current_story") // Key for storing output in session state
        .build();

LlmAgent critic =
    LlmAgent.builder()
        .name("Critic")
        .model(MODEL_NAME)
        .description("Critiques the story.")
        .instruction(
            """
          You are a story critic. Review the story: {current_story}. Provide 1-2 sentences of constructive criticism
          on how to improve it. Focus on plot or character.
          """)
        .inputSchema(null)
        .outputKey("criticism") // Key for storing criticism in session state
        .build();

LlmAgent reviser =
    LlmAgent.builder()
        .name("Reviser")
        .model(MODEL_NAME)
        .description("Revises the story based on criticism.")
        .instruction(
            """
          You are a story reviser. Revise the story: {current_story}, based on the criticism: {criticism}. Output only the revised story.
          """)
        .inputSchema(null)
        .outputKey("current_story") // Overwrites the original story
        .build();

LlmAgent grammarCheck =
    LlmAgent.builder()
        .name("GrammarCheck")
        .model(MODEL_NAME)
        .description("Checks grammar and suggests corrections.")
        .instruction(
            """
           You are a grammar checker. Check the grammar of the story: {current_story}. Output only the suggested
           corrections as a list, or output 'Grammar is good!' if there are no errors.
           """)
        .outputKey("grammar_suggestions")
        .build();

LlmAgent toneCheck =
    LlmAgent.builder()
        .name("ToneCheck")
        .model(MODEL_NAME)
        .description("Analyzes the tone of the story.")
        .instruction(
            """
          You are a tone analyzer. Analyze the tone of the story: {current_story}. Output only one word: 'positive' if
          the tone is generally positive, 'negative' if the tone is generally negative, or 'neutral'
          otherwise.
          """)
        .outputKey("tone_check_result") // This agent's output determines the conditional flow
        .build();

LoopAgent loopAgent =
    LoopAgent.builder()
        .name("CriticReviserLoop")
        .description("Iteratively critiques and revises the story.")
        .subAgents(critic, reviser)
        .maxIterations(2)
        .build();

SequentialAgent sequentialAgent =
    SequentialAgent.builder()
        .name("PostProcessing")
        .description("Performs grammar and tone checks sequentially.")
        .subAgents(grammarCheck, toneCheck)
        .build();

```

// --- Define the individual LLM agents ---
LlmAgent storyGenerator =
    LlmAgent.builder()
        .name("StoryGenerator")
        .model(MODEL_NAME)
        .description("Generates the initial story.")
        .instruction(
            """
          You are a story writer. Write a short story (around 100 words) about a cat,
          based on the topic: {topic}
          """)
        .inputSchema(null)
        .outputKey("current_story") // Key for storing output in session state
        .build();

LlmAgent critic =
    LlmAgent.builder()
        .name("Critic")
        .model(MODEL_NAME)
        .description("Critiques the story.")
        .instruction(
            """
          You are a story critic. Review the story: {current_story}. Provide 1-2 sentences of constructive criticism
          on how to improve it. Focus on plot or character.
          """)
        .inputSchema(null)
        .outputKey("criticism") // Key for storing criticism in session state
        .build();

LlmAgent reviser =
    LlmAgent.builder()
        .name("Reviser")
        .model(MODEL_NAME)
        .description("Revises the story based on criticism.")
        .instruction(
            """
          You are a story reviser. Revise the story: {current_story}, based on the criticism: {criticism}. Output only the revised story.
          """)
        .inputSchema(null)
        .outputKey("current_story") // Overwrites the original story
        .build();

LlmAgent grammarCheck =
    LlmAgent.builder()
        .name("GrammarCheck")
        .model(MODEL_NAME)
        .description("Checks grammar and suggests corrections.")
        .instruction(
            """
           You are a grammar checker. Check the grammar of the story: {current_story}. Output only the suggested
           corrections as a list, or output 'Grammar is good!' if there are no errors.
           """)
        .outputKey("grammar_suggestions")
        .build();

LlmAgent toneCheck =
    LlmAgent.builder()
        .name("ToneCheck")
        .model(MODEL_NAME)
        .description("Analyzes the tone of the story.")
        .instruction(
            """
          You are a tone analyzer. Analyze the tone of the story: {current_story}. Output only one word: 'positive' if
          the tone is generally positive, 'negative' if the tone is generally negative, or 'neutral'
          otherwise.
          """)
        .outputKey("tone_check_result") // This agent's output determines the conditional flow
        .build();

LoopAgent loopAgent =
    LoopAgent.builder()
        .name("CriticReviserLoop")
        .description("Iteratively critiques and revises the story.")
        .subAgents(critic, reviser)
        .maxIterations(2)
        .build();

SequentialAgent sequentialAgent =
    SequentialAgent.builder()
        .name("PostProcessing")
        .description("Performs grammar and tone checks sequentially.")
        .subAgents(grammarCheck, toneCheck)
        .build();

### Part 4: Instantiating and Running the custom agent

Finally, you instantiate your `StoryFlowAgent` and use the `Runner` as usual.

`StoryFlowAgent`

`Runner`

```
# --- Create the custom agent instance ---
story_flow_agent = StoryFlowAgent(
    name="StoryFlowAgent",
    story_generator=story_generator,
    critic=critic,
    reviser=reviser,
    grammar_check=grammar_check,
    tone_check=tone_check,
)

INITIAL_STATE = {"topic": "a brave kitten exploring a haunted house"}

# --- Setup Runner and Session ---
async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID, state=INITIAL_STATE)
    logger.info(f"Initial session state: {session.state}")
    runner = Runner(
        agent=story_flow_agent, # Pass the custom orchestrator agent
        app_name=APP_NAME,
        session_service=session_service
    )
    return session_service, runner

# --- Function to Interact with the Agent ---
async def call_agent_async(user_input_topic: str):
    """
    Sends a new topic to the agent (overwriting the initial one if needed)
    and runs the workflow.
    """

    session_service, runner = await setup_session_and_runner()

    current_session = await session_service.get_session(app_name=APP_NAME, 
                                                  user_id=USER_ID, 
                                                  session_id=SESSION_ID)
    if not current_session:
        logger.error("Session not found!")
        return

    current_session.state["topic"] = user_input_topic
    logger.info(f"Updated session state topic to: {user_input_topic}")

    content = types.Content(role='user', parts=[types.Part(text=f"Generate a story about: {user_input_topic}")])
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    final_response = "No final response captured."
    async for event in events:
        if event.is_final_response() and event.content and event.content.parts:
            logger.info(f"Potential final response from [{event.author}]: {event.content.parts[0].text}")
            final_response = event.content.parts[0].text

    print("\n--- Agent Interaction Result ---")
    print("Agent Final Response: ", final_response)

    final_session = await session_service.get_session(app_name=APP_NAME, 
                                                user_id=USER_ID, 
                                                session_id=SESSION_ID)
    print("Final Session State:")
    import json
    print(json.dumps(final_session.state, indent=2))
    print("-------------------------------\n")

# --- Run the Agent ---
# Note: In Colab, you can directly use 'await' at the top level.
# If running this code as a standalone Python script, you'll need to use asyncio.run() or manage the event loop.
await call_agent_async("a lonely robot finding a friend in a junkyard")

```

# --- Create the custom agent instance ---
story_flow_agent = StoryFlowAgent(
    name="StoryFlowAgent",
    story_generator=story_generator,
    critic=critic,
    reviser=reviser,
    grammar_check=grammar_check,
    tone_check=tone_check,
)

INITIAL_STATE = {"topic": "a brave kitten exploring a haunted house"}

# --- Setup Runner and Session ---
async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID, state=INITIAL_STATE)
    logger.info(f"Initial session state: {session.state}")
    runner = Runner(
        agent=story_flow_agent, # Pass the custom orchestrator agent
        app_name=APP_NAME,
        session_service=session_service
    )
    return session_service, runner

# --- Function to Interact with the Agent ---
async def call_agent_async(user_input_topic: str):
    """
    Sends a new topic to the agent (overwriting the initial one if needed)
    and runs the workflow.
    """

    session_service, runner = await setup_session_and_runner()

    current_session = await session_service.get_session(app_name=APP_NAME, 
                                                  user_id=USER_ID, 
                                                  session_id=SESSION_ID)
    if not current_session:
        logger.error("Session not found!")
        return

    current_session.state["topic"] = user_input_topic
    logger.info(f"Updated session state topic to: {user_input_topic}")

    content = types.Content(role='user', parts=[types.Part(text=f"Generate a story about: {user_input_topic}")])
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    final_response = "No final response captured."
    async for event in events:
        if event.is_final_response() and event.content and event.content.parts:
            logger.info(f"Potential final response from [{event.author}]: {event.content.parts[0].text}")
            final_response = event.content.parts[0].text

    print("\n--- Agent Interaction Result ---")
    print("Agent Final Response: ", final_response)

    final_session = await session_service.get_session(app_name=APP_NAME, 
                                                user_id=USER_ID, 
                                                session_id=SESSION_ID)
    print("Final Session State:")
    import json
    print(json.dumps(final_session.state, indent=2))
    print("-------------------------------\n")

# --- Run the Agent ---
# Note: In Colab, you can directly use 'await' at the top level.
# If running this code as a standalone Python script, you'll need to use asyncio.run() or manage the event loop.
await call_agent_async("a lonely robot finding a friend in a junkyard")

```
// --- Function to Interact with the Agent ---
// Sends a new topic to the agent (overwriting the initial one if needed)
// and runs the workflow.
public static void runAgent(StoryFlowAgentExample agent, String userTopic) {
  // --- Setup Runner and Session ---
  InMemoryRunner runner = new InMemoryRunner(agent);

  Map<String, Object> initialState = new HashMap<>();
  initialState.put("topic", "a brave kitten exploring a haunted house");

  Session session =
      runner
          .sessionService()
          .createSession(APP_NAME, USER_ID, new ConcurrentHashMap<>(initialState), SESSION_ID)
          .blockingGet();
  logger.log(Level.INFO, () -> String.format("Initial session state: %s", session.state()));

  session.state().put("topic", userTopic); // Update the state in the retrieved session
  logger.log(Level.INFO, () -> String.format("Updated session state topic to: %s", userTopic));

  Content userMessage = Content.fromParts(Part.fromText("Generate a story about: " + userTopic));
  // Use the modified session object for the run
  Flowable<Event> eventStream = runner.runAsync(USER_ID, session.id(), userMessage);

  final String[] finalResponse = {"No final response captured."};
  eventStream.blockingForEach(
      event -> {
        if (event.finalResponse() && event.content().isPresent()) {
          String author = event.author() != null ? event.author() : "UNKNOWN_AUTHOR";
          Optional<String> textOpt =
              event
                  .content()
                  .flatMap(Content::parts)
                  .filter(parts -> !parts.isEmpty())
                  .map(parts -> parts.get(0).text().orElse(""));

          logger.log(Level.INFO, () ->
              String.format("Potential final response from [%s]: %s", author, textOpt.orElse("N/A")));
          textOpt.ifPresent(text -> finalResponse[0] = text);
        }
      });

  System.out.println("\n--- Agent Interaction Result ---");
  System.out.println("Agent Final Response: " + finalResponse[0]);

  // Retrieve session again to see the final state after the run
  Session finalSession =
      runner
          .sessionService()
          .getSession(APP_NAME, USER_ID, SESSION_ID, Optional.empty())
          .blockingGet();

  assert finalSession != null;
  System.out.println("Final Session State:" + finalSession.state());
  System.out.println("-------------------------------\n");
}

```

// --- Function to Interact with the Agent ---
// Sends a new topic to the agent (overwriting the initial one if needed)
// and runs the workflow.
public static void runAgent(StoryFlowAgentExample agent, String userTopic) {
  // --- Setup Runner and Session ---
  InMemoryRunner runner = new InMemoryRunner(agent);

  Map<String, Object> initialState = new HashMap<>();
  initialState.put("topic", "a brave kitten exploring a haunted house");

  Session session =
      runner
          .sessionService()
          .createSession(APP_NAME, USER_ID, new ConcurrentHashMap<>(initialState), SESSION_ID)
          .blockingGet();
  logger.log(Level.INFO, () -> String.format("Initial session state: %s", session.state()));

  session.state().put("topic", userTopic); // Update the state in the retrieved session
  logger.log(Level.INFO, () -> String.format("Updated session state topic to: %s", userTopic));

  Content userMessage = Content.fromParts(Part.fromText("Generate a story about: " + userTopic));
  // Use the modified session object for the run
  Flowable<Event> eventStream = runner.runAsync(USER_ID, session.id(), userMessage);

  final String[] finalResponse = {"No final response captured."};
  eventStream.blockingForEach(
      event -> {
        if (event.finalResponse() && event.content().isPresent()) {
          String author = event.author() != null ? event.author() : "UNKNOWN_AUTHOR";
          Optional<String> textOpt =
              event
                  .content()
                  .flatMap(Content::parts)
                  .filter(parts -> !parts.isEmpty())
                  .map(parts -> parts.get(0).text().orElse(""));

          logger.log(Level.INFO, () ->
              String.format("Potential final response from [%s]: %s", author, textOpt.orElse("N/A")));
          textOpt.ifPresent(text -> finalResponse[0] = text);
        }
      });

  System.out.println("\n--- Agent Interaction Result ---");
  System.out.println("Agent Final Response: " + finalResponse[0]);

  // Retrieve session again to see the final state after the run
  Session finalSession =
      runner
          .sessionService()
          .getSession(APP_NAME, USER_ID, SESSION_ID, Optional.empty())
          .blockingGet();

  assert finalSession != null;
  System.out.println("Final Session State:" + finalSession.state());
  System.out.println("-------------------------------\n");
}

*(Note: The full runnable code, including imports and execution logic, can be found linked below.)*

## Full Code Example

```
# Full runnable code for the StoryFlowAgent example
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
from typing import AsyncGenerator
from typing_extensions import override

from google.adk.agents import LlmAgent, BaseAgent, LoopAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.events import Event
from pydantic import BaseModel, Field

# --- Constants ---
APP_NAME = "story_app"
USER_ID = "12345"
SESSION_ID = "123344"
GEMINI_2_FLASH = "gemini-2.0-flash"

# --- Configure Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- Custom Orchestrator Agent ---
class StoryFlowAgent(BaseAgent):
    """
    Custom agent for a story generation and refinement workflow.

    This agent orchestrates a sequence of LLM agents to generate a story,
    critique it, revise it, check grammar and tone, and potentially
    regenerate the story if the tone is negative.
    """

    # --- Field Declarations for Pydantic ---
    # Declare the agents passed during initialization as class attributes with type hints
    story_generator: LlmAgent
    critic: LlmAgent
    reviser: LlmAgent
    grammar_check: LlmAgent
    tone_check: LlmAgent

    loop_agent: LoopAgent
    sequential_agent: SequentialAgent

    # model_config allows setting Pydantic configurations if needed, e.g., arbitrary_types_allowed
    model_config = {"arbitrary_types_allowed": True}

    def __init__(
        self,
        name: str,
        story_generator: LlmAgent,
        critic: LlmAgent,
        reviser: LlmAgent,
        grammar_check: LlmAgent,
        tone_check: LlmAgent,
    ):
        """
        Initializes the StoryFlowAgent.

        Args:
            name: The name of the agent.
            story_generator: An LlmAgent to generate the initial story.
            critic: An LlmAgent to critique the story.
            reviser: An LlmAgent to revise the story based on criticism.
            grammar_check: An LlmAgent to check the grammar.
            tone_check: An LlmAgent to analyze the tone.
        """
        # Create internal agents *before* calling super().__init__
        loop_agent = LoopAgent(
            name="CriticReviserLoop", sub_agents=[critic, reviser], max_iterations=2
        )
        sequential_agent = SequentialAgent(
            name="PostProcessing", sub_agents=[grammar_check, tone_check]
        )

        # Define the sub_agents list for the framework
        sub_agents_list = [
            story_generator,
            loop_agent,
            sequential_agent,
        ]

        # Pydantic will validate and assign them based on the class annotations.
        super().__init__(
            name=name,
            story_generator=story_generator,
            critic=critic,
            reviser=reviser,
            grammar_check=grammar_check,
            tone_check=tone_check,
            loop_agent=loop_agent,
            sequential_agent=sequential_agent,
            sub_agents=sub_agents_list, # Pass the sub_agents list directly
        )

    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """
        Implements the custom orchestration logic for the story workflow.
        Uses the instance attributes assigned by Pydantic (e.g., self.story_generator).
        """
        logger.info(f"[{self.name}] Starting story generation workflow.")

        # 1. Initial Story Generation
        logger.info(f"[{self.name}] Running StoryGenerator...")
        async for event in self.story_generator.run_async(ctx):
            logger.info(f"[{self.name}] Event from StoryGenerator: {event.model_dump_json(indent=2, exclude_none=True)}")
            yield event

        # Check if story was generated before proceeding
        if "current_story" not in ctx.session.state or not ctx.session.state["current_story"]:
             logger.error(f"[{self.name}] Failed to generate initial story. Aborting workflow.")
             return # Stop processing if initial story failed

        logger.info(f"[{self.name}] Story state after generator: {ctx.session.state.get('current_story')}")


        # 2. Critic-Reviser Loop
        logger.info(f"[{self.name}] Running CriticReviserLoop...")
        # Use the loop_agent instance attribute assigned during init
        async for event in self.loop_agent.run_async(ctx):
            logger.info(f"[{self.name}] Event from CriticReviserLoop: {event.model_dump_json(indent=2, exclude_none=True)}")
            yield event

        logger.info(f"[{self.name}] Story state after loop: {ctx.session.state.get('current_story')}")

        # 3. Sequential Post-Processing (Grammar and Tone Check)
        logger.info(f"[{self.name}] Running PostProcessing...")
        # Use the sequential_agent instance attribute assigned during init
        async for event in self.sequential_agent.run_async(ctx):
            logger.info(f"[{self.name}] Event from PostProcessing: {event.model_dump_json(indent=2, exclude_none=True)}")
            yield event

        # 4. Tone-Based Conditional Logic
        tone_check_result = ctx.session.state.get("tone_check_result")
        logger.info(f"[{self.name}] Tone check result: {tone_check_result}")

        if tone_check_result == "negative":
            logger.info(f"[{self.name}] Tone is negative. Regenerating story...")
            async for event in self.story_generator.run_async(ctx):
                logger.info(f"[{self.name}] Event from StoryGenerator (Regen): {event.model_dump_json(indent=2, exclude_none=True)}")
                yield event
        else:
            logger.info(f"[{self.name}] Tone is not negative. Keeping current story.")
            pass

        logger.info(f"[{self.name}] Workflow finished.")

# --- Define the individual LLM agents ---
story_generator = LlmAgent(
    name="StoryGenerator",
    model=GEMINI_2_FLASH,
    instruction="""You are a story writer. Write a short story (around 100 words), on the following topic: {topic}""",
    input_schema=None,
    output_key="current_story",  # Key for storing output in session state
)

critic = LlmAgent(
    name="Critic",
    model=GEMINI_2_FLASH,
    instruction="""You are a story critic. Review the story provided: {{current_story}}. Provide 1-2 sentences of constructive criticism
on how to improve it. Focus on plot or character.""",
    input_schema=None,
    output_key="criticism",  # Key for storing criticism in session state
)

reviser = LlmAgent(
    name="Reviser",
    model=GEMINI_2_FLASH,
    instruction="""You are a story reviser. Revise the story provided: {{current_story}}, based on the criticism in
{{criticism}}. Output only the revised story.""",
    input_schema=None,
    output_key="current_story",  # Overwrites the original story
)

grammar_check = LlmAgent(
    name="GrammarCheck",
    model=GEMINI_2_FLASH,
    instruction="""You are a grammar checker. Check the grammar of the story provided: {current_story}. Output only the suggested
corrections as a list, or output 'Grammar is good!' if there are no errors.""",
    input_schema=None,
    output_key="grammar_suggestions",
)

tone_check = LlmAgent(
    name="ToneCheck",
    model=GEMINI_2_FLASH,
    instruction="""You are a tone analyzer. Analyze the tone of the story provided: {current_story}. Output only one word: 'positive' if
the tone is generally positive, 'negative' if the tone is generally negative, or 'neutral'
otherwise.""",
    input_schema=None,
    output_key="tone_check_result", # This agent's output determines the conditional flow
)

# --- Create the custom agent instance ---
story_flow_agent = StoryFlowAgent(
    name="StoryFlowAgent",
    story_generator=story_generator,
    critic=critic,
    reviser=reviser,
    grammar_check=grammar_check,
    tone_check=tone_check,
)

INITIAL_STATE = {"topic": "a brave kitten exploring a haunted house"}

# --- Setup Runner and Session ---
async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID, state=INITIAL_STATE)
    logger.info(f"Initial session state: {session.state}")
    runner = Runner(
        agent=story_flow_agent, # Pass the custom orchestrator agent
        app_name=APP_NAME,
        session_service=session_service
    )
    return session_service, runner

# --- Function to Interact with the Agent ---
async def call_agent_async(user_input_topic: str):
    """
    Sends a new topic to the agent (overwriting the initial one if needed)
    and runs the workflow.
    """

    session_service, runner = await setup_session_and_runner()

    current_session = await session_service.get_session(app_name=APP_NAME, 
                                                  user_id=USER_ID, 
                                                  session_id=SESSION_ID)
    if not current_session:
        logger.error("Session not found!")
        return

    current_session.state["topic"] = user_input_topic
    logger.info(f"Updated session state topic to: {user_input_topic}")

    content = types.Content(role='user', parts=[types.Part(text=f"Generate a story about: {user_input_topic}")])
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    final_response = "No final response captured."
    async for event in events:
        if event.is_final_response() and event.content and event.content.parts:
            logger.info(f"Potential final response from [{event.author}]: {event.content.parts[0].text}")
            final_response = event.content.parts[0].text

    print("\n--- Agent Interaction Result ---")
    print("Agent Final Response: ", final_response)

    final_session = await session_service.get_session(app_name=APP_NAME, 
                                                user_id=USER_ID, 
                                                session_id=SESSION_ID)
    print("Final Session State:")
    import json
    print(json.dumps(final_session.state, indent=2))
    print("-------------------------------\n")

# --- Run the Agent ---
# Note: In Colab, you can directly use 'await' at the top level.
# If running this code as a standalone Python script, you'll need to use asyncio.run() or manage the event loop.
await call_agent_async("a lonely robot finding a friend in a junkyard")

```

# Full runnable code for the StoryFlowAgent example
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
from typing import AsyncGenerator
from typing_extensions import override

from google.adk.agents import LlmAgent, BaseAgent, LoopAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.events import Event
from pydantic import BaseModel, Field

# --- Constants ---
APP_NAME = "story_app"
USER_ID = "12345"
SESSION_ID = "123344"
GEMINI_2_FLASH = "gemini-2.0-flash"

# --- Configure Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- Custom Orchestrator Agent ---
class StoryFlowAgent(BaseAgent):
    """
    Custom agent for a story generation and refinement workflow.

    This agent orchestrates a sequence of LLM agents to generate a story,
    critique it, revise it, check grammar and tone, and potentially
    regenerate the story if the tone is negative.
    """

    # --- Field Declarations for Pydantic ---
    # Declare the agents passed during initialization as class attributes with type hints
    story_generator: LlmAgent
    critic: LlmAgent
    reviser: LlmAgent
    grammar_check: LlmAgent
    tone_check: LlmAgent

    loop_agent: LoopAgent
    sequential_agent: SequentialAgent

    # model_config allows setting Pydantic configurations if needed, e.g., arbitrary_types_allowed
    model_config = {"arbitrary_types_allowed": True}

    def __init__(
        self,
        name: str,
        story_generator: LlmAgent,
        critic: LlmAgent,
        reviser: LlmAgent,
        grammar_check: LlmAgent,
        tone_check: LlmAgent,
    ):
        """
        Initializes the StoryFlowAgent.

        Args:
            name: The name of the agent.
            story_generator: An LlmAgent to generate the initial story.
            critic: An LlmAgent to critique the story.
            reviser: An LlmAgent to revise the story based on criticism.
            grammar_check: An LlmAgent to check the grammar.
            tone_check: An LlmAgent to analyze the tone.
        """
        # Create internal agents *before* calling super().__init__
        loop_agent = LoopAgent(
            name="CriticReviserLoop", sub_agents=[critic, reviser], max_iterations=2
        )
        sequential_agent = SequentialAgent(
            name="PostProcessing", sub_agents=[grammar_check, tone_check]
        )

        # Define the sub_agents list for the framework
        sub_agents_list = [
            story_generator,
            loop_agent,
            sequential_agent,
        ]

        # Pydantic will validate and assign them based on the class annotations.
        super().__init__(
            name=name,
            story_generator=story_generator,
            critic=critic,
            reviser=reviser,
            grammar_check=grammar_check,
            tone_check=tone_check,
            loop_agent=loop_agent,
            sequential_agent=sequential_agent,
            sub_agents=sub_agents_list, # Pass the sub_agents list directly
        )

    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """
        Implements the custom orchestration logic for the story workflow.
        Uses the instance attributes assigned by Pydantic (e.g., self.story_generator).
        """
        logger.info(f"[{self.name}] Starting story generation workflow.")

        # 1. Initial Story Generation
        logger.info(f"[{self.name}] Running StoryGenerator...")
        async for event in self.story_generator.run_async(ctx):
            logger.info(f"[{self.name}] Event from StoryGenerator: {event.model_dump_json(indent=2, exclude_none=True)}")
            yield event

        # Check if story was generated before proceeding
        if "current_story" not in ctx.session.state or not ctx.session.state["current_story"]:
             logger.error(f"[{self.name}] Failed to generate initial story. Aborting workflow.")
             return # Stop processing if initial story failed

        logger.info(f"[{self.name}] Story state after generator: {ctx.session.state.get('current_story')}")


        # 2. Critic-Reviser Loop
        logger.info(f"[{self.name}] Running CriticReviserLoop...")
        # Use the loop_agent instance attribute assigned during init
        async for event in self.loop_agent.run_async(ctx):
            logger.info(f"[{self.name}] Event from CriticReviserLoop: {event.model_dump_json(indent=2, exclude_none=True)}")
            yield event

        logger.info(f"[{self.name}] Story state after loop: {ctx.session.state.get('current_story')}")

        # 3. Sequential Post-Processing (Grammar and Tone Check)
        logger.info(f"[{self.name}] Running PostProcessing...")
        # Use the sequential_agent instance attribute assigned during init
        async for event in self.sequential_agent.run_async(ctx):
            logger.info(f"[{self.name}] Event from PostProcessing: {event.model_dump_json(indent=2, exclude_none=True)}")
            yield event

        # 4. Tone-Based Conditional Logic
        tone_check_result = ctx.session.state.get("tone_check_result")
        logger.info(f"[{self.name}] Tone check result: {tone_check_result}")

        if tone_check_result == "negative":
            logger.info(f"[{self.name}] Tone is negative. Regenerating story...")
            async for event in self.story_generator.run_async(ctx):
                logger.info(f"[{self.name}] Event from StoryGenerator (Regen): {event.model_dump_json(indent=2, exclude_none=True)}")
                yield event
        else:
            logger.info(f"[{self.name}] Tone is not negative. Keeping current story.")
            pass

        logger.info(f"[{self.name}] Workflow finished.")

# --- Define the individual LLM agents ---
story_generator = LlmAgent(
    name="StoryGenerator",
    model=GEMINI_2_FLASH,
    instruction="""You are a story writer. Write a short story (around 100 words), on the following topic: {topic}""",
    input_schema=None,
    output_key="current_story",  # Key for storing output in session state
)

critic = LlmAgent(
    name="Critic",
    model=GEMINI_2_FLASH,
    instruction="""You are a story critic. Review the story provided: {{current_story}}. Provide 1-2 sentences of constructive criticism
on how to improve it. Focus on plot or character.""",
    input_schema=None,
    output_key="criticism",  # Key for storing criticism in session state
)

reviser = LlmAgent(
    name="Reviser",
    model=GEMINI_2_FLASH,
    instruction="""You are a story reviser. Revise the story provided: {{current_story}}, based on the criticism in
{{criticism}}. Output only the revised story.""",
    input_schema=None,
    output_key="current_story",  # Overwrites the original story
)

grammar_check = LlmAgent(
    name="GrammarCheck",
    model=GEMINI_2_FLASH,
    instruction="""You are a grammar checker. Check the grammar of the story provided: {current_story}. Output only the suggested
corrections as a list, or output 'Grammar is good!' if there are no errors.""",
    input_schema=None,
    output_key="grammar_suggestions",
)

tone_check = LlmAgent(
    name="ToneCheck",
    model=GEMINI_2_FLASH,
    instruction="""You are a tone analyzer. Analyze the tone of the story provided: {current_story}. Output only one word: 'positive' if
the tone is generally positive, 'negative' if the tone is generally negative, or 'neutral'
otherwise.""",
    input_schema=None,
    output_key="tone_check_result", # This agent's output determines the conditional flow
)

# --- Create the custom agent instance ---
story_flow_agent = StoryFlowAgent(
    name="StoryFlowAgent",
    story_generator=story_generator,
    critic=critic,
    reviser=reviser,
    grammar_check=grammar_check,
    tone_check=tone_check,
)

INITIAL_STATE = {"topic": "a brave kitten exploring a haunted house"}

# --- Setup Runner and Session ---
async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID, state=INITIAL_STATE)
    logger.info(f"Initial session state: {session.state}")
    runner = Runner(
        agent=story_flow_agent, # Pass the custom orchestrator agent
        app_name=APP_NAME,
        session_service=session_service
    )
    return session_service, runner

# --- Function to Interact with the Agent ---
async def call_agent_async(user_input_topic: str):
    """
    Sends a new topic to the agent (overwriting the initial one if needed)
    and runs the workflow.
    """

    session_service, runner = await setup_session_and_runner()

    current_session = await session_service.get_session(app_name=APP_NAME, 
                                                  user_id=USER_ID, 
                                                  session_id=SESSION_ID)
    if not current_session:
        logger.error("Session not found!")
        return

    current_session.state["topic"] = user_input_topic
    logger.info(f"Updated session state topic to: {user_input_topic}")

    content = types.Content(role='user', parts=[types.Part(text=f"Generate a story about: {user_input_topic}")])
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    final_response = "No final response captured."
    async for event in events:
        if event.is_final_response() and event.content and event.content.parts:
            logger.info(f"Potential final response from [{event.author}]: {event.content.parts[0].text}")
            final_response = event.content.parts[0].text

    print("\n--- Agent Interaction Result ---")
    print("Agent Final Response: ", final_response)

    final_session = await session_service.get_session(app_name=APP_NAME, 
                                                user_id=USER_ID, 
                                                session_id=SESSION_ID)
    print("Final Session State:")
    import json
    print(json.dumps(final_session.state, indent=2))
    print("-------------------------------\n")

# --- Run the Agent ---
# Note: In Colab, you can directly use 'await' at the top level.
# If running this code as a standalone Python script, you'll need to use asyncio.run() or manage the event loop.
await call_agent_async("a lonely robot finding a friend in a junkyard")

```
# Full runnable code for the StoryFlowAgent example

import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.BaseAgent;
import com.google.adk.agents.InvocationContext;
import com.google.adk.agents.LoopAgent;
import com.google.adk.agents.SequentialAgent;
import com.google.adk.events.Event;
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.sessions.Session;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import io.reactivex.rxjava3.core.Flowable;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.logging.Level;
import java.util.logging.Logger;

public class StoryFlowAgentExample extends BaseAgent {

  // --- Constants ---
  private static final String APP_NAME = "story_app";
  private static final String USER_ID = "user_12345";
  private static final String SESSION_ID = "session_123344";
  private static final String MODEL_NAME = "gemini-2.0-flash"; // Ensure this model is available

  private static final Logger logger = Logger.getLogger(StoryFlowAgentExample.class.getName());

  private final LlmAgent storyGenerator;
  private final LoopAgent loopAgent;
  private final SequentialAgent sequentialAgent;

  public StoryFlowAgentExample(
      String name, LlmAgent storyGenerator, LoopAgent loopAgent, SequentialAgent sequentialAgent) {
    super(
        name,
        "Orchestrates story generation, critique, revision, and checks.",
        List.of(storyGenerator, loopAgent, sequentialAgent),
        null,
        null);

    this.storyGenerator = storyGenerator;
    this.loopAgent = loopAgent;
    this.sequentialAgent = sequentialAgent;
  }

  public static void main(String[] args) {

    // --- Define the individual LLM agents ---
    LlmAgent storyGenerator =
        LlmAgent.builder()
            .name("StoryGenerator")
            .model(MODEL_NAME)
            .description("Generates the initial story.")
            .instruction(
                """
              You are a story writer. Write a short story (around 100 words) about a cat,
              based on the topic: {topic}
              """)
            .inputSchema(null)
            .outputKey("current_story") // Key for storing output in session state
            .build();

    LlmAgent critic =
        LlmAgent.builder()
            .name("Critic")
            .model(MODEL_NAME)
            .description("Critiques the story.")
            .instruction(
                """
              You are a story critic. Review the story: {current_story}. Provide 1-2 sentences of constructive criticism
              on how to improve it. Focus on plot or character.
              """)
            .inputSchema(null)
            .outputKey("criticism") // Key for storing criticism in session state
            .build();

    LlmAgent reviser =
        LlmAgent.builder()
            .name("Reviser")
            .model(MODEL_NAME)
            .description("Revises the story based on criticism.")
            .instruction(
                """
              You are a story reviser. Revise the story: {current_story}, based on the criticism: {criticism}. Output only the revised story.
              """)
            .inputSchema(null)
            .outputKey("current_story") // Overwrites the original story
            .build();

    LlmAgent grammarCheck =
        LlmAgent.builder()
            .name("GrammarCheck")
            .model(MODEL_NAME)
            .description("Checks grammar and suggests corrections.")
            .instruction(
                """
               You are a grammar checker. Check the grammar of the story: {current_story}. Output only the suggested
               corrections as a list, or output 'Grammar is good!' if there are no errors.
               """)
            .outputKey("grammar_suggestions")
            .build();

    LlmAgent toneCheck =
        LlmAgent.builder()
            .name("ToneCheck")
            .model(MODEL_NAME)
            .description("Analyzes the tone of the story.")
            .instruction(
                """
              You are a tone analyzer. Analyze the tone of the story: {current_story}. Output only one word: 'positive' if
              the tone is generally positive, 'negative' if the tone is generally negative, or 'neutral'
              otherwise.
              """)
            .outputKey("tone_check_result") // This agent's output determines the conditional flow
            .build();

    LoopAgent loopAgent =
        LoopAgent.builder()
            .name("CriticReviserLoop")
            .description("Iteratively critiques and revises the story.")
            .subAgents(critic, reviser)
            .maxIterations(2)
            .build();

    SequentialAgent sequentialAgent =
        SequentialAgent.builder()
            .name("PostProcessing")
            .description("Performs grammar and tone checks sequentially.")
            .subAgents(grammarCheck, toneCheck)
            .build();


    StoryFlowAgentExample storyFlowAgentExample =
        new StoryFlowAgentExample(APP_NAME, storyGenerator, loopAgent, sequentialAgent);

    // --- Run the Agent ---
    runAgent(storyFlowAgentExample, "a lonely robot finding a friend in a junkyard");
  }

  // --- Function to Interact with the Agent ---
  // Sends a new topic to the agent (overwriting the initial one if needed)
  // and runs the workflow.
  public static void runAgent(StoryFlowAgentExample agent, String userTopic) {
    // --- Setup Runner and Session ---
    InMemoryRunner runner = new InMemoryRunner(agent);

    Map<String, Object> initialState = new HashMap<>();
    initialState.put("topic", "a brave kitten exploring a haunted house");

    Session session =
        runner
            .sessionService()
            .createSession(APP_NAME, USER_ID, new ConcurrentHashMap<>(initialState), SESSION_ID)
            .blockingGet();
    logger.log(Level.INFO, () -> String.format("Initial session state: %s", session.state()));

    session.state().put("topic", userTopic); // Update the state in the retrieved session
    logger.log(Level.INFO, () -> String.format("Updated session state topic to: %s", userTopic));

    Content userMessage = Content.fromParts(Part.fromText("Generate a story about: " + userTopic));
    // Use the modified session object for the run
    Flowable<Event> eventStream = runner.runAsync(USER_ID, session.id(), userMessage);

    final String[] finalResponse = {"No final response captured."};
    eventStream.blockingForEach(
        event -> {
          if (event.finalResponse() && event.content().isPresent()) {
            String author = event.author() != null ? event.author() : "UNKNOWN_AUTHOR";
            Optional<String> textOpt =
                event
                    .content()
                    .flatMap(Content::parts)
                    .filter(parts -> !parts.isEmpty())
                    .map(parts -> parts.get(0).text().orElse(""));

            logger.log(Level.INFO, () ->
                String.format("Potential final response from [%s]: %s", author, textOpt.orElse("N/A")));
            textOpt.ifPresent(text -> finalResponse[0] = text);
          }
        });

    System.out.println("\n--- Agent Interaction Result ---");
    System.out.println("Agent Final Response: " + finalResponse[0]);

    // Retrieve session again to see the final state after the run
    Session finalSession =
        runner
            .sessionService()
            .getSession(APP_NAME, USER_ID, SESSION_ID, Optional.empty())
            .blockingGet();

    assert finalSession != null;
    System.out.println("Final Session State:" + finalSession.state());
    System.out.println("-------------------------------\n");
  }

  private boolean isStoryGenerated(InvocationContext ctx) {
    Object currentStoryObj = ctx.session().state().get("current_story");
    return currentStoryObj != null && !String.valueOf(currentStoryObj).isEmpty();
  }

  @Override
  protected Flowable<Event> runAsyncImpl(InvocationContext invocationContext) {
    // Implements the custom orchestration logic for the story workflow.
    // Uses the instance attributes assigned by Pydantic (e.g., self.story_generator).
    logger.log(Level.INFO, () -> String.format("[%s] Starting story generation workflow.", name()));

    // Stage 1. Initial Story Generation
    Flowable<Event> storyGenFlow = runStage(storyGenerator, invocationContext, "StoryGenerator");

    // Stage 2: Critic-Reviser Loop (runs after story generation completes)
    Flowable<Event> criticReviserFlow = Flowable.defer(() -> {
      if (!isStoryGenerated(invocationContext)) {
        logger.log(Level.SEVERE,() ->
            String.format("[%s] Failed to generate initial story. Aborting after StoryGenerator.",
                name()));
        return Flowable.empty(); // Stop further processing if no story
      }
        logger.log(Level.INFO, () ->
            String.format("[%s] Story state after generator: %s",
                name(), invocationContext.session().state().get("current_story")));
        return runStage(loopAgent, invocationContext, "CriticReviserLoop");
    });

    // Stage 3: Post-Processing (runs after critic-reviser loop completes)
    Flowable<Event> postProcessingFlow = Flowable.defer(() -> {
      logger.log(Level.INFO, () ->
          String.format("[%s] Story state after loop: %s",
              name(), invocationContext.session().state().get("current_story")));
      return runStage(sequentialAgent, invocationContext, "PostProcessing");
    });

    // Stage 4: Conditional Regeneration (runs after post-processing completes)
    Flowable<Event> conditionalRegenFlow = Flowable.defer(() -> {
      String toneCheckResult = (String) invocationContext.session().state().get("tone_check_result");
      logger.log(Level.INFO, () -> String.format("[%s] Tone check result: %s", name(), toneCheckResult));

      if ("negative".equalsIgnoreCase(toneCheckResult)) {
        logger.log(Level.INFO, () ->
            String.format("[%s] Tone is negative. Regenerating story...", name()));
        return runStage(storyGenerator, invocationContext, "StoryGenerator (Regen)");
      } else {
        logger.log(Level.INFO, () ->
            String.format("[%s] Tone is not negative. Keeping current story.", name()));
        return Flowable.empty(); // No regeneration needed
      }
    });

    return Flowable.concatArray(storyGenFlow, criticReviserFlow, postProcessingFlow, conditionalRegenFlow)
        .doOnComplete(() -> logger.log(Level.INFO, () -> String.format("[%s] Workflow finished.", name())));
  }

  // Helper method for a single agent run stage with logging
  private Flowable<Event> runStage(BaseAgent agentToRun, InvocationContext ctx, String stageName) {
    logger.log(Level.INFO, () -> String.format("[%s] Running %s...", name(), stageName));
    return agentToRun
        .runAsync(ctx)
        .doOnNext(event ->
            logger.log(Level.INFO,() ->
                String.format("[%s] Event from %s: %s", name(), stageName, event.toJson())))
        .doOnError(err ->
            logger.log(Level.SEVERE,
                String.format("[%s] Error in %s", name(), stageName), err))
        .doOnComplete(() ->
            logger.log(Level.INFO, () ->
                String.format("[%s] %s finished.", name(), stageName)));
  }

  @Override
  protected Flowable<Event> runLiveImpl(InvocationContext invocationContext) {
    return Flowable.error(new UnsupportedOperationException("runLive not implemented."));
  }
}

```

# Full runnable code for the StoryFlowAgent example

import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.BaseAgent;
import com.google.adk.agents.InvocationContext;
import com.google.adk.agents.LoopAgent;
import com.google.adk.agents.SequentialAgent;
import com.google.adk.events.Event;
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.sessions.Session;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import io.reactivex.rxjava3.core.Flowable;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.logging.Level;
import java.util.logging.Logger;

public class StoryFlowAgentExample extends BaseAgent {

  // --- Constants ---
  private static final String APP_NAME = "story_app";
  private static final String USER_ID = "user_12345";
  private static final String SESSION_ID = "session_123344";
  private static final String MODEL_NAME = "gemini-2.0-flash"; // Ensure this model is available

  private static final Logger logger = Logger.getLogger(StoryFlowAgentExample.class.getName());

  private final LlmAgent storyGenerator;
  private final LoopAgent loopAgent;
  private final SequentialAgent sequentialAgent;

  public StoryFlowAgentExample(
      String name, LlmAgent storyGenerator, LoopAgent loopAgent, SequentialAgent sequentialAgent) {
    super(
        name,
        "Orchestrates story generation, critique, revision, and checks.",
        List.of(storyGenerator, loopAgent, sequentialAgent),
        null,
        null);

    this.storyGenerator = storyGenerator;
    this.loopAgent = loopAgent;
    this.sequentialAgent = sequentialAgent;
  }

  public static void main(String[] args) {

    // --- Define the individual LLM agents ---
    LlmAgent storyGenerator =
        LlmAgent.builder()
            .name("StoryGenerator")
            .model(MODEL_NAME)
            .description("Generates the initial story.")
            .instruction(
                """
              You are a story writer. Write a short story (around 100 words) about a cat,
              based on the topic: {topic}
              """)
            .inputSchema(null)
            .outputKey("current_story") // Key for storing output in session state
            .build();

    LlmAgent critic =
        LlmAgent.builder()
            .name("Critic")
            .model(MODEL_NAME)
            .description("Critiques the story.")
            .instruction(
                """
              You are a story critic. Review the story: {current_story}. Provide 1-2 sentences of constructive criticism
              on how to improve it. Focus on plot or character.
              """)
            .inputSchema(null)
            .outputKey("criticism") // Key for storing criticism in session state
            .build();

    LlmAgent reviser =
        LlmAgent.builder()
            .name("Reviser")
            .model(MODEL_NAME)
            .description("Revises the story based on criticism.")
            .instruction(
                """
              You are a story reviser. Revise the story: {current_story}, based on the criticism: {criticism}. Output only the revised story.
              """)
            .inputSchema(null)
            .outputKey("current_story") // Overwrites the original story
            .build();

    LlmAgent grammarCheck =
        LlmAgent.builder()
            .name("GrammarCheck")
            .model(MODEL_NAME)
            .description("Checks grammar and suggests corrections.")
            .instruction(
                """
               You are a grammar checker. Check the grammar of the story: {current_story}. Output only the suggested
               corrections as a list, or output 'Grammar is good!' if there are no errors.
               """)
            .outputKey("grammar_suggestions")
            .build();

    LlmAgent toneCheck =
        LlmAgent.builder()
            .name("ToneCheck")
            .model(MODEL_NAME)
            .description("Analyzes the tone of the story.")
            .instruction(
                """
              You are a tone analyzer. Analyze the tone of the story: {current_story}. Output only one word: 'positive' if
              the tone is generally positive, 'negative' if the tone is generally negative, or 'neutral'
              otherwise.
              """)
            .outputKey("tone_check_result") // This agent's output determines the conditional flow
            .build();

    LoopAgent loopAgent =
        LoopAgent.builder()
            .name("CriticReviserLoop")
            .description("Iteratively critiques and revises the story.")
            .subAgents(critic, reviser)
            .maxIterations(2)
            .build();

    SequentialAgent sequentialAgent =
        SequentialAgent.builder()
            .name("PostProcessing")
            .description("Performs grammar and tone checks sequentially.")
            .subAgents(grammarCheck, toneCheck)
            .build();


    StoryFlowAgentExample storyFlowAgentExample =
        new StoryFlowAgentExample(APP_NAME, storyGenerator, loopAgent, sequentialAgent);

    // --- Run the Agent ---
    runAgent(storyFlowAgentExample, "a lonely robot finding a friend in a junkyard");
  }

  // --- Function to Interact with the Agent ---
  // Sends a new topic to the agent (overwriting the initial one if needed)
  // and runs the workflow.
  public static void runAgent(StoryFlowAgentExample agent, String userTopic) {
    // --- Setup Runner and Session ---
    InMemoryRunner runner = new InMemoryRunner(agent);

    Map<String, Object> initialState = new HashMap<>();
    initialState.put("topic", "a brave kitten exploring a haunted house");

    Session session =
        runner
            .sessionService()
            .createSession(APP_NAME, USER_ID, new ConcurrentHashMap<>(initialState), SESSION_ID)
            .blockingGet();
    logger.log(Level.INFO, () -> String.format("Initial session state: %s", session.state()));

    session.state().put("topic", userTopic); // Update the state in the retrieved session
    logger.log(Level.INFO, () -> String.format("Updated session state topic to: %s", userTopic));

    Content userMessage = Content.fromParts(Part.fromText("Generate a story about: " + userTopic));
    // Use the modified session object for the run
    Flowable<Event> eventStream = runner.runAsync(USER_ID, session.id(), userMessage);

    final String[] finalResponse = {"No final response captured."};
    eventStream.blockingForEach(
        event -> {
          if (event.finalResponse() && event.content().isPresent()) {
            String author = event.author() != null ? event.author() : "UNKNOWN_AUTHOR";
            Optional<String> textOpt =
                event
                    .content()
                    .flatMap(Content::parts)
                    .filter(parts -> !parts.isEmpty())
                    .map(parts -> parts.get(0).text().orElse(""));

            logger.log(Level.INFO, () ->
                String.format("Potential final response from [%s]: %s", author, textOpt.orElse("N/A")));
            textOpt.ifPresent(text -> finalResponse[0] = text);
          }
        });

    System.out.println("\n--- Agent Interaction Result ---");
    System.out.println("Agent Final Response: " + finalResponse[0]);

    // Retrieve session again to see the final state after the run
    Session finalSession =
        runner
            .sessionService()
            .getSession(APP_NAME, USER_ID, SESSION_ID, Optional.empty())
            .blockingGet();

    assert finalSession != null;
    System.out.println("Final Session State:" + finalSession.state());
    System.out.println("-------------------------------\n");
  }

  private boolean isStoryGenerated(InvocationContext ctx) {
    Object currentStoryObj = ctx.session().state().get("current_story");
    return currentStoryObj != null && !String.valueOf(currentStoryObj).isEmpty();
  }

  @Override
  protected Flowable<Event> runAsyncImpl(InvocationContext invocationContext) {
    // Implements the custom orchestration logic for the story workflow.
    // Uses the instance attributes assigned by Pydantic (e.g., self.story_generator).
    logger.log(Level.INFO, () -> String.format("[%s] Starting story generation workflow.", name()));

    // Stage 1. Initial Story Generation
    Flowable<Event> storyGenFlow = runStage(storyGenerator, invocationContext, "StoryGenerator");

    // Stage 2: Critic-Reviser Loop (runs after story generation completes)
    Flowable<Event> criticReviserFlow = Flowable.defer(() -> {
      if (!isStoryGenerated(invocationContext)) {
        logger.log(Level.SEVERE,() ->
            String.format("[%s] Failed to generate initial story. Aborting after StoryGenerator.",
                name()));
        return Flowable.empty(); // Stop further processing if no story
      }
        logger.log(Level.INFO, () ->
            String.format("[%s] Story state after generator: %s",
                name(), invocationContext.session().state().get("current_story")));
        return runStage(loopAgent, invocationContext, "CriticReviserLoop");
    });

    // Stage 3: Post-Processing (runs after critic-reviser loop completes)
    Flowable<Event> postProcessingFlow = Flowable.defer(() -> {
      logger.log(Level.INFO, () ->
          String.format("[%s] Story state after loop: %s",
              name(), invocationContext.session().state().get("current_story")));
      return runStage(sequentialAgent, invocationContext, "PostProcessing");
    });

    // Stage 4: Conditional Regeneration (runs after post-processing completes)
    Flowable<Event> conditionalRegenFlow = Flowable.defer(() -> {
      String toneCheckResult = (String) invocationContext.session().state().get("tone_check_result");
      logger.log(Level.INFO, () -> String.format("[%s] Tone check result: %s", name(), toneCheckResult));

      if ("negative".equalsIgnoreCase(toneCheckResult)) {
        logger.log(Level.INFO, () ->
            String.format("[%s] Tone is negative. Regenerating story...", name()));
        return runStage(storyGenerator, invocationContext, "StoryGenerator (Regen)");
      } else {
        logger.log(Level.INFO, () ->
            String.format("[%s] Tone is not negative. Keeping current story.", name()));
        return Flowable.empty(); // No regeneration needed
      }
    });

    return Flowable.concatArray(storyGenFlow, criticReviserFlow, postProcessingFlow, conditionalRegenFlow)
        .doOnComplete(() -> logger.log(Level.INFO, () -> String.format("[%s] Workflow finished.", name())));
  }

  // Helper method for a single agent run stage with logging
  private Flowable<Event> runStage(BaseAgent agentToRun, InvocationContext ctx, String stageName) {
    logger.log(Level.INFO, () -> String.format("[%s] Running %s...", name(), stageName));
    return agentToRun
        .runAsync(ctx)
        .doOnNext(event ->
            logger.log(Level.INFO,() ->
                String.format("[%s] Event from %s: %s", name(), stageName, event.toJson())))
        .doOnError(err ->
            logger.log(Level.SEVERE,
                String.format("[%s] Error in %s", name(), stageName), err))
        .doOnComplete(() ->
            logger.log(Level.INFO, () ->
                String.format("[%s] %s finished.", name(), stageName)));
  }

  @Override
  protected Flowable<Event> runLiveImpl(InvocationContext invocationContext) {
    return Flowable.error(new UnsupportedOperationException("runLive not implemented."));
  }
}