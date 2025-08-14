# Agent Development Kit

*Source: https://google.github.io/adk-docs/*

# Agent Development Kit

## What is Agent Development Kit?

Agent Development Kit (ADK) is a flexible and modular framework for **developing
and deploying AI agents**. While optimized for Gemini and the Google ecosystem,
ADK is **model-agnostic**, **deployment-agnostic**, and is built for
**compatibility with other frameworks**. ADK was designed to make agent
development feel more like software development, to make it easier for
developers to create, deploy, and orchestrate agentic architectures that range
from simple tasks to complex workflows.

Get started:

pip install google-adk

`pip install google-adk`

`pip install google-adk`

```
<dependency>
    <groupId>com.google.adk</groupId>
    <artifactId>google-adk</artifactId>
    <version>0.2.0</version>
</dependency>

```

<dependency>
    <groupId>com.google.adk</groupId>
    <artifactId>google-adk</artifactId>
    <version>0.2.0</version>
</dependency>

```
dependencies {
    implementation 'com.google.adk:google-adk:0.2.0'
}

```

dependencies {
    implementation 'com.google.adk:google-adk:0.2.0'
}

[Quickstart](get-started/quickstart/)
[Tutorials](tutorials/)
[Sample Agents](http://github.com/google/adk-samples)
[API Reference](api-reference/)
[Contribute ❤️](contributing-guide/)

## Learn more

[ Watch "Introducing Agent Development Kit"!](https://www.youtube.com/watch?v=zgrOwow_uTQ target=)

- Flexible Orchestration

Define workflows using workflow agents (Sequential, Parallel, Loop)
for predictable pipelines, or leverage LLM-driven dynamic routing
(LlmAgent transfer) for adaptive behavior.
Learn about agents
- Multi-Agent Architecture

Build modular and scalable applications by composing multiple specialized
agents in a hierarchy. Enable complex coordination and delegation.
Explore multi-agent systems
- Rich Tool Ecosystem

Equip agents with diverse capabilities: use pre-built tools (Search, Code
Exec), create custom functions, integrate 3rd-party libraries (LangChain,
CrewAI), or even use other agents as tools.
Browse tools
- Deployment Ready

Containerize and deploy your agents anywhere – run locally, scale with
Vertex AI Agent Engine, or integrate into custom infrastructure using Cloud
Run or Docker.
Deploy agents
- Built-in Evaluation

Systematically assess agent performance by evaluating both the final
response quality and the step-by-step execution trajectory against
predefined test cases.
Evaluate agents
- Building Safe and Secure Agents

Learn how to building powerful and trustworthy agents by implementing
security and safety patterns and best practices into your agent's design.
Safety and Security

**Flexible Orchestration**

Define workflows using workflow agents (`Sequential`, `Parallel`, `Loop`)
for predictable pipelines, or leverage LLM-driven dynamic routing
(`LlmAgent` transfer) for adaptive behavior.

`Sequential`

`Parallel`

`Loop`

`LlmAgent`

[Learn about agents](agents/)

**Multi-Agent Architecture**

Build modular and scalable applications by composing multiple specialized
agents in a hierarchy. Enable complex coordination and delegation.

[Explore multi-agent systems](agents/multi-agents/)

**Rich Tool Ecosystem**

Equip agents with diverse capabilities: use pre-built tools (Search, Code
Exec), create custom functions, integrate 3rd-party libraries (LangChain,
CrewAI), or even use other agents as tools.

[Browse tools](tools/)

**Deployment Ready**

Containerize and deploy your agents anywhere – run locally, scale with
Vertex AI Agent Engine, or integrate into custom infrastructure using Cloud
Run or Docker.

[Deploy agents](deploy/)

**Built-in Evaluation**

Systematically assess agent performance by evaluating both the final
response quality and the step-by-step execution trajectory against
predefined test cases.

[Evaluate agents](evaluate/)

**Building Safe and Secure Agents**

Learn how to building powerful and trustworthy agents by implementing
security and safety patterns and best practices into your agent's design.

[Safety and Security](safety/)