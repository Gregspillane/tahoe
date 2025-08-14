# Third party tools - Agent Development Kit

*Source: https://google.github.io/adk-docs/tools/third-party-tools/*

# Third Party Tools



ADK is designed to be **highly extensible, allowing you to seamlessly integrate tools from other AI Agent frameworks** like CrewAI and LangChain. This interoperability is crucial because it allows for faster development time and allows you to reuse existing tools.

## 1. Using LangChain Tools

ADK provides the `LangchainTool` wrapper to integrate tools from the LangChain ecosystem into your agents.

`LangchainTool`

### Example: Web Search using LangChain's Tavily tool

[Tavily](https://tavily.com/) provides a search API that returns answers derived from real-time search results, intended for use by applications like AI agents.

1. Follow ADK installation and setup guide.
1. Install Dependencies: Ensure you have the necessary LangChain packages installed. For example, to use the Tavily search tool, install its specific dependencies:
pip install langchain_community tavily-python
1. Obtain a Tavily API KEY and export it as an environment variable.
export TAVILY_API_KEY=<REPLACE_WITH_API_KEY>
1. Import: Import the LangchainTool wrapper from ADK and the specific LangChain tool you wish to use (e.g, TavilySearchResults).
from google.adk.tools.langchain_tool import LangchainTool
from langchain_community.tools import TavilySearchResults
1. Instantiate & Wrap: Create an instance of your LangChain tool and pass it to the LangchainTool constructor.
# Instantiate the LangChain tool
tavily_tool_instance = TavilySearchResults(
    max_results=5,
    search_depth="advanced",
    include_answer=True,
    include_raw_content=True,
    include_images=True,
)

# Wrap it with LangchainTool for ADK
adk_tavily_tool = LangchainTool(tool=tavily_tool_instance)
1. Add to Agent: Include the wrapped LangchainTool instance in your agent's tools list during definition.
from google.adk import Agent

# Define the ADK agent, including the wrapped tool
my_agent = Agent(
    name="langchain_tool_agent",
    model="gemini-2.0-flash",
    description="Agent to answer questions using TavilySearch.",
    instruction="I can answer your questions by searching the internet. Just ask me anything!",
    tools=[adk_tavily_tool] # Add the wrapped tool here
)

Follow [ADK installation and setup](../../get-started/installation/) guide.

**Install Dependencies:** Ensure you have the necessary LangChain packages installed. For example, to use the Tavily search tool, install its specific dependencies:

```
pip install langchain_community tavily-python

```

pip install langchain_community tavily-python

Obtain a [Tavily](https://tavily.com/) API KEY and export it as an environment variable.

```
export TAVILY_API_KEY=<REPLACE_WITH_API_KEY>

```

export TAVILY_API_KEY=<REPLACE_WITH_API_KEY>

**Import:** Import the `LangchainTool` wrapper from ADK and the specific `LangChain` tool you wish to use (e.g, `TavilySearchResults`).

`LangchainTool`

`LangChain`

`TavilySearchResults`

```
from google.adk.tools.langchain_tool import LangchainTool
from langchain_community.tools import TavilySearchResults

```

from google.adk.tools.langchain_tool import LangchainTool
from langchain_community.tools import TavilySearchResults

**Instantiate & Wrap:** Create an instance of your LangChain tool and pass it to the `LangchainTool` constructor.

`LangchainTool`

```
# Instantiate the LangChain tool
tavily_tool_instance = TavilySearchResults(
    max_results=5,
    search_depth="advanced",
    include_answer=True,
    include_raw_content=True,
    include_images=True,
)

# Wrap it with LangchainTool for ADK
adk_tavily_tool = LangchainTool(tool=tavily_tool_instance)

```

# Instantiate the LangChain tool
tavily_tool_instance = TavilySearchResults(
    max_results=5,
    search_depth="advanced",
    include_answer=True,
    include_raw_content=True,
    include_images=True,
)

# Wrap it with LangchainTool for ADK
adk_tavily_tool = LangchainTool(tool=tavily_tool_instance)

**Add to Agent:** Include the wrapped `LangchainTool` instance in your agent's `tools` list during definition.

`LangchainTool`

`tools`

```
from google.adk import Agent

# Define the ADK agent, including the wrapped tool
my_agent = Agent(
    name="langchain_tool_agent",
    model="gemini-2.0-flash",
    description="Agent to answer questions using TavilySearch.",
    instruction="I can answer your questions by searching the internet. Just ask me anything!",
    tools=[adk_tavily_tool] # Add the wrapped tool here
)

```

from google.adk import Agent

# Define the ADK agent, including the wrapped tool
my_agent = Agent(
    name="langchain_tool_agent",
    model="gemini-2.0-flash",
    description="Agent to answer questions using TavilySearch.",
    instruction="I can answer your questions by searching the internet. Just ask me anything!",
    tools=[adk_tavily_tool] # Add the wrapped tool here
)

### Full Example: Tavily Search

Here's the full code combining the steps above to create and run an agent using the LangChain Tavily search tool.

```
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

import os
from google.adk import Agent, Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.langchain_tool import LangchainTool
from google.genai import types
from langchain_community.tools import TavilySearchResults

# Ensure TAVILY_API_KEY is set in your environment
if not os.getenv("TAVILY_API_KEY"):
    print("Warning: TAVILY_API_KEY environment variable not set.")

APP_NAME = "news_app"
USER_ID = "1234"
SESSION_ID = "session1234"

# Instantiate LangChain tool
tavily_search = TavilySearchResults(
    max_results=5,
    search_depth="advanced",
    include_answer=True,
    include_raw_content=True,
    include_images=True,
)

# Wrap with LangchainTool
adk_tavily_tool = LangchainTool(tool=tavily_search)

# Define Agent with the wrapped tool
my_agent = Agent(
    name="langchain_tool_agent",
    model="gemini-2.0-flash",
    description="Agent to answer questions using TavilySearch.",
    instruction="I can answer your questions by searching the internet. Just ask me anything!",
    tools=[adk_tavily_tool] # Add the wrapped tool here
)

async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=my_agent, app_name=APP_NAME, session_service=session_service)
    return session, runner

# Agent Interaction
async def call_agent_async(query):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    session, runner = await setup_session_and_runner()
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    async for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response: ", final_response)

# Note: In Colab, you can directly use 'await' at the top level.
# If running this code as a standalone Python script, you'll need to use asyncio.run() or manage the event loop.
await call_agent_async("stock price of GOOG")

```

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

import os
from google.adk import Agent, Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.langchain_tool import LangchainTool
from google.genai import types
from langchain_community.tools import TavilySearchResults

# Ensure TAVILY_API_KEY is set in your environment
if not os.getenv("TAVILY_API_KEY"):
    print("Warning: TAVILY_API_KEY environment variable not set.")

APP_NAME = "news_app"
USER_ID = "1234"
SESSION_ID = "session1234"

# Instantiate LangChain tool
tavily_search = TavilySearchResults(
    max_results=5,
    search_depth="advanced",
    include_answer=True,
    include_raw_content=True,
    include_images=True,
)

# Wrap with LangchainTool
adk_tavily_tool = LangchainTool(tool=tavily_search)

# Define Agent with the wrapped tool
my_agent = Agent(
    name="langchain_tool_agent",
    model="gemini-2.0-flash",
    description="Agent to answer questions using TavilySearch.",
    instruction="I can answer your questions by searching the internet. Just ask me anything!",
    tools=[adk_tavily_tool] # Add the wrapped tool here
)

async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=my_agent, app_name=APP_NAME, session_service=session_service)
    return session, runner

# Agent Interaction
async def call_agent_async(query):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    session, runner = await setup_session_and_runner()
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    async for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response: ", final_response)

# Note: In Colab, you can directly use 'await' at the top level.
# If running this code as a standalone Python script, you'll need to use asyncio.run() or manage the event loop.
await call_agent_async("stock price of GOOG")

## 2. Using CrewAI tools

ADK provides the `CrewaiTool` wrapper to integrate tools from the CrewAI library.

`CrewaiTool`

### Example: Web Search using CrewAI's Serper API

[Serper API](https://serper.dev/) provides access to Google Search results programmatically. It allows applications, like AI agents, to perform real-time Google searches (including news, images, etc.) and get structured data back without needing to scrape web pages directly.

1. Follow ADK installation and setup guide.
1. Install Dependencies: Install the necessary CrewAI tools package. For example, to use the SerperDevTool:
pip install crewai-tools
1. Obtain a Serper API KEY and export it as an environment variable.
export SERPER_API_KEY=<REPLACE_WITH_API_KEY>
1. Import: Import CrewaiTool from ADK and the desired CrewAI tool (e.g, SerperDevTool).
from google.adk.tools.crewai_tool import CrewaiTool
from crewai_tools import SerperDevTool
1. Instantiate & Wrap: Create an instance of the CrewAI tool. Pass it to the CrewaiTool constructor. Crucially, you must provide a name and description to the ADK wrapper, as these are used by ADK's underlying model to understand when to use the tool.
# Instantiate the CrewAI tool
serper_tool_instance = SerperDevTool(
    n_results=10,
    save_file=False,
    search_type="news",
)

# Wrap it with CrewaiTool for ADK, providing name and description
adk_serper_tool = CrewaiTool(
    name="InternetNewsSearch",
    description="Searches the internet specifically for recent news articles using Serper.",
    tool=serper_tool_instance
)
1. Add to Agent: Include the wrapped CrewaiTool instance in your agent's tools list.
from google.adk import Agent

# Define the ADK agent
my_agent = Agent(
    name="crewai_search_agent",
    model="gemini-2.0-flash",
    description="Agent to find recent news using the Serper search tool.",
    instruction="I can find the latest news for you. What topic are you interested in?",
    tools=[adk_serper_tool] # Add the wrapped tool here
)

Follow [ADK installation and setup](../../get-started/installation/) guide.

**Install Dependencies:** Install the necessary CrewAI tools package. For example, to use the SerperDevTool:

```
pip install crewai-tools

```

pip install crewai-tools

Obtain a [Serper API KEY](https://serper.dev/) and export it as an environment variable.

```
export SERPER_API_KEY=<REPLACE_WITH_API_KEY>

```

export SERPER_API_KEY=<REPLACE_WITH_API_KEY>

**Import:** Import `CrewaiTool` from ADK and the desired CrewAI tool (e.g, `SerperDevTool`).

`CrewaiTool`

`SerperDevTool`

```
from google.adk.tools.crewai_tool import CrewaiTool
from crewai_tools import SerperDevTool

```

from google.adk.tools.crewai_tool import CrewaiTool
from crewai_tools import SerperDevTool

**Instantiate & Wrap:** Create an instance of the CrewAI tool. Pass it to the `CrewaiTool` constructor. **Crucially, you must provide a name and description** to the ADK wrapper, as these are used by ADK's underlying model to understand when to use the tool.

`CrewaiTool`

```
# Instantiate the CrewAI tool
serper_tool_instance = SerperDevTool(
    n_results=10,
    save_file=False,
    search_type="news",
)

# Wrap it with CrewaiTool for ADK, providing name and description
adk_serper_tool = CrewaiTool(
    name="InternetNewsSearch",
    description="Searches the internet specifically for recent news articles using Serper.",
    tool=serper_tool_instance
)

```

# Instantiate the CrewAI tool
serper_tool_instance = SerperDevTool(
    n_results=10,
    save_file=False,
    search_type="news",
)

# Wrap it with CrewaiTool for ADK, providing name and description
adk_serper_tool = CrewaiTool(
    name="InternetNewsSearch",
    description="Searches the internet specifically for recent news articles using Serper.",
    tool=serper_tool_instance
)

**Add to Agent:** Include the wrapped `CrewaiTool` instance in your agent's `tools` list.

`CrewaiTool`

`tools`

```
from google.adk import Agent

# Define the ADK agent
my_agent = Agent(
    name="crewai_search_agent",
    model="gemini-2.0-flash",
    description="Agent to find recent news using the Serper search tool.",
    instruction="I can find the latest news for you. What topic are you interested in?",
    tools=[adk_serper_tool] # Add the wrapped tool here
)

```

from google.adk import Agent

# Define the ADK agent
my_agent = Agent(
    name="crewai_search_agent",
    model="gemini-2.0-flash",
    description="Agent to find recent news using the Serper search tool.",
    instruction="I can find the latest news for you. What topic are you interested in?",
    tools=[adk_serper_tool] # Add the wrapped tool here
)

### Full Example: Serper API

Here's the full code combining the steps above to create and run an agent using the CrewAI Serper API search tool.

```
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

import os
from google.adk import Agent, Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.crewai_tool import CrewaiTool
from google.genai import types
from crewai_tools import SerperDevTool


# Constants
APP_NAME = "news_app"
USER_ID = "user1234"
SESSION_ID = "1234"

# Ensure SERPER_API_KEY is set in your environment
if not os.getenv("SERPER_API_KEY"):
    print("Warning: SERPER_API_KEY environment variable not set.")

serper_tool_instance = SerperDevTool(
    n_results=10,
    save_file=False,
    search_type="news",
)

adk_serper_tool = CrewaiTool(
    name="InternetNewsSearch",
    description="Searches the internet specifically for recent news articles using Serper.",
    tool=serper_tool_instance
)

serper_agent = Agent(
    name="basic_search_agent",
    model="gemini-2.0-flash",
    description="Agent to answer questions using Google Search.",
    instruction="I can answer your questions by searching the internet. Just ask me anything!",
    # Add the Serper tool
    tools=[adk_serper_tool]
)

# Session and Runner
async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=serper_agent, app_name=APP_NAME, session_service=session_service)
    return session, runner


# Agent Interaction
async def call_agent_async(query):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    session, runner = await setup_session_and_runner()
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    async for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response: ", final_response)

# Note: In Colab, you can directly use 'await' at the top level.
# If running this code as a standalone Python script, you'll need to use asyncio.run() or manage the event loop.
await call_agent_async("what's the latest news on AI Agents?")

```

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

import os
from google.adk import Agent, Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.crewai_tool import CrewaiTool
from google.genai import types
from crewai_tools import SerperDevTool


# Constants
APP_NAME = "news_app"
USER_ID = "user1234"
SESSION_ID = "1234"

# Ensure SERPER_API_KEY is set in your environment
if not os.getenv("SERPER_API_KEY"):
    print("Warning: SERPER_API_KEY environment variable not set.")

serper_tool_instance = SerperDevTool(
    n_results=10,
    save_file=False,
    search_type="news",
)

adk_serper_tool = CrewaiTool(
    name="InternetNewsSearch",
    description="Searches the internet specifically for recent news articles using Serper.",
    tool=serper_tool_instance
)

serper_agent = Agent(
    name="basic_search_agent",
    model="gemini-2.0-flash",
    description="Agent to answer questions using Google Search.",
    instruction="I can answer your questions by searching the internet. Just ask me anything!",
    # Add the Serper tool
    tools=[adk_serper_tool]
)

# Session and Runner
async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=serper_agent, app_name=APP_NAME, session_service=session_service)
    return session, runner


# Agent Interaction
async def call_agent_async(query):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    session, runner = await setup_session_and_runner()
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    async for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response: ", final_response)

# Note: In Colab, you can directly use 'await' at the top level.
# If running this code as a standalone Python script, you'll need to use asyncio.run() or manage the event loop.
await call_agent_async("what's the latest news on AI Agents?")