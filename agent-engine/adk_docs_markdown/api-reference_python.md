# Agent Development Kit documentation

*Source: https://google.github.io/adk-docs/api-reference/python/*

# google

- [Submodules](google-adk.html)
- [google.adk.a2a module](google-adk.html#module-google.adk.a2a)
- [google.adk.agents module](google-adk.html#module-google.adk.agents)
Agent
BaseAgent
BaseAgent.after_agent_callback
BaseAgent.before_agent_callback
BaseAgent.description
BaseAgent.name
BaseAgent.parent_agent
BaseAgent.sub_agents
BaseAgent.from_config()
BaseAgent.clone()
BaseAgent.find_agent()
BaseAgent.find_sub_agent()
BaseAgent.model_post_init()
BaseAgent.run_async()
BaseAgent.run_live()
BaseAgent.canonical_after_agent_callbacks
BaseAgent.canonical_before_agent_callbacks
BaseAgent.root_agent


InvocationContext
InvocationContext.active_streaming_tools
InvocationContext.agent
InvocationContext.artifact_service
InvocationContext.branch
InvocationContext.credential_service
InvocationContext.end_invocation
InvocationContext.invocation_id
InvocationContext.live_request_queue
InvocationContext.memory_service
InvocationContext.plugin_manager
InvocationContext.run_config
InvocationContext.session
InvocationContext.session_service
InvocationContext.transcription_cache
InvocationContext.user_content
InvocationContext.increment_llm_call_count()
InvocationContext.model_post_init()
InvocationContext.app_name
InvocationContext.user_id


LiveRequest
LiveRequest.activity_end
LiveRequest.activity_start
LiveRequest.blob
LiveRequest.close
LiveRequest.content


LiveRequestQueue
LiveRequestQueue.close()
LiveRequestQueue.get()
LiveRequestQueue.send()
LiveRequestQueue.send_activity_end()
LiveRequestQueue.send_activity_start()
LiveRequestQueue.send_content()
LiveRequestQueue.send_realtime()


LlmAgent
LlmAgent.after_model_callback
LlmAgent.after_tool_callback
LlmAgent.before_model_callback
LlmAgent.before_tool_callback
LlmAgent.code_executor
LlmAgent.disallow_transfer_to_parent
LlmAgent.disallow_transfer_to_peers
LlmAgent.generate_content_config
LlmAgent.global_instruction
LlmAgent.include_contents
LlmAgent.input_schema
LlmAgent.instruction
LlmAgent.model
LlmAgent.output_key
LlmAgent.output_schema
LlmAgent.planner
LlmAgent.tools
LlmAgent.from_config()
LlmAgent.canonical_global_instruction()
LlmAgent.canonical_instruction()
LlmAgent.canonical_tools()
LlmAgent.canonical_after_model_callbacks
LlmAgent.canonical_after_tool_callbacks
LlmAgent.canonical_before_model_callbacks
LlmAgent.canonical_before_tool_callbacks
LlmAgent.canonical_model


LoopAgent
LoopAgent.max_iterations
LoopAgent.from_config()


ParallelAgent
ParallelAgent.from_config()


RunConfig
RunConfig.enable_affective_dialog
RunConfig.input_audio_transcription
RunConfig.max_llm_calls
RunConfig.output_audio_transcription
RunConfig.proactivity
RunConfig.realtime_input_config
RunConfig.response_modalities
RunConfig.save_input_blobs_as_artifacts
RunConfig.session_resumption
RunConfig.speech_config
RunConfig.streaming_mode
RunConfig.support_cfc
RunConfig.validate_max_llm_calls


SequentialAgent
SequentialAgent.from_config()
- [google.adk.artifacts module](google-adk.html#module-google.adk.artifacts)
BaseArtifactService
BaseArtifactService.delete_artifact()
BaseArtifactService.list_artifact_keys()
BaseArtifactService.list_versions()
BaseArtifactService.load_artifact()
BaseArtifactService.save_artifact()


GcsArtifactService
GcsArtifactService.delete_artifact()
GcsArtifactService.list_artifact_keys()
GcsArtifactService.list_versions()
GcsArtifactService.load_artifact()
GcsArtifactService.save_artifact()


InMemoryArtifactService
InMemoryArtifactService.artifacts
InMemoryArtifactService.delete_artifact()
InMemoryArtifactService.list_artifact_keys()
InMemoryArtifactService.list_versions()
InMemoryArtifactService.load_artifact()
InMemoryArtifactService.save_artifact()
- [google.adk.auth module](google-adk.html#module-google.adk.auth)
- [google.adk.cli module](google-adk.html#module-google.adk.cli)
- [google.adk.code_executors module](google-adk.html#module-google.adk.code_executors)
BaseCodeExecutor
BaseCodeExecutor.optimize_data_file
BaseCodeExecutor.stateful
BaseCodeExecutor.error_retry_attempts
BaseCodeExecutor.code_block_delimiters
BaseCodeExecutor.execution_result_delimiters
BaseCodeExecutor.code_block_delimiters
BaseCodeExecutor.error_retry_attempts
BaseCodeExecutor.execution_result_delimiters
BaseCodeExecutor.optimize_data_file
BaseCodeExecutor.stateful
BaseCodeExecutor.execute_code()


BuiltInCodeExecutor
BuiltInCodeExecutor.execute_code()
BuiltInCodeExecutor.process_llm_request()


CodeExecutorContext
CodeExecutorContext.add_input_files()
CodeExecutorContext.add_processed_file_names()
CodeExecutorContext.clear_input_files()
CodeExecutorContext.get_error_count()
CodeExecutorContext.get_execution_id()
CodeExecutorContext.get_input_files()
CodeExecutorContext.get_processed_file_names()
CodeExecutorContext.get_state_delta()
CodeExecutorContext.increment_error_count()
CodeExecutorContext.reset_error_count()
CodeExecutorContext.set_execution_id()
CodeExecutorContext.update_code_execution_result()


ContainerCodeExecutor
ContainerCodeExecutor.base_url
ContainerCodeExecutor.image
ContainerCodeExecutor.docker_path
ContainerCodeExecutor.base_url
ContainerCodeExecutor.docker_path
ContainerCodeExecutor.image
ContainerCodeExecutor.optimize_data_file
ContainerCodeExecutor.stateful
ContainerCodeExecutor.execute_code()
ContainerCodeExecutor.model_post_init()


UnsafeLocalCodeExecutor
UnsafeLocalCodeExecutor.optimize_data_file
UnsafeLocalCodeExecutor.stateful
UnsafeLocalCodeExecutor.execute_code()


VertexAiCodeExecutor
VertexAiCodeExecutor.resource_name
VertexAiCodeExecutor.resource_name
VertexAiCodeExecutor.execute_code()
VertexAiCodeExecutor.model_post_init()
- [google.adk.errors module](google-adk.html#module-google.adk.errors)
- [google.adk.evaluation module](google-adk.html#module-google.adk.evaluation)
AgentEvaluator
AgentEvaluator.evaluate()
AgentEvaluator.evaluate_eval_set()
AgentEvaluator.find_config_for_test_file()
AgentEvaluator.migrate_eval_data_to_new_schema()
- [google.adk.events module](google-adk.html#module-google.adk.events)
Event
Event.invocation_id
Event.author
Event.actions
Event.long_running_tool_ids
Event.branch
Event.id
Event.timestamp
Event.get_function_calls
Event.actions
Event.author
Event.branch
Event.id
Event.invocation_id
Event.long_running_tool_ids
Event.timestamp
Event.new_id()
Event.get_function_calls()
Event.get_function_responses()
Event.has_trailing_code_execution_result()
Event.is_final_response()
Event.model_post_init()


EventActions
EventActions.artifact_delta
EventActions.escalate
EventActions.requested_auth_configs
EventActions.skip_summarization
EventActions.state_delta
EventActions.transfer_to_agent
- [google.adk.examples module](google-adk.html#module-google.adk.examples)
BaseExampleProvider
BaseExampleProvider.get_examples()


Example
Example.input
Example.output
Example.input
Example.output


VertexAiExampleStore
VertexAiExampleStore.get_examples()
- [google.adk.flows module](google-adk.html#module-google.adk.flows)
- [google.adk.memory module](google-adk.html#module-google.adk.memory)
BaseMemoryService
BaseMemoryService.add_session_to_memory()
BaseMemoryService.search_memory()


InMemoryMemoryService
InMemoryMemoryService.add_session_to_memory()
InMemoryMemoryService.search_memory()


VertexAiMemoryBankService
VertexAiMemoryBankService.add_session_to_memory()
VertexAiMemoryBankService.search_memory()


VertexAiRagMemoryService
VertexAiRagMemoryService.add_session_to_memory()
VertexAiRagMemoryService.search_memory()
- [google.adk.models module](google-adk.html#module-google.adk.models)
BaseLlm
BaseLlm.model
BaseLlm.model
BaseLlm.supported_models()
BaseLlm.connect()
BaseLlm.generate_content_async()


Gemini
Gemini.model
Gemini.model
Gemini.retry_options
Gemini.supported_models()
Gemini.connect()
Gemini.generate_content_async()
Gemini.api_client


LLMRegistry
LLMRegistry.new_llm()
LLMRegistry.register()
LLMRegistry.resolve()
- [google.adk.planners module](google-adk.html#module-google.adk.planners)
BasePlanner
BasePlanner.build_planning_instruction()
BasePlanner.process_planning_response()


BuiltInPlanner
BuiltInPlanner.thinking_config
BuiltInPlanner.apply_thinking_config()
BuiltInPlanner.build_planning_instruction()
BuiltInPlanner.process_planning_response()
BuiltInPlanner.thinking_config


PlanReActPlanner
PlanReActPlanner.build_planning_instruction()
PlanReActPlanner.process_planning_response()
- [google.adk.platform module](google-adk.html#module-google.adk.platform)
- [google.adk.plugins module](google-adk.html#module-google.adk.plugins)
BasePlugin
BasePlugin.after_agent_callback()
BasePlugin.after_model_callback()
BasePlugin.after_run_callback()
BasePlugin.after_tool_callback()
BasePlugin.before_agent_callback()
BasePlugin.before_model_callback()
BasePlugin.before_run_callback()
BasePlugin.before_tool_callback()
BasePlugin.on_event_callback()
BasePlugin.on_model_error_callback()
BasePlugin.on_tool_error_callback()
BasePlugin.on_user_message_callback()
- [google.adk.runners module](google-adk.html#module-google.adk.runners)
InMemoryRunner
InMemoryRunner.agent
InMemoryRunner.app_name
InMemoryRunner._in_memory_session_service


Runner
Runner.app_name
Runner.agent
Runner.artifact_service
Runner.plugin_manager
Runner.session_service
Runner.memory_service
Runner.agent
Runner.app_name
Runner.artifact_service
Runner.close()
Runner.credential_service
Runner.memory_service
Runner.plugin_manager
Runner.run()
Runner.run_async()
Runner.run_live()
Runner.session_service
- [google.adk.sessions module](google-adk.html#module-google.adk.sessions)
BaseSessionService
BaseSessionService.append_event()
BaseSessionService.create_session()
BaseSessionService.delete_session()
BaseSessionService.get_session()
BaseSessionService.list_sessions()


DatabaseSessionService
DatabaseSessionService.append_event()
DatabaseSessionService.create_session()
DatabaseSessionService.delete_session()
DatabaseSessionService.get_session()
DatabaseSessionService.list_sessions()


InMemorySessionService
InMemorySessionService.append_event()
InMemorySessionService.create_session()
InMemorySessionService.create_session_sync()
InMemorySessionService.delete_session()
InMemorySessionService.delete_session_sync()
InMemorySessionService.get_session()
InMemorySessionService.get_session_sync()
InMemorySessionService.list_sessions()
InMemorySessionService.list_sessions_sync()


Session
Session.id
Session.app_name
Session.user_id
Session.state
Session.events
Session.last_update_time
Session.app_name
Session.events
Session.id
Session.last_update_time
Session.state
Session.user_id


State
State.APP_PREFIX
State.TEMP_PREFIX
State.USER_PREFIX
State.get()
State.has_delta()
State.to_dict()
State.update()


VertexAiSessionService
VertexAiSessionService.append_event()
VertexAiSessionService.create_session()
VertexAiSessionService.delete_session()
VertexAiSessionService.get_session()
VertexAiSessionService.list_sessions()
- [google.adk.telemetry module](google-adk.html#module-google.adk.telemetry)
trace_call_llm()
trace_merged_tool_calls()
trace_send_data()
trace_tool_call()
- [google.adk.tools package](google-adk.html#module-google.adk.tools)
APIHubToolset
APIHubToolset.close()
APIHubToolset.get_tools()


AgentTool
AgentTool.agent
AgentTool.skip_summarization
AgentTool.from_config()
AgentTool.populate_name()
AgentTool.run_async()


AuthToolArguments
AuthToolArguments.auth_config
AuthToolArguments.function_call_id


BaseTool
BaseTool.description
BaseTool.from_config()
BaseTool.is_long_running
BaseTool.name
BaseTool.process_llm_request()
BaseTool.run_async()


ExampleTool
ExampleTool.examples
ExampleTool.process_llm_request()


FunctionTool
FunctionTool.func
FunctionTool.run_async()


LongRunningFunctionTool
LongRunningFunctionTool.is_long_running


ToolContext
ToolContext.invocation_context
ToolContext.function_call_id
ToolContext.event_actions
ToolContext.actions
ToolContext.get_auth_response()
ToolContext.request_credential()
ToolContext.search_memory()


VertexAiSearchTool
VertexAiSearchTool.data_store_id
VertexAiSearchTool.search_engine_id
VertexAiSearchTool.process_llm_request()


exit_loop()
transfer_to_agent()
- [google.adk.tools.agent_tool module](google-adk.html#module-google.adk.tools.agent_tool)
AgentTool
AgentTool.agent
AgentTool.skip_summarization
AgentTool.from_config()
AgentTool.populate_name()
AgentTool.run_async()


AgentToolConfig
AgentToolConfig.agent
AgentToolConfig.skip_summarization
- [google.adk.tools.apihub_tool module](google-adk.html#module-google.adk.tools.apihub_tool)
APIHubToolset
APIHubToolset.close()
APIHubToolset.get_tools()
- [google.adk.tools.application_integration_tool module](google-adk.html#module-google.adk.tools.application_integration_tool)
ApplicationIntegrationToolset
ApplicationIntegrationToolset.close()
ApplicationIntegrationToolset.get_tools()


IntegrationConnectorTool
IntegrationConnectorTool.EXCLUDE_FIELDS
IntegrationConnectorTool.OPTIONAL_FIELDS
IntegrationConnectorTool.run_async()
- [google.adk.tools.authenticated_function_tool module](google-adk.html#module-google.adk.tools.authenticated_function_tool)
AuthenticatedFunctionTool
AuthenticatedFunctionTool.run_async()
- [google.adk.tools.base_authenticated_tool module](google-adk.html#module-google.adk.tools.base_authenticated_tool)
BaseAuthenticatedTool
BaseAuthenticatedTool.run_async()
- [google.adk.tools.base_tool module](google-adk.html#module-google.adk.tools.base_tool)
BaseTool
BaseTool.description
BaseTool.from_config()
BaseTool.is_long_running
BaseTool.name
BaseTool.process_llm_request()
BaseTool.run_async()


BaseToolConfig
ToolArgsConfig
ToolConfig
ToolConfig.args
ToolConfig.name
- [google.adk.tools.base_toolset module](google-adk.html#module-google.adk.tools.base_toolset)
BaseToolset
BaseToolset.close()
BaseToolset.get_tools()
BaseToolset.process_llm_request()


ToolPredicate
- [google.adk.tools.bigquery module](google-adk.html#module-google.adk.tools.bigquery)
BigQueryCredentialsConfig
BigQueryCredentialsConfig.client_id
BigQueryCredentialsConfig.client_secret
BigQueryCredentialsConfig.credentials
BigQueryCredentialsConfig.scopes


BigQueryTool
BigQueryTool.run_async()


BigQueryToolset
BigQueryToolset.close()
BigQueryToolset.get_tools()
- [google.adk.tools.crewai_tool module](google-adk.html#module-google.adk.tools.crewai_tool)
CrewaiTool
CrewaiTool.tool
- [google.adk.tools.enterprise_search_tool module](google-adk.html#module-google.adk.tools.enterprise_search_tool)
EnterpriseWebSearchTool
EnterpriseWebSearchTool.description
EnterpriseWebSearchTool.name
EnterpriseWebSearchTool.process_llm_request()
- [google.adk.tools.example_tool module](google-adk.html#module-google.adk.tools.example_tool)
ExampleTool
ExampleTool.examples
ExampleTool.process_llm_request()
- [google.adk.tools.exit_loop_tool module](google-adk.html#module-google.adk.tools.exit_loop_tool)
exit_loop()
- [google.adk.tools.function_tool module](google-adk.html#module-google.adk.tools.function_tool)
FunctionTool
FunctionTool.func
FunctionTool.run_async()
- [google.adk.tools.get_user_choice_tool module](google-adk.html#module-google.adk.tools.get_user_choice_tool)
get_user_choice()
- [google.adk.tools.google_api_tool module](google-adk.html#module-google.adk.tools.google_api_tool)
BigQueryToolset
CalendarToolset
DocsToolset
GmailToolset
GoogleApiTool
GoogleApiTool.configure_auth()
GoogleApiTool.configure_sa_auth()
GoogleApiTool.description
GoogleApiTool.name
GoogleApiTool.run_async()


GoogleApiToolset
GoogleApiToolset.close()
GoogleApiToolset.configure_auth()
GoogleApiToolset.configure_sa_auth()
GoogleApiToolset.get_tools()
GoogleApiToolset.set_tool_filter()


SheetsToolset
SlidesToolset
YoutubeToolset
- [google.adk.tools.google_search_tool module](google-adk.html#module-google.adk.tools.google_search_tool)
GoogleSearchTool
GoogleSearchTool.description
GoogleSearchTool.name
GoogleSearchTool.process_llm_request()
- [google.adk.tools.langchain_tool module](google-adk.html#module-google.adk.tools.langchain_tool)
LangchainTool
- [google.adk.tools.load_artifacts_tool module](google-adk.html#module-google.adk.tools.load_artifacts_tool)
LoadArtifactsTool
LoadArtifactsTool.description
LoadArtifactsTool.name
LoadArtifactsTool.process_llm_request()
LoadArtifactsTool.run_async()
- [google.adk.tools.load_memory_tool module](google-adk.html#module-google.adk.tools.load_memory_tool)
LoadMemoryResponse
LoadMemoryResponse.memories


LoadMemoryTool
LoadMemoryTool.process_llm_request()


load_memory()
- [google.adk.tools.load_web_page module](google-adk.html#module-google.adk.tools.load_web_page)
load_web_page()
- [google.adk.tools.long_running_tool module](google-adk.html#module-google.adk.tools.long_running_tool)
LongRunningFunctionTool
LongRunningFunctionTool.is_long_running
- [google.adk.tools.mcp_tool module](google-adk.html#module-google.adk.tools.mcp_tool)
MCPTool
MCPToolset
MCPToolset.close()
MCPToolset.get_tools()


SseConnectionParams
SseConnectionParams.url
SseConnectionParams.headers
SseConnectionParams.timeout
SseConnectionParams.sse_read_timeout
SseConnectionParams.headers
SseConnectionParams.sse_read_timeout
SseConnectionParams.timeout
SseConnectionParams.url


StdioConnectionParams
StdioConnectionParams.server_params
StdioConnectionParams.timeout
StdioConnectionParams.server_params
StdioConnectionParams.timeout


StreamableHTTPConnectionParams
StreamableHTTPConnectionParams.url
StreamableHTTPConnectionParams.headers
StreamableHTTPConnectionParams.timeout
StreamableHTTPConnectionParams.sse_read_timeout
StreamableHTTPConnectionParams.terminate_on_close
StreamableHTTPConnectionParams.headers
StreamableHTTPConnectionParams.sse_read_timeout
StreamableHTTPConnectionParams.terminate_on_close
StreamableHTTPConnectionParams.timeout
StreamableHTTPConnectionParams.url


adk_to_mcp_tool_type()
gemini_to_json_schema()
- [google.adk.tools.openapi_tool module](google-adk.html#module-google.adk.tools.openapi_tool)
OpenAPIToolset
OpenAPIToolset.close()
OpenAPIToolset.get_tool()
OpenAPIToolset.get_tools()


RestApiTool
RestApiTool.call()
RestApiTool.configure_auth_credential()
RestApiTool.configure_auth_scheme()
RestApiTool.description
RestApiTool.from_parsed_operation()
RestApiTool.from_parsed_operation_str()
RestApiTool.name
RestApiTool.run_async()
- [google.adk.tools.preload_memory_tool module](google-adk.html#module-google.adk.tools.preload_memory_tool)
PreloadMemoryTool
PreloadMemoryTool.description
PreloadMemoryTool.name
PreloadMemoryTool.process_llm_request()
- [google.adk.tools.retrieval module](google-adk.html#module-google.adk.tools.retrieval)
BaseRetrievalTool
BaseRetrievalTool.description
BaseRetrievalTool.name


FilesRetrieval
FilesRetrieval.description
FilesRetrieval.name


LlamaIndexRetrieval
LlamaIndexRetrieval.description
LlamaIndexRetrieval.name
LlamaIndexRetrieval.run_async()


VertexAiRagRetrieval
VertexAiRagRetrieval.description
VertexAiRagRetrieval.name
VertexAiRagRetrieval.process_llm_request()
VertexAiRagRetrieval.run_async()
- [google.adk.tools.tool_context module](google-adk.html#module-google.adk.tools.tool_context)
ToolContext
ToolContext.invocation_context
ToolContext.function_call_id
ToolContext.event_actions
ToolContext.actions
ToolContext.get_auth_response()
ToolContext.request_credential()
ToolContext.search_memory()
- [google.adk.tools.toolbox_toolset module](google-adk.html#module-google.adk.tools.toolbox_toolset)
ToolboxToolset
ToolboxToolset.close()
ToolboxToolset.get_tools()
- [google.adk.tools.transfer_to_agent_tool module](google-adk.html#module-google.adk.tools.transfer_to_agent_tool)
transfer_to_agent()
- [google.adk.tools.url_context_tool module](google-adk.html#module-google.adk.tools.url_context_tool)
UrlContextTool
UrlContextTool.description
UrlContextTool.name
UrlContextTool.process_llm_request()
- [google.adk.tools.vertex_ai_search_tool module](google-adk.html#module-google.adk.tools.vertex_ai_search_tool)
VertexAiSearchTool
VertexAiSearchTool.data_store_id
VertexAiSearchTool.search_engine_id
VertexAiSearchTool.process_llm_request()
- [google.adk.utils module](google-adk.html#module-google.adk.utils)
- [google.adk.version module](google-adk.html#module-google.adk.version)

- [Agent](google-adk.html#google.adk.agents.Agent)
- [BaseAgent](google-adk.html#google.adk.agents.BaseAgent)
BaseAgent.after_agent_callback
BaseAgent.before_agent_callback
BaseAgent.description
BaseAgent.name
BaseAgent.parent_agent
BaseAgent.sub_agents
BaseAgent.from_config()
BaseAgent.clone()
BaseAgent.find_agent()
BaseAgent.find_sub_agent()
BaseAgent.model_post_init()
BaseAgent.run_async()
BaseAgent.run_live()
BaseAgent.canonical_after_agent_callbacks
BaseAgent.canonical_before_agent_callbacks
BaseAgent.root_agent
- [InvocationContext](google-adk.html#google.adk.agents.InvocationContext)
InvocationContext.active_streaming_tools
InvocationContext.agent
InvocationContext.artifact_service
InvocationContext.branch
InvocationContext.credential_service
InvocationContext.end_invocation
InvocationContext.invocation_id
InvocationContext.live_request_queue
InvocationContext.memory_service
InvocationContext.plugin_manager
InvocationContext.run_config
InvocationContext.session
InvocationContext.session_service
InvocationContext.transcription_cache
InvocationContext.user_content
InvocationContext.increment_llm_call_count()
InvocationContext.model_post_init()
InvocationContext.app_name
InvocationContext.user_id
- [LiveRequest](google-adk.html#google.adk.agents.LiveRequest)
LiveRequest.activity_end
LiveRequest.activity_start
LiveRequest.blob
LiveRequest.close
LiveRequest.content
- [LiveRequestQueue](google-adk.html#google.adk.agents.LiveRequestQueue)
LiveRequestQueue.close()
LiveRequestQueue.get()
LiveRequestQueue.send()
LiveRequestQueue.send_activity_end()
LiveRequestQueue.send_activity_start()
LiveRequestQueue.send_content()
LiveRequestQueue.send_realtime()
- [LlmAgent](google-adk.html#google.adk.agents.LlmAgent)
LlmAgent.after_model_callback
LlmAgent.after_tool_callback
LlmAgent.before_model_callback
LlmAgent.before_tool_callback
LlmAgent.code_executor
LlmAgent.disallow_transfer_to_parent
LlmAgent.disallow_transfer_to_peers
LlmAgent.generate_content_config
LlmAgent.global_instruction
LlmAgent.include_contents
LlmAgent.input_schema
LlmAgent.instruction
LlmAgent.model
LlmAgent.output_key
LlmAgent.output_schema
LlmAgent.planner
LlmAgent.tools
LlmAgent.from_config()
LlmAgent.canonical_global_instruction()
LlmAgent.canonical_instruction()
LlmAgent.canonical_tools()
LlmAgent.canonical_after_model_callbacks
LlmAgent.canonical_after_tool_callbacks
LlmAgent.canonical_before_model_callbacks
LlmAgent.canonical_before_tool_callbacks
LlmAgent.canonical_model
- [LoopAgent](google-adk.html#google.adk.agents.LoopAgent)
LoopAgent.max_iterations
LoopAgent.from_config()
- [ParallelAgent](google-adk.html#google.adk.agents.ParallelAgent)
ParallelAgent.from_config()
- [RunConfig](google-adk.html#google.adk.agents.RunConfig)
RunConfig.enable_affective_dialog
RunConfig.input_audio_transcription
RunConfig.max_llm_calls
RunConfig.output_audio_transcription
RunConfig.proactivity
RunConfig.realtime_input_config
RunConfig.response_modalities
RunConfig.save_input_blobs_as_artifacts
RunConfig.session_resumption
RunConfig.speech_config
RunConfig.streaming_mode
RunConfig.support_cfc
RunConfig.validate_max_llm_calls
- [SequentialAgent](google-adk.html#google.adk.agents.SequentialAgent)
SequentialAgent.from_config()

`Agent`

`BaseAgent`

- [BaseAgent.after_agent_callback](google-adk.html#google.adk.agents.BaseAgent.after_agent_callback)
- [BaseAgent.before_agent_callback](google-adk.html#google.adk.agents.BaseAgent.before_agent_callback)
- [BaseAgent.description](google-adk.html#google.adk.agents.BaseAgent.description)
- [BaseAgent.name](google-adk.html#google.adk.agents.BaseAgent.name)
- [BaseAgent.parent_agent](google-adk.html#google.adk.agents.BaseAgent.parent_agent)
- [BaseAgent.sub_agents](google-adk.html#google.adk.agents.BaseAgent.sub_agents)
- [BaseAgent.from_config()](google-adk.html#google.adk.agents.BaseAgent.from_config)
- [BaseAgent.clone()](google-adk.html#google.adk.agents.BaseAgent.clone)
- [BaseAgent.find_agent()](google-adk.html#google.adk.agents.BaseAgent.find_agent)
- [BaseAgent.find_sub_agent()](google-adk.html#google.adk.agents.BaseAgent.find_sub_agent)
- [BaseAgent.model_post_init()](google-adk.html#google.adk.agents.BaseAgent.model_post_init)
- [BaseAgent.run_async()](google-adk.html#google.adk.agents.BaseAgent.run_async)
- [BaseAgent.run_live()](google-adk.html#google.adk.agents.BaseAgent.run_live)
- [BaseAgent.canonical_after_agent_callbacks](google-adk.html#google.adk.agents.BaseAgent.canonical_after_agent_callbacks)
- [BaseAgent.canonical_before_agent_callbacks](google-adk.html#google.adk.agents.BaseAgent.canonical_before_agent_callbacks)
- [BaseAgent.root_agent](google-adk.html#google.adk.agents.BaseAgent.root_agent)

`BaseAgent.after_agent_callback`

`BaseAgent.before_agent_callback`

`BaseAgent.description`

`BaseAgent.name`

`BaseAgent.parent_agent`

`BaseAgent.sub_agents`

`BaseAgent.from_config()`

`BaseAgent.clone()`

`BaseAgent.find_agent()`

`BaseAgent.find_sub_agent()`

`BaseAgent.model_post_init()`

`BaseAgent.run_async()`

`BaseAgent.run_live()`

`BaseAgent.canonical_after_agent_callbacks`

`BaseAgent.canonical_before_agent_callbacks`

`BaseAgent.root_agent`

`InvocationContext`

- [InvocationContext.active_streaming_tools](google-adk.html#google.adk.agents.InvocationContext.active_streaming_tools)
- [InvocationContext.agent](google-adk.html#google.adk.agents.InvocationContext.agent)
- [InvocationContext.artifact_service](google-adk.html#google.adk.agents.InvocationContext.artifact_service)
- [InvocationContext.branch](google-adk.html#google.adk.agents.InvocationContext.branch)
- [InvocationContext.credential_service](google-adk.html#google.adk.agents.InvocationContext.credential_service)
- [InvocationContext.end_invocation](google-adk.html#google.adk.agents.InvocationContext.end_invocation)
- [InvocationContext.invocation_id](google-adk.html#google.adk.agents.InvocationContext.invocation_id)
- [InvocationContext.live_request_queue](google-adk.html#google.adk.agents.InvocationContext.live_request_queue)
- [InvocationContext.memory_service](google-adk.html#google.adk.agents.InvocationContext.memory_service)
- [InvocationContext.plugin_manager](google-adk.html#google.adk.agents.InvocationContext.plugin_manager)
- [InvocationContext.run_config](google-adk.html#google.adk.agents.InvocationContext.run_config)
- [InvocationContext.session](google-adk.html#google.adk.agents.InvocationContext.session)
- [InvocationContext.session_service](google-adk.html#google.adk.agents.InvocationContext.session_service)
- [InvocationContext.transcription_cache](google-adk.html#google.adk.agents.InvocationContext.transcription_cache)
- [InvocationContext.user_content](google-adk.html#google.adk.agents.InvocationContext.user_content)
- [InvocationContext.increment_llm_call_count()](google-adk.html#google.adk.agents.InvocationContext.increment_llm_call_count)
- [InvocationContext.model_post_init()](google-adk.html#google.adk.agents.InvocationContext.model_post_init)
- [InvocationContext.app_name](google-adk.html#google.adk.agents.InvocationContext.app_name)
- [InvocationContext.user_id](google-adk.html#google.adk.agents.InvocationContext.user_id)

`InvocationContext.active_streaming_tools`

`InvocationContext.agent`

`InvocationContext.artifact_service`

`InvocationContext.branch`

`InvocationContext.credential_service`

`InvocationContext.end_invocation`

`InvocationContext.invocation_id`

`InvocationContext.live_request_queue`

`InvocationContext.memory_service`

`InvocationContext.plugin_manager`

`InvocationContext.run_config`

`InvocationContext.session`

`InvocationContext.session_service`

`InvocationContext.transcription_cache`

`InvocationContext.user_content`

`InvocationContext.increment_llm_call_count()`

`InvocationContext.model_post_init()`

`InvocationContext.app_name`

`InvocationContext.user_id`

`LiveRequest`

- [LiveRequest.activity_end](google-adk.html#google.adk.agents.LiveRequest.activity_end)
- [LiveRequest.activity_start](google-adk.html#google.adk.agents.LiveRequest.activity_start)
- [LiveRequest.blob](google-adk.html#google.adk.agents.LiveRequest.blob)
- [LiveRequest.close](google-adk.html#google.adk.agents.LiveRequest.close)
- [LiveRequest.content](google-adk.html#google.adk.agents.LiveRequest.content)

`LiveRequest.activity_end`

`LiveRequest.activity_start`

`LiveRequest.blob`

`LiveRequest.close`

`LiveRequest.content`

`LiveRequestQueue`

- [LiveRequestQueue.close()](google-adk.html#google.adk.agents.LiveRequestQueue.close)
- [LiveRequestQueue.get()](google-adk.html#google.adk.agents.LiveRequestQueue.get)
- [LiveRequestQueue.send()](google-adk.html#google.adk.agents.LiveRequestQueue.send)
- [LiveRequestQueue.send_activity_end()](google-adk.html#google.adk.agents.LiveRequestQueue.send_activity_end)
- [LiveRequestQueue.send_activity_start()](google-adk.html#google.adk.agents.LiveRequestQueue.send_activity_start)
- [LiveRequestQueue.send_content()](google-adk.html#google.adk.agents.LiveRequestQueue.send_content)
- [LiveRequestQueue.send_realtime()](google-adk.html#google.adk.agents.LiveRequestQueue.send_realtime)

`LiveRequestQueue.close()`

`LiveRequestQueue.get()`

`LiveRequestQueue.send()`

`LiveRequestQueue.send_activity_end()`

`LiveRequestQueue.send_activity_start()`

`LiveRequestQueue.send_content()`

`LiveRequestQueue.send_realtime()`

`LlmAgent`

- [LlmAgent.after_model_callback](google-adk.html#google.adk.agents.LlmAgent.after_model_callback)
- [LlmAgent.after_tool_callback](google-adk.html#google.adk.agents.LlmAgent.after_tool_callback)
- [LlmAgent.before_model_callback](google-adk.html#google.adk.agents.LlmAgent.before_model_callback)
- [LlmAgent.before_tool_callback](google-adk.html#google.adk.agents.LlmAgent.before_tool_callback)
- [LlmAgent.code_executor](google-adk.html#google.adk.agents.LlmAgent.code_executor)
- [LlmAgent.disallow_transfer_to_parent](google-adk.html#google.adk.agents.LlmAgent.disallow_transfer_to_parent)
- [LlmAgent.disallow_transfer_to_peers](google-adk.html#google.adk.agents.LlmAgent.disallow_transfer_to_peers)
- [LlmAgent.generate_content_config](google-adk.html#google.adk.agents.LlmAgent.generate_content_config)
- [LlmAgent.global_instruction](google-adk.html#google.adk.agents.LlmAgent.global_instruction)
- [LlmAgent.include_contents](google-adk.html#google.adk.agents.LlmAgent.include_contents)
- [LlmAgent.input_schema](google-adk.html#google.adk.agents.LlmAgent.input_schema)
- [LlmAgent.instruction](google-adk.html#google.adk.agents.LlmAgent.instruction)
- [LlmAgent.model](google-adk.html#google.adk.agents.LlmAgent.model)
- [LlmAgent.output_key](google-adk.html#google.adk.agents.LlmAgent.output_key)
- [LlmAgent.output_schema](google-adk.html#google.adk.agents.LlmAgent.output_schema)
- [LlmAgent.planner](google-adk.html#google.adk.agents.LlmAgent.planner)
- [LlmAgent.tools](google-adk.html#google.adk.agents.LlmAgent.tools)
- [LlmAgent.from_config()](google-adk.html#google.adk.agents.LlmAgent.from_config)
- [LlmAgent.canonical_global_instruction()](google-adk.html#google.adk.agents.LlmAgent.canonical_global_instruction)
- [LlmAgent.canonical_instruction()](google-adk.html#google.adk.agents.LlmAgent.canonical_instruction)
- [LlmAgent.canonical_tools()](google-adk.html#google.adk.agents.LlmAgent.canonical_tools)
- [LlmAgent.canonical_after_model_callbacks](google-adk.html#google.adk.agents.LlmAgent.canonical_after_model_callbacks)
- [LlmAgent.canonical_after_tool_callbacks](google-adk.html#google.adk.agents.LlmAgent.canonical_after_tool_callbacks)
- [LlmAgent.canonical_before_model_callbacks](google-adk.html#google.adk.agents.LlmAgent.canonical_before_model_callbacks)
- [LlmAgent.canonical_before_tool_callbacks](google-adk.html#google.adk.agents.LlmAgent.canonical_before_tool_callbacks)
- [LlmAgent.canonical_model](google-adk.html#google.adk.agents.LlmAgent.canonical_model)

`LlmAgent.after_model_callback`

`LlmAgent.after_tool_callback`

`LlmAgent.before_model_callback`

`LlmAgent.before_tool_callback`

`LlmAgent.code_executor`

`LlmAgent.disallow_transfer_to_parent`

`LlmAgent.disallow_transfer_to_peers`

`LlmAgent.generate_content_config`

`LlmAgent.global_instruction`

`LlmAgent.include_contents`

`LlmAgent.input_schema`

`LlmAgent.instruction`

`LlmAgent.model`

`LlmAgent.output_key`

`LlmAgent.output_schema`

`LlmAgent.planner`

`LlmAgent.tools`

`LlmAgent.from_config()`

`LlmAgent.canonical_global_instruction()`

`LlmAgent.canonical_instruction()`

`LlmAgent.canonical_tools()`

`LlmAgent.canonical_after_model_callbacks`

`LlmAgent.canonical_after_tool_callbacks`

`LlmAgent.canonical_before_model_callbacks`

`LlmAgent.canonical_before_tool_callbacks`

`LlmAgent.canonical_model`

`LoopAgent`

- [LoopAgent.max_iterations](google-adk.html#google.adk.agents.LoopAgent.max_iterations)
- [LoopAgent.from_config()](google-adk.html#google.adk.agents.LoopAgent.from_config)

`LoopAgent.max_iterations`

`LoopAgent.from_config()`

`ParallelAgent`

- [ParallelAgent.from_config()](google-adk.html#google.adk.agents.ParallelAgent.from_config)

`ParallelAgent.from_config()`

`RunConfig`

- [RunConfig.enable_affective_dialog](google-adk.html#google.adk.agents.RunConfig.enable_affective_dialog)
- [RunConfig.input_audio_transcription](google-adk.html#google.adk.agents.RunConfig.input_audio_transcription)
- [RunConfig.max_llm_calls](google-adk.html#google.adk.agents.RunConfig.max_llm_calls)
- [RunConfig.output_audio_transcription](google-adk.html#google.adk.agents.RunConfig.output_audio_transcription)
- [RunConfig.proactivity](google-adk.html#google.adk.agents.RunConfig.proactivity)
- [RunConfig.realtime_input_config](google-adk.html#google.adk.agents.RunConfig.realtime_input_config)
- [RunConfig.response_modalities](google-adk.html#google.adk.agents.RunConfig.response_modalities)
- [RunConfig.save_input_blobs_as_artifacts](google-adk.html#google.adk.agents.RunConfig.save_input_blobs_as_artifacts)
- [RunConfig.session_resumption](google-adk.html#google.adk.agents.RunConfig.session_resumption)
- [RunConfig.speech_config](google-adk.html#google.adk.agents.RunConfig.speech_config)
- [RunConfig.streaming_mode](google-adk.html#google.adk.agents.RunConfig.streaming_mode)
- [RunConfig.support_cfc](google-adk.html#google.adk.agents.RunConfig.support_cfc)
- [RunConfig.validate_max_llm_calls](google-adk.html#google.adk.agents.RunConfig.validate_max_llm_calls)

`RunConfig.enable_affective_dialog`

`RunConfig.input_audio_transcription`

`RunConfig.max_llm_calls`

`RunConfig.output_audio_transcription`

`RunConfig.proactivity`

`RunConfig.realtime_input_config`

`RunConfig.response_modalities`

`RunConfig.save_input_blobs_as_artifacts`

`RunConfig.session_resumption`

`RunConfig.speech_config`

`RunConfig.streaming_mode`

`RunConfig.support_cfc`

`RunConfig.validate_max_llm_calls`

`SequentialAgent`

- [SequentialAgent.from_config()](google-adk.html#google.adk.agents.SequentialAgent.from_config)

`SequentialAgent.from_config()`

- [BaseArtifactService](google-adk.html#google.adk.artifacts.BaseArtifactService)
BaseArtifactService.delete_artifact()
BaseArtifactService.list_artifact_keys()
BaseArtifactService.list_versions()
BaseArtifactService.load_artifact()
BaseArtifactService.save_artifact()
- [GcsArtifactService](google-adk.html#google.adk.artifacts.GcsArtifactService)
GcsArtifactService.delete_artifact()
GcsArtifactService.list_artifact_keys()
GcsArtifactService.list_versions()
GcsArtifactService.load_artifact()
GcsArtifactService.save_artifact()
- [InMemoryArtifactService](google-adk.html#google.adk.artifacts.InMemoryArtifactService)
InMemoryArtifactService.artifacts
InMemoryArtifactService.delete_artifact()
InMemoryArtifactService.list_artifact_keys()
InMemoryArtifactService.list_versions()
InMemoryArtifactService.load_artifact()
InMemoryArtifactService.save_artifact()

`BaseArtifactService`

- [BaseArtifactService.delete_artifact()](google-adk.html#google.adk.artifacts.BaseArtifactService.delete_artifact)
- [BaseArtifactService.list_artifact_keys()](google-adk.html#google.adk.artifacts.BaseArtifactService.list_artifact_keys)
- [BaseArtifactService.list_versions()](google-adk.html#google.adk.artifacts.BaseArtifactService.list_versions)
- [BaseArtifactService.load_artifact()](google-adk.html#google.adk.artifacts.BaseArtifactService.load_artifact)
- [BaseArtifactService.save_artifact()](google-adk.html#google.adk.artifacts.BaseArtifactService.save_artifact)

`BaseArtifactService.delete_artifact()`

`BaseArtifactService.list_artifact_keys()`

`BaseArtifactService.list_versions()`

`BaseArtifactService.load_artifact()`

`BaseArtifactService.save_artifact()`

`GcsArtifactService`

- [GcsArtifactService.delete_artifact()](google-adk.html#google.adk.artifacts.GcsArtifactService.delete_artifact)
- [GcsArtifactService.list_artifact_keys()](google-adk.html#google.adk.artifacts.GcsArtifactService.list_artifact_keys)
- [GcsArtifactService.list_versions()](google-adk.html#google.adk.artifacts.GcsArtifactService.list_versions)
- [GcsArtifactService.load_artifact()](google-adk.html#google.adk.artifacts.GcsArtifactService.load_artifact)
- [GcsArtifactService.save_artifact()](google-adk.html#google.adk.artifacts.GcsArtifactService.save_artifact)

`GcsArtifactService.delete_artifact()`

`GcsArtifactService.list_artifact_keys()`

`GcsArtifactService.list_versions()`

`GcsArtifactService.load_artifact()`

`GcsArtifactService.save_artifact()`

`InMemoryArtifactService`

- [InMemoryArtifactService.artifacts](google-adk.html#google.adk.artifacts.InMemoryArtifactService.artifacts)
- [InMemoryArtifactService.delete_artifact()](google-adk.html#google.adk.artifacts.InMemoryArtifactService.delete_artifact)
- [InMemoryArtifactService.list_artifact_keys()](google-adk.html#google.adk.artifacts.InMemoryArtifactService.list_artifact_keys)
- [InMemoryArtifactService.list_versions()](google-adk.html#google.adk.artifacts.InMemoryArtifactService.list_versions)
- [InMemoryArtifactService.load_artifact()](google-adk.html#google.adk.artifacts.InMemoryArtifactService.load_artifact)
- [InMemoryArtifactService.save_artifact()](google-adk.html#google.adk.artifacts.InMemoryArtifactService.save_artifact)

`InMemoryArtifactService.artifacts`

`InMemoryArtifactService.delete_artifact()`

`InMemoryArtifactService.list_artifact_keys()`

`InMemoryArtifactService.list_versions()`

`InMemoryArtifactService.load_artifact()`

`InMemoryArtifactService.save_artifact()`

- [BaseCodeExecutor](google-adk.html#google.adk.code_executors.BaseCodeExecutor)
BaseCodeExecutor.optimize_data_file
BaseCodeExecutor.stateful
BaseCodeExecutor.error_retry_attempts
BaseCodeExecutor.code_block_delimiters
BaseCodeExecutor.execution_result_delimiters
BaseCodeExecutor.code_block_delimiters
BaseCodeExecutor.error_retry_attempts
BaseCodeExecutor.execution_result_delimiters
BaseCodeExecutor.optimize_data_file
BaseCodeExecutor.stateful
BaseCodeExecutor.execute_code()
- [BuiltInCodeExecutor](google-adk.html#google.adk.code_executors.BuiltInCodeExecutor)
BuiltInCodeExecutor.execute_code()
BuiltInCodeExecutor.process_llm_request()
- [CodeExecutorContext](google-adk.html#google.adk.code_executors.CodeExecutorContext)
CodeExecutorContext.add_input_files()
CodeExecutorContext.add_processed_file_names()
CodeExecutorContext.clear_input_files()
CodeExecutorContext.get_error_count()
CodeExecutorContext.get_execution_id()
CodeExecutorContext.get_input_files()
CodeExecutorContext.get_processed_file_names()
CodeExecutorContext.get_state_delta()
CodeExecutorContext.increment_error_count()
CodeExecutorContext.reset_error_count()
CodeExecutorContext.set_execution_id()
CodeExecutorContext.update_code_execution_result()
- [ContainerCodeExecutor](google-adk.html#google.adk.code_executors.ContainerCodeExecutor)
ContainerCodeExecutor.base_url
ContainerCodeExecutor.image
ContainerCodeExecutor.docker_path
ContainerCodeExecutor.base_url
ContainerCodeExecutor.docker_path
ContainerCodeExecutor.image
ContainerCodeExecutor.optimize_data_file
ContainerCodeExecutor.stateful
ContainerCodeExecutor.execute_code()
ContainerCodeExecutor.model_post_init()
- [UnsafeLocalCodeExecutor](google-adk.html#google.adk.code_executors.UnsafeLocalCodeExecutor)
UnsafeLocalCodeExecutor.optimize_data_file
UnsafeLocalCodeExecutor.stateful
UnsafeLocalCodeExecutor.execute_code()
- [VertexAiCodeExecutor](google-adk.html#google.adk.code_executors.VertexAiCodeExecutor)
VertexAiCodeExecutor.resource_name
VertexAiCodeExecutor.resource_name
VertexAiCodeExecutor.execute_code()
VertexAiCodeExecutor.model_post_init()

`BaseCodeExecutor`

- [BaseCodeExecutor.optimize_data_file](google-adk.html#google.adk.code_executors.BaseCodeExecutor.optimize_data_file)
- [BaseCodeExecutor.stateful](google-adk.html#google.adk.code_executors.BaseCodeExecutor.stateful)
- [BaseCodeExecutor.error_retry_attempts](google-adk.html#google.adk.code_executors.BaseCodeExecutor.error_retry_attempts)
- [BaseCodeExecutor.code_block_delimiters](google-adk.html#google.adk.code_executors.BaseCodeExecutor.code_block_delimiters)
- [BaseCodeExecutor.execution_result_delimiters](google-adk.html#google.adk.code_executors.BaseCodeExecutor.execution_result_delimiters)
- [BaseCodeExecutor.code_block_delimiters](google-adk.html#id0)
- [BaseCodeExecutor.error_retry_attempts](google-adk.html#id9)
- [BaseCodeExecutor.execution_result_delimiters](google-adk.html#id10)
- [BaseCodeExecutor.optimize_data_file](google-adk.html#id11)
- [BaseCodeExecutor.stateful](google-adk.html#id12)
- [BaseCodeExecutor.execute_code()](google-adk.html#google.adk.code_executors.BaseCodeExecutor.execute_code)

`BaseCodeExecutor.optimize_data_file`

`BaseCodeExecutor.stateful`

`BaseCodeExecutor.error_retry_attempts`

`BaseCodeExecutor.code_block_delimiters`

`BaseCodeExecutor.execution_result_delimiters`

`BaseCodeExecutor.code_block_delimiters`

`BaseCodeExecutor.error_retry_attempts`

`BaseCodeExecutor.execution_result_delimiters`

`BaseCodeExecutor.optimize_data_file`

`BaseCodeExecutor.stateful`

`BaseCodeExecutor.execute_code()`

`BuiltInCodeExecutor`

- [BuiltInCodeExecutor.execute_code()](google-adk.html#google.adk.code_executors.BuiltInCodeExecutor.execute_code)
- [BuiltInCodeExecutor.process_llm_request()](google-adk.html#google.adk.code_executors.BuiltInCodeExecutor.process_llm_request)

`BuiltInCodeExecutor.execute_code()`

`BuiltInCodeExecutor.process_llm_request()`

`CodeExecutorContext`

- [CodeExecutorContext.add_input_files()](google-adk.html#google.adk.code_executors.CodeExecutorContext.add_input_files)
- [CodeExecutorContext.add_processed_file_names()](google-adk.html#google.adk.code_executors.CodeExecutorContext.add_processed_file_names)
- [CodeExecutorContext.clear_input_files()](google-adk.html#google.adk.code_executors.CodeExecutorContext.clear_input_files)
- [CodeExecutorContext.get_error_count()](google-adk.html#google.adk.code_executors.CodeExecutorContext.get_error_count)
- [CodeExecutorContext.get_execution_id()](google-adk.html#google.adk.code_executors.CodeExecutorContext.get_execution_id)
- [CodeExecutorContext.get_input_files()](google-adk.html#google.adk.code_executors.CodeExecutorContext.get_input_files)
- [CodeExecutorContext.get_processed_file_names()](google-adk.html#google.adk.code_executors.CodeExecutorContext.get_processed_file_names)
- [CodeExecutorContext.get_state_delta()](google-adk.html#google.adk.code_executors.CodeExecutorContext.get_state_delta)
- [CodeExecutorContext.increment_error_count()](google-adk.html#google.adk.code_executors.CodeExecutorContext.increment_error_count)
- [CodeExecutorContext.reset_error_count()](google-adk.html#google.adk.code_executors.CodeExecutorContext.reset_error_count)
- [CodeExecutorContext.set_execution_id()](google-adk.html#google.adk.code_executors.CodeExecutorContext.set_execution_id)
- [CodeExecutorContext.update_code_execution_result()](google-adk.html#google.adk.code_executors.CodeExecutorContext.update_code_execution_result)

`CodeExecutorContext.add_input_files()`

`CodeExecutorContext.add_processed_file_names()`

`CodeExecutorContext.clear_input_files()`

`CodeExecutorContext.get_error_count()`

`CodeExecutorContext.get_execution_id()`

`CodeExecutorContext.get_input_files()`

`CodeExecutorContext.get_processed_file_names()`

`CodeExecutorContext.get_state_delta()`

`CodeExecutorContext.increment_error_count()`

`CodeExecutorContext.reset_error_count()`

`CodeExecutorContext.set_execution_id()`

`CodeExecutorContext.update_code_execution_result()`

`ContainerCodeExecutor`

- [ContainerCodeExecutor.base_url](google-adk.html#google.adk.code_executors.ContainerCodeExecutor.base_url)
- [ContainerCodeExecutor.image](google-adk.html#google.adk.code_executors.ContainerCodeExecutor.image)
- [ContainerCodeExecutor.docker_path](google-adk.html#google.adk.code_executors.ContainerCodeExecutor.docker_path)
- [ContainerCodeExecutor.base_url](google-adk.html#id13)
- [ContainerCodeExecutor.docker_path](google-adk.html#id14)
- [ContainerCodeExecutor.image](google-adk.html#id15)
- [ContainerCodeExecutor.optimize_data_file](google-adk.html#google.adk.code_executors.ContainerCodeExecutor.optimize_data_file)
- [ContainerCodeExecutor.stateful](google-adk.html#google.adk.code_executors.ContainerCodeExecutor.stateful)
- [ContainerCodeExecutor.execute_code()](google-adk.html#google.adk.code_executors.ContainerCodeExecutor.execute_code)
- [ContainerCodeExecutor.model_post_init()](google-adk.html#google.adk.code_executors.ContainerCodeExecutor.model_post_init)

`ContainerCodeExecutor.base_url`

`ContainerCodeExecutor.image`

`ContainerCodeExecutor.docker_path`

`ContainerCodeExecutor.base_url`

`ContainerCodeExecutor.docker_path`

`ContainerCodeExecutor.image`

`ContainerCodeExecutor.optimize_data_file`

`ContainerCodeExecutor.stateful`

`ContainerCodeExecutor.execute_code()`

`ContainerCodeExecutor.model_post_init()`

`UnsafeLocalCodeExecutor`

- [UnsafeLocalCodeExecutor.optimize_data_file](google-adk.html#google.adk.code_executors.UnsafeLocalCodeExecutor.optimize_data_file)
- [UnsafeLocalCodeExecutor.stateful](google-adk.html#google.adk.code_executors.UnsafeLocalCodeExecutor.stateful)
- [UnsafeLocalCodeExecutor.execute_code()](google-adk.html#google.adk.code_executors.UnsafeLocalCodeExecutor.execute_code)

`UnsafeLocalCodeExecutor.optimize_data_file`

`UnsafeLocalCodeExecutor.stateful`

`UnsafeLocalCodeExecutor.execute_code()`

`VertexAiCodeExecutor`

- [VertexAiCodeExecutor.resource_name](google-adk.html#google.adk.code_executors.VertexAiCodeExecutor.resource_name)
- [VertexAiCodeExecutor.resource_name](google-adk.html#id16)
- [VertexAiCodeExecutor.execute_code()](google-adk.html#google.adk.code_executors.VertexAiCodeExecutor.execute_code)
- [VertexAiCodeExecutor.model_post_init()](google-adk.html#google.adk.code_executors.VertexAiCodeExecutor.model_post_init)

`VertexAiCodeExecutor.resource_name`

`VertexAiCodeExecutor.resource_name`

`VertexAiCodeExecutor.execute_code()`

`VertexAiCodeExecutor.model_post_init()`

- [AgentEvaluator](google-adk.html#google.adk.evaluation.AgentEvaluator)
AgentEvaluator.evaluate()
AgentEvaluator.evaluate_eval_set()
AgentEvaluator.find_config_for_test_file()
AgentEvaluator.migrate_eval_data_to_new_schema()

`AgentEvaluator`

- [AgentEvaluator.evaluate()](google-adk.html#google.adk.evaluation.AgentEvaluator.evaluate)
- [AgentEvaluator.evaluate_eval_set()](google-adk.html#google.adk.evaluation.AgentEvaluator.evaluate_eval_set)
- [AgentEvaluator.find_config_for_test_file()](google-adk.html#google.adk.evaluation.AgentEvaluator.find_config_for_test_file)
- [AgentEvaluator.migrate_eval_data_to_new_schema()](google-adk.html#google.adk.evaluation.AgentEvaluator.migrate_eval_data_to_new_schema)

`AgentEvaluator.evaluate()`

`AgentEvaluator.evaluate_eval_set()`

`AgentEvaluator.find_config_for_test_file()`

`AgentEvaluator.migrate_eval_data_to_new_schema()`

- [Event](google-adk.html#google.adk.events.Event)
Event.invocation_id
Event.author
Event.actions
Event.long_running_tool_ids
Event.branch
Event.id
Event.timestamp
Event.get_function_calls
Event.actions
Event.author
Event.branch
Event.id
Event.invocation_id
Event.long_running_tool_ids
Event.timestamp
Event.new_id()
Event.get_function_calls()
Event.get_function_responses()
Event.has_trailing_code_execution_result()
Event.is_final_response()
Event.model_post_init()
- [EventActions](google-adk.html#google.adk.events.EventActions)
EventActions.artifact_delta
EventActions.escalate
EventActions.requested_auth_configs
EventActions.skip_summarization
EventActions.state_delta
EventActions.transfer_to_agent

`Event`

- [Event.invocation_id](google-adk.html#google.adk.events.Event.invocation_id)
- [Event.author](google-adk.html#google.adk.events.Event.author)
- [Event.actions](google-adk.html#google.adk.events.Event.actions)
- [Event.long_running_tool_ids](google-adk.html#google.adk.events.Event.long_running_tool_ids)
- [Event.branch](google-adk.html#google.adk.events.Event.branch)
- [Event.id](google-adk.html#google.adk.events.Event.id)
- [Event.timestamp](google-adk.html#google.adk.events.Event.timestamp)
- [Event.get_function_calls](google-adk.html#google.adk.events.Event.get_function_calls)
- [Event.actions](google-adk.html#id17)
- [Event.author](google-adk.html#id18)
- [Event.branch](google-adk.html#id19)
- [Event.id](google-adk.html#id20)
- [Event.invocation_id](google-adk.html#id21)
- [Event.long_running_tool_ids](google-adk.html#id22)
- [Event.timestamp](google-adk.html#id23)
- [Event.new_id()](google-adk.html#google.adk.events.Event.new_id)
- [Event.get_function_calls()](google-adk.html#id24)
- [Event.get_function_responses()](google-adk.html#google.adk.events.Event.get_function_responses)
- [Event.has_trailing_code_execution_result()](google-adk.html#google.adk.events.Event.has_trailing_code_execution_result)
- [Event.is_final_response()](google-adk.html#google.adk.events.Event.is_final_response)
- [Event.model_post_init()](google-adk.html#google.adk.events.Event.model_post_init)

`Event.invocation_id`

`Event.author`

`Event.actions`

`Event.long_running_tool_ids`

`Event.branch`

`Event.id`

`Event.timestamp`

`Event.get_function_calls`

`Event.actions`

`Event.author`

`Event.branch`

`Event.id`

`Event.invocation_id`

`Event.long_running_tool_ids`

`Event.timestamp`

`Event.new_id()`

`Event.get_function_calls()`

`Event.get_function_responses()`

`Event.has_trailing_code_execution_result()`

`Event.is_final_response()`

`Event.model_post_init()`

`EventActions`

- [EventActions.artifact_delta](google-adk.html#google.adk.events.EventActions.artifact_delta)
- [EventActions.escalate](google-adk.html#google.adk.events.EventActions.escalate)
- [EventActions.requested_auth_configs](google-adk.html#google.adk.events.EventActions.requested_auth_configs)
- [EventActions.skip_summarization](google-adk.html#google.adk.events.EventActions.skip_summarization)
- [EventActions.state_delta](google-adk.html#google.adk.events.EventActions.state_delta)
- [EventActions.transfer_to_agent](google-adk.html#google.adk.events.EventActions.transfer_to_agent)

`EventActions.artifact_delta`

`EventActions.escalate`

`EventActions.requested_auth_configs`

`EventActions.skip_summarization`

`EventActions.state_delta`

`EventActions.transfer_to_agent`

- [BaseExampleProvider](google-adk.html#google.adk.examples.BaseExampleProvider)
BaseExampleProvider.get_examples()
- [Example](google-adk.html#google.adk.examples.Example)
Example.input
Example.output
Example.input
Example.output
- [VertexAiExampleStore](google-adk.html#google.adk.examples.VertexAiExampleStore)
VertexAiExampleStore.get_examples()

`BaseExampleProvider`

- [BaseExampleProvider.get_examples()](google-adk.html#google.adk.examples.BaseExampleProvider.get_examples)

`BaseExampleProvider.get_examples()`

`Example`

- [Example.input](google-adk.html#google.adk.examples.Example.input)
- [Example.output](google-adk.html#google.adk.examples.Example.output)
- [Example.input](google-adk.html#id25)
- [Example.output](google-adk.html#id26)

`Example.input`

`Example.output`

`Example.input`

`Example.output`

`VertexAiExampleStore`

- [VertexAiExampleStore.get_examples()](google-adk.html#google.adk.examples.VertexAiExampleStore.get_examples)

`VertexAiExampleStore.get_examples()`

- [BaseMemoryService](google-adk.html#google.adk.memory.BaseMemoryService)
BaseMemoryService.add_session_to_memory()
BaseMemoryService.search_memory()
- [InMemoryMemoryService](google-adk.html#google.adk.memory.InMemoryMemoryService)
InMemoryMemoryService.add_session_to_memory()
InMemoryMemoryService.search_memory()
- [VertexAiMemoryBankService](google-adk.html#google.adk.memory.VertexAiMemoryBankService)
VertexAiMemoryBankService.add_session_to_memory()
VertexAiMemoryBankService.search_memory()
- [VertexAiRagMemoryService](google-adk.html#google.adk.memory.VertexAiRagMemoryService)
VertexAiRagMemoryService.add_session_to_memory()
VertexAiRagMemoryService.search_memory()

`BaseMemoryService`

- [BaseMemoryService.add_session_to_memory()](google-adk.html#google.adk.memory.BaseMemoryService.add_session_to_memory)
- [BaseMemoryService.search_memory()](google-adk.html#google.adk.memory.BaseMemoryService.search_memory)

`BaseMemoryService.add_session_to_memory()`

`BaseMemoryService.search_memory()`

`InMemoryMemoryService`

- [InMemoryMemoryService.add_session_to_memory()](google-adk.html#google.adk.memory.InMemoryMemoryService.add_session_to_memory)
- [InMemoryMemoryService.search_memory()](google-adk.html#google.adk.memory.InMemoryMemoryService.search_memory)

`InMemoryMemoryService.add_session_to_memory()`

`InMemoryMemoryService.search_memory()`

`VertexAiMemoryBankService`

- [VertexAiMemoryBankService.add_session_to_memory()](google-adk.html#google.adk.memory.VertexAiMemoryBankService.add_session_to_memory)
- [VertexAiMemoryBankService.search_memory()](google-adk.html#google.adk.memory.VertexAiMemoryBankService.search_memory)

`VertexAiMemoryBankService.add_session_to_memory()`

`VertexAiMemoryBankService.search_memory()`

`VertexAiRagMemoryService`

- [VertexAiRagMemoryService.add_session_to_memory()](google-adk.html#google.adk.memory.VertexAiRagMemoryService.add_session_to_memory)
- [VertexAiRagMemoryService.search_memory()](google-adk.html#google.adk.memory.VertexAiRagMemoryService.search_memory)

`VertexAiRagMemoryService.add_session_to_memory()`

`VertexAiRagMemoryService.search_memory()`

- [BaseLlm](google-adk.html#google.adk.models.BaseLlm)
BaseLlm.model
BaseLlm.model
BaseLlm.supported_models()
BaseLlm.connect()
BaseLlm.generate_content_async()
- [Gemini](google-adk.html#google.adk.models.Gemini)
Gemini.model
Gemini.model
Gemini.retry_options
Gemini.supported_models()
Gemini.connect()
Gemini.generate_content_async()
Gemini.api_client
- [LLMRegistry](google-adk.html#google.adk.models.LLMRegistry)
LLMRegistry.new_llm()
LLMRegistry.register()
LLMRegistry.resolve()

`BaseLlm`

- [BaseLlm.model](google-adk.html#google.adk.models.BaseLlm.model)
- [BaseLlm.model](google-adk.html#id27)
- [BaseLlm.supported_models()](google-adk.html#google.adk.models.BaseLlm.supported_models)
- [BaseLlm.connect()](google-adk.html#google.adk.models.BaseLlm.connect)
- [BaseLlm.generate_content_async()](google-adk.html#google.adk.models.BaseLlm.generate_content_async)

`BaseLlm.model`

`BaseLlm.model`

`BaseLlm.supported_models()`

`BaseLlm.connect()`

`BaseLlm.generate_content_async()`

`Gemini`

- [Gemini.model](google-adk.html#google.adk.models.Gemini.model)
- [Gemini.model](google-adk.html#id28)
- [Gemini.retry_options](google-adk.html#google.adk.models.Gemini.retry_options)
- [Gemini.supported_models()](google-adk.html#google.adk.models.Gemini.supported_models)
- [Gemini.connect()](google-adk.html#google.adk.models.Gemini.connect)
- [Gemini.generate_content_async()](google-adk.html#google.adk.models.Gemini.generate_content_async)
- [Gemini.api_client](google-adk.html#google.adk.models.Gemini.api_client)

`Gemini.model`

`Gemini.model`

`Gemini.retry_options`

`Gemini.supported_models()`

`Gemini.connect()`

`Gemini.generate_content_async()`

`Gemini.api_client`

`LLMRegistry`

- [LLMRegistry.new_llm()](google-adk.html#google.adk.models.LLMRegistry.new_llm)
- [LLMRegistry.register()](google-adk.html#google.adk.models.LLMRegistry.register)
- [LLMRegistry.resolve()](google-adk.html#google.adk.models.LLMRegistry.resolve)

`LLMRegistry.new_llm()`

`LLMRegistry.register()`

`LLMRegistry.resolve()`

- [BasePlanner](google-adk.html#google.adk.planners.BasePlanner)
BasePlanner.build_planning_instruction()
BasePlanner.process_planning_response()
- [BuiltInPlanner](google-adk.html#google.adk.planners.BuiltInPlanner)
BuiltInPlanner.thinking_config
BuiltInPlanner.apply_thinking_config()
BuiltInPlanner.build_planning_instruction()
BuiltInPlanner.process_planning_response()
BuiltInPlanner.thinking_config
- [PlanReActPlanner](google-adk.html#google.adk.planners.PlanReActPlanner)
PlanReActPlanner.build_planning_instruction()
PlanReActPlanner.process_planning_response()

`BasePlanner`

- [BasePlanner.build_planning_instruction()](google-adk.html#google.adk.planners.BasePlanner.build_planning_instruction)
- [BasePlanner.process_planning_response()](google-adk.html#google.adk.planners.BasePlanner.process_planning_response)

`BasePlanner.build_planning_instruction()`

`BasePlanner.process_planning_response()`

`BuiltInPlanner`

- [BuiltInPlanner.thinking_config](google-adk.html#google.adk.planners.BuiltInPlanner.thinking_config)
- [BuiltInPlanner.apply_thinking_config()](google-adk.html#google.adk.planners.BuiltInPlanner.apply_thinking_config)
- [BuiltInPlanner.build_planning_instruction()](google-adk.html#google.adk.planners.BuiltInPlanner.build_planning_instruction)
- [BuiltInPlanner.process_planning_response()](google-adk.html#google.adk.planners.BuiltInPlanner.process_planning_response)
- [BuiltInPlanner.thinking_config](google-adk.html#id34)

`BuiltInPlanner.thinking_config`

`BuiltInPlanner.apply_thinking_config()`

`BuiltInPlanner.build_planning_instruction()`

`BuiltInPlanner.process_planning_response()`

`BuiltInPlanner.thinking_config`

`PlanReActPlanner`

- [PlanReActPlanner.build_planning_instruction()](google-adk.html#google.adk.planners.PlanReActPlanner.build_planning_instruction)
- [PlanReActPlanner.process_planning_response()](google-adk.html#google.adk.planners.PlanReActPlanner.process_planning_response)

`PlanReActPlanner.build_planning_instruction()`

`PlanReActPlanner.process_planning_response()`

- [BasePlugin](google-adk.html#google.adk.plugins.BasePlugin)
BasePlugin.after_agent_callback()
BasePlugin.after_model_callback()
BasePlugin.after_run_callback()
BasePlugin.after_tool_callback()
BasePlugin.before_agent_callback()
BasePlugin.before_model_callback()
BasePlugin.before_run_callback()
BasePlugin.before_tool_callback()
BasePlugin.on_event_callback()
BasePlugin.on_model_error_callback()
BasePlugin.on_tool_error_callback()
BasePlugin.on_user_message_callback()

`BasePlugin`

- [BasePlugin.after_agent_callback()](google-adk.html#google.adk.plugins.BasePlugin.after_agent_callback)
- [BasePlugin.after_model_callback()](google-adk.html#google.adk.plugins.BasePlugin.after_model_callback)
- [BasePlugin.after_run_callback()](google-adk.html#google.adk.plugins.BasePlugin.after_run_callback)
- [BasePlugin.after_tool_callback()](google-adk.html#google.adk.plugins.BasePlugin.after_tool_callback)
- [BasePlugin.before_agent_callback()](google-adk.html#google.adk.plugins.BasePlugin.before_agent_callback)
- [BasePlugin.before_model_callback()](google-adk.html#google.adk.plugins.BasePlugin.before_model_callback)
- [BasePlugin.before_run_callback()](google-adk.html#google.adk.plugins.BasePlugin.before_run_callback)
- [BasePlugin.before_tool_callback()](google-adk.html#google.adk.plugins.BasePlugin.before_tool_callback)
- [BasePlugin.on_event_callback()](google-adk.html#google.adk.plugins.BasePlugin.on_event_callback)
- [BasePlugin.on_model_error_callback()](google-adk.html#google.adk.plugins.BasePlugin.on_model_error_callback)
- [BasePlugin.on_tool_error_callback()](google-adk.html#google.adk.plugins.BasePlugin.on_tool_error_callback)
- [BasePlugin.on_user_message_callback()](google-adk.html#google.adk.plugins.BasePlugin.on_user_message_callback)

`BasePlugin.after_agent_callback()`

`BasePlugin.after_model_callback()`

`BasePlugin.after_run_callback()`

`BasePlugin.after_tool_callback()`

`BasePlugin.before_agent_callback()`

`BasePlugin.before_model_callback()`

`BasePlugin.before_run_callback()`

`BasePlugin.before_tool_callback()`

`BasePlugin.on_event_callback()`

`BasePlugin.on_model_error_callback()`

`BasePlugin.on_tool_error_callback()`

`BasePlugin.on_user_message_callback()`

- [InMemoryRunner](google-adk.html#google.adk.runners.InMemoryRunner)
InMemoryRunner.agent
InMemoryRunner.app_name
InMemoryRunner._in_memory_session_service
- [Runner](google-adk.html#google.adk.runners.Runner)
Runner.app_name
Runner.agent
Runner.artifact_service
Runner.plugin_manager
Runner.session_service
Runner.memory_service
Runner.agent
Runner.app_name
Runner.artifact_service
Runner.close()
Runner.credential_service
Runner.memory_service
Runner.plugin_manager
Runner.run()
Runner.run_async()
Runner.run_live()
Runner.session_service

`InMemoryRunner`

- [InMemoryRunner.agent](google-adk.html#google.adk.runners.InMemoryRunner.agent)
- [InMemoryRunner.app_name](google-adk.html#google.adk.runners.InMemoryRunner.app_name)
- [InMemoryRunner._in_memory_session_service](google-adk.html#google.adk.runners.InMemoryRunner._in_memory_session_service)

`InMemoryRunner.agent`

`InMemoryRunner.app_name`

`InMemoryRunner._in_memory_session_service`

`Runner`

- [Runner.app_name](google-adk.html#google.adk.runners.Runner.app_name)
- [Runner.agent](google-adk.html#google.adk.runners.Runner.agent)
- [Runner.artifact_service](google-adk.html#google.adk.runners.Runner.artifact_service)
- [Runner.plugin_manager](google-adk.html#google.adk.runners.Runner.plugin_manager)
- [Runner.session_service](google-adk.html#google.adk.runners.Runner.session_service)
- [Runner.memory_service](google-adk.html#google.adk.runners.Runner.memory_service)
- [Runner.agent](google-adk.html#id35)
- [Runner.app_name](google-adk.html#id36)
- [Runner.artifact_service](google-adk.html#id37)
- [Runner.close()](google-adk.html#google.adk.runners.Runner.close)
- [Runner.credential_service](google-adk.html#google.adk.runners.Runner.credential_service)
- [Runner.memory_service](google-adk.html#id38)
- [Runner.plugin_manager](google-adk.html#id39)
- [Runner.run()](google-adk.html#google.adk.runners.Runner.run)
- [Runner.run_async()](google-adk.html#google.adk.runners.Runner.run_async)
- [Runner.run_live()](google-adk.html#google.adk.runners.Runner.run_live)
- [Runner.session_service](google-adk.html#id40)

`Runner.app_name`

`Runner.agent`

`Runner.artifact_service`

`Runner.plugin_manager`

`Runner.session_service`

`Runner.memory_service`

`Runner.agent`

`Runner.app_name`

`Runner.artifact_service`

`Runner.close()`

`Runner.credential_service`

`Runner.memory_service`

`Runner.plugin_manager`

`Runner.run()`

`Runner.run_async()`

`Runner.run_live()`

`Runner.session_service`

- [BaseSessionService](google-adk.html#google.adk.sessions.BaseSessionService)
BaseSessionService.append_event()
BaseSessionService.create_session()
BaseSessionService.delete_session()
BaseSessionService.get_session()
BaseSessionService.list_sessions()
- [DatabaseSessionService](google-adk.html#google.adk.sessions.DatabaseSessionService)
DatabaseSessionService.append_event()
DatabaseSessionService.create_session()
DatabaseSessionService.delete_session()
DatabaseSessionService.get_session()
DatabaseSessionService.list_sessions()
- [InMemorySessionService](google-adk.html#google.adk.sessions.InMemorySessionService)
InMemorySessionService.append_event()
InMemorySessionService.create_session()
InMemorySessionService.create_session_sync()
InMemorySessionService.delete_session()
InMemorySessionService.delete_session_sync()
InMemorySessionService.get_session()
InMemorySessionService.get_session_sync()
InMemorySessionService.list_sessions()
InMemorySessionService.list_sessions_sync()
- [Session](google-adk.html#google.adk.sessions.Session)
Session.id
Session.app_name
Session.user_id
Session.state
Session.events
Session.last_update_time
Session.app_name
Session.events
Session.id
Session.last_update_time
Session.state
Session.user_id
- [State](google-adk.html#google.adk.sessions.State)
State.APP_PREFIX
State.TEMP_PREFIX
State.USER_PREFIX
State.get()
State.has_delta()
State.to_dict()
State.update()
- [VertexAiSessionService](google-adk.html#google.adk.sessions.VertexAiSessionService)
VertexAiSessionService.append_event()
VertexAiSessionService.create_session()
VertexAiSessionService.delete_session()
VertexAiSessionService.get_session()
VertexAiSessionService.list_sessions()

`BaseSessionService`

- [BaseSessionService.append_event()](google-adk.html#google.adk.sessions.BaseSessionService.append_event)
- [BaseSessionService.create_session()](google-adk.html#google.adk.sessions.BaseSessionService.create_session)
- [BaseSessionService.delete_session()](google-adk.html#google.adk.sessions.BaseSessionService.delete_session)
- [BaseSessionService.get_session()](google-adk.html#google.adk.sessions.BaseSessionService.get_session)
- [BaseSessionService.list_sessions()](google-adk.html#google.adk.sessions.BaseSessionService.list_sessions)

`BaseSessionService.append_event()`

`BaseSessionService.create_session()`

`BaseSessionService.delete_session()`

`BaseSessionService.get_session()`

`BaseSessionService.list_sessions()`

`DatabaseSessionService`

- [DatabaseSessionService.append_event()](google-adk.html#google.adk.sessions.DatabaseSessionService.append_event)
- [DatabaseSessionService.create_session()](google-adk.html#google.adk.sessions.DatabaseSessionService.create_session)
- [DatabaseSessionService.delete_session()](google-adk.html#google.adk.sessions.DatabaseSessionService.delete_session)
- [DatabaseSessionService.get_session()](google-adk.html#google.adk.sessions.DatabaseSessionService.get_session)
- [DatabaseSessionService.list_sessions()](google-adk.html#google.adk.sessions.DatabaseSessionService.list_sessions)

`DatabaseSessionService.append_event()`

`DatabaseSessionService.create_session()`

`DatabaseSessionService.delete_session()`

`DatabaseSessionService.get_session()`

`DatabaseSessionService.list_sessions()`

`InMemorySessionService`

- [InMemorySessionService.append_event()](google-adk.html#google.adk.sessions.InMemorySessionService.append_event)
- [InMemorySessionService.create_session()](google-adk.html#google.adk.sessions.InMemorySessionService.create_session)
- [InMemorySessionService.create_session_sync()](google-adk.html#google.adk.sessions.InMemorySessionService.create_session_sync)
- [InMemorySessionService.delete_session()](google-adk.html#google.adk.sessions.InMemorySessionService.delete_session)
- [InMemorySessionService.delete_session_sync()](google-adk.html#google.adk.sessions.InMemorySessionService.delete_session_sync)
- [InMemorySessionService.get_session()](google-adk.html#google.adk.sessions.InMemorySessionService.get_session)
- [InMemorySessionService.get_session_sync()](google-adk.html#google.adk.sessions.InMemorySessionService.get_session_sync)
- [InMemorySessionService.list_sessions()](google-adk.html#google.adk.sessions.InMemorySessionService.list_sessions)
- [InMemorySessionService.list_sessions_sync()](google-adk.html#google.adk.sessions.InMemorySessionService.list_sessions_sync)

`InMemorySessionService.append_event()`

`InMemorySessionService.create_session()`

`InMemorySessionService.create_session_sync()`

`InMemorySessionService.delete_session()`

`InMemorySessionService.delete_session_sync()`

`InMemorySessionService.get_session()`

`InMemorySessionService.get_session_sync()`

`InMemorySessionService.list_sessions()`

`InMemorySessionService.list_sessions_sync()`

`Session`

- [Session.id](google-adk.html#google.adk.sessions.Session.id)
- [Session.app_name](google-adk.html#google.adk.sessions.Session.app_name)
- [Session.user_id](google-adk.html#google.adk.sessions.Session.user_id)
- [Session.state](google-adk.html#google.adk.sessions.Session.state)
- [Session.events](google-adk.html#google.adk.sessions.Session.events)
- [Session.last_update_time](google-adk.html#google.adk.sessions.Session.last_update_time)
- [Session.app_name](google-adk.html#id41)
- [Session.events](google-adk.html#id42)
- [Session.id](google-adk.html#id43)
- [Session.last_update_time](google-adk.html#id44)
- [Session.state](google-adk.html#id45)
- [Session.user_id](google-adk.html#id46)

`Session.id`

`Session.app_name`

`Session.user_id`

`Session.state`

`Session.events`

`Session.last_update_time`

`Session.app_name`

`Session.events`

`Session.id`

`Session.last_update_time`

`Session.state`

`Session.user_id`

`State`

- [State.APP_PREFIX](google-adk.html#google.adk.sessions.State.APP_PREFIX)
- [State.TEMP_PREFIX](google-adk.html#google.adk.sessions.State.TEMP_PREFIX)
- [State.USER_PREFIX](google-adk.html#google.adk.sessions.State.USER_PREFIX)
- [State.get()](google-adk.html#google.adk.sessions.State.get)
- [State.has_delta()](google-adk.html#google.adk.sessions.State.has_delta)
- [State.to_dict()](google-adk.html#google.adk.sessions.State.to_dict)
- [State.update()](google-adk.html#google.adk.sessions.State.update)

`State.APP_PREFIX`

`State.TEMP_PREFIX`

`State.USER_PREFIX`

`State.get()`

`State.has_delta()`

`State.to_dict()`

`State.update()`

`VertexAiSessionService`

- [VertexAiSessionService.append_event()](google-adk.html#google.adk.sessions.VertexAiSessionService.append_event)
- [VertexAiSessionService.create_session()](google-adk.html#google.adk.sessions.VertexAiSessionService.create_session)
- [VertexAiSessionService.delete_session()](google-adk.html#google.adk.sessions.VertexAiSessionService.delete_session)
- [VertexAiSessionService.get_session()](google-adk.html#google.adk.sessions.VertexAiSessionService.get_session)
- [VertexAiSessionService.list_sessions()](google-adk.html#google.adk.sessions.VertexAiSessionService.list_sessions)

`VertexAiSessionService.append_event()`

`VertexAiSessionService.create_session()`

`VertexAiSessionService.delete_session()`

`VertexAiSessionService.get_session()`

`VertexAiSessionService.list_sessions()`

- [trace_call_llm()](google-adk.html#google.adk.telemetry.trace_call_llm)
- [trace_merged_tool_calls()](google-adk.html#google.adk.telemetry.trace_merged_tool_calls)
- [trace_send_data()](google-adk.html#google.adk.telemetry.trace_send_data)
- [trace_tool_call()](google-adk.html#google.adk.telemetry.trace_tool_call)

`trace_call_llm()`

`trace_merged_tool_calls()`

`trace_send_data()`

`trace_tool_call()`

- [APIHubToolset](google-adk.html#google.adk.tools.APIHubToolset)
APIHubToolset.close()
APIHubToolset.get_tools()
- [AgentTool](google-adk.html#google.adk.tools.AgentTool)
AgentTool.agent
AgentTool.skip_summarization
AgentTool.from_config()
AgentTool.populate_name()
AgentTool.run_async()
- [AuthToolArguments](google-adk.html#google.adk.tools.AuthToolArguments)
AuthToolArguments.auth_config
AuthToolArguments.function_call_id
- [BaseTool](google-adk.html#google.adk.tools.BaseTool)
BaseTool.description
BaseTool.from_config()
BaseTool.is_long_running
BaseTool.name
BaseTool.process_llm_request()
BaseTool.run_async()
- [ExampleTool](google-adk.html#google.adk.tools.ExampleTool)
ExampleTool.examples
ExampleTool.process_llm_request()
- [FunctionTool](google-adk.html#google.adk.tools.FunctionTool)
FunctionTool.func
FunctionTool.run_async()
- [LongRunningFunctionTool](google-adk.html#google.adk.tools.LongRunningFunctionTool)
LongRunningFunctionTool.is_long_running
- [ToolContext](google-adk.html#google.adk.tools.ToolContext)
ToolContext.invocation_context
ToolContext.function_call_id
ToolContext.event_actions
ToolContext.actions
ToolContext.get_auth_response()
ToolContext.request_credential()
ToolContext.search_memory()
- [VertexAiSearchTool](google-adk.html#google.adk.tools.VertexAiSearchTool)
VertexAiSearchTool.data_store_id
VertexAiSearchTool.search_engine_id
VertexAiSearchTool.process_llm_request()
- [exit_loop()](google-adk.html#google.adk.tools.exit_loop)
- [transfer_to_agent()](google-adk.html#google.adk.tools.transfer_to_agent)

`APIHubToolset`

- [APIHubToolset.close()](google-adk.html#google.adk.tools.APIHubToolset.close)
- [APIHubToolset.get_tools()](google-adk.html#google.adk.tools.APIHubToolset.get_tools)

`APIHubToolset.close()`

`APIHubToolset.get_tools()`

`AgentTool`

- [AgentTool.agent](google-adk.html#google.adk.tools.AgentTool.agent)
- [AgentTool.skip_summarization](google-adk.html#google.adk.tools.AgentTool.skip_summarization)
- [AgentTool.from_config()](google-adk.html#google.adk.tools.AgentTool.from_config)
- [AgentTool.populate_name()](google-adk.html#google.adk.tools.AgentTool.populate_name)
- [AgentTool.run_async()](google-adk.html#google.adk.tools.AgentTool.run_async)

`AgentTool.agent`

`AgentTool.skip_summarization`

`AgentTool.from_config()`

`AgentTool.populate_name()`

`AgentTool.run_async()`

`AuthToolArguments`

- [AuthToolArguments.auth_config](google-adk.html#google.adk.tools.AuthToolArguments.auth_config)
- [AuthToolArguments.function_call_id](google-adk.html#google.adk.tools.AuthToolArguments.function_call_id)

`AuthToolArguments.auth_config`

`AuthToolArguments.function_call_id`

`BaseTool`

- [BaseTool.description](google-adk.html#google.adk.tools.BaseTool.description)
- [BaseTool.from_config()](google-adk.html#google.adk.tools.BaseTool.from_config)
- [BaseTool.is_long_running](google-adk.html#google.adk.tools.BaseTool.is_long_running)
- [BaseTool.name](google-adk.html#google.adk.tools.BaseTool.name)
- [BaseTool.process_llm_request()](google-adk.html#google.adk.tools.BaseTool.process_llm_request)
- [BaseTool.run_async()](google-adk.html#google.adk.tools.BaseTool.run_async)

`BaseTool.description`

`BaseTool.from_config()`

`BaseTool.is_long_running`

`BaseTool.name`

`BaseTool.process_llm_request()`

`BaseTool.run_async()`

`ExampleTool`

- [ExampleTool.examples](google-adk.html#google.adk.tools.ExampleTool.examples)
- [ExampleTool.process_llm_request()](google-adk.html#google.adk.tools.ExampleTool.process_llm_request)

`ExampleTool.examples`

`ExampleTool.process_llm_request()`

`FunctionTool`

- [FunctionTool.func](google-adk.html#google.adk.tools.FunctionTool.func)
- [FunctionTool.run_async()](google-adk.html#google.adk.tools.FunctionTool.run_async)

`FunctionTool.func`

`FunctionTool.run_async()`

`LongRunningFunctionTool`

- [LongRunningFunctionTool.is_long_running](google-adk.html#google.adk.tools.LongRunningFunctionTool.is_long_running)

`LongRunningFunctionTool.is_long_running`

`ToolContext`

- [ToolContext.invocation_context](google-adk.html#google.adk.tools.ToolContext.invocation_context)
- [ToolContext.function_call_id](google-adk.html#google.adk.tools.ToolContext.function_call_id)
- [ToolContext.event_actions](google-adk.html#google.adk.tools.ToolContext.event_actions)
- [ToolContext.actions](google-adk.html#google.adk.tools.ToolContext.actions)
- [ToolContext.get_auth_response()](google-adk.html#google.adk.tools.ToolContext.get_auth_response)
- [ToolContext.request_credential()](google-adk.html#google.adk.tools.ToolContext.request_credential)
- [ToolContext.search_memory()](google-adk.html#google.adk.tools.ToolContext.search_memory)

`ToolContext.invocation_context`

`ToolContext.function_call_id`

`ToolContext.event_actions`

`ToolContext.actions`

`ToolContext.get_auth_response()`

`ToolContext.request_credential()`

`ToolContext.search_memory()`

`VertexAiSearchTool`

- [VertexAiSearchTool.data_store_id](google-adk.html#google.adk.tools.VertexAiSearchTool.data_store_id)
- [VertexAiSearchTool.search_engine_id](google-adk.html#google.adk.tools.VertexAiSearchTool.search_engine_id)
- [VertexAiSearchTool.process_llm_request()](google-adk.html#google.adk.tools.VertexAiSearchTool.process_llm_request)

`VertexAiSearchTool.data_store_id`

`VertexAiSearchTool.search_engine_id`

`VertexAiSearchTool.process_llm_request()`

`exit_loop()`

`transfer_to_agent()`

- [AgentTool](google-adk.html#google.adk.tools.agent_tool.AgentTool)
AgentTool.agent
AgentTool.skip_summarization
AgentTool.from_config()
AgentTool.populate_name()
AgentTool.run_async()
- [AgentToolConfig](google-adk.html#google.adk.tools.agent_tool.AgentToolConfig)
AgentToolConfig.agent
AgentToolConfig.skip_summarization

`AgentTool`

- [AgentTool.agent](google-adk.html#google.adk.tools.agent_tool.AgentTool.agent)
- [AgentTool.skip_summarization](google-adk.html#google.adk.tools.agent_tool.AgentTool.skip_summarization)
- [AgentTool.from_config()](google-adk.html#google.adk.tools.agent_tool.AgentTool.from_config)
- [AgentTool.populate_name()](google-adk.html#google.adk.tools.agent_tool.AgentTool.populate_name)
- [AgentTool.run_async()](google-adk.html#google.adk.tools.agent_tool.AgentTool.run_async)

`AgentTool.agent`

`AgentTool.skip_summarization`

`AgentTool.from_config()`

`AgentTool.populate_name()`

`AgentTool.run_async()`

`AgentToolConfig`

- [AgentToolConfig.agent](google-adk.html#google.adk.tools.agent_tool.AgentToolConfig.agent)
- [AgentToolConfig.skip_summarization](google-adk.html#google.adk.tools.agent_tool.AgentToolConfig.skip_summarization)

`AgentToolConfig.agent`

`AgentToolConfig.skip_summarization`

- [APIHubToolset](google-adk.html#google.adk.tools.apihub_tool.APIHubToolset)
APIHubToolset.close()
APIHubToolset.get_tools()

`APIHubToolset`

- [APIHubToolset.close()](google-adk.html#google.adk.tools.apihub_tool.APIHubToolset.close)
- [APIHubToolset.get_tools()](google-adk.html#google.adk.tools.apihub_tool.APIHubToolset.get_tools)

`APIHubToolset.close()`

`APIHubToolset.get_tools()`

- [ApplicationIntegrationToolset](google-adk.html#google.adk.tools.application_integration_tool.ApplicationIntegrationToolset)
ApplicationIntegrationToolset.close()
ApplicationIntegrationToolset.get_tools()
- [IntegrationConnectorTool](google-adk.html#google.adk.tools.application_integration_tool.IntegrationConnectorTool)
IntegrationConnectorTool.EXCLUDE_FIELDS
IntegrationConnectorTool.OPTIONAL_FIELDS
IntegrationConnectorTool.run_async()

`ApplicationIntegrationToolset`

- [ApplicationIntegrationToolset.close()](google-adk.html#google.adk.tools.application_integration_tool.ApplicationIntegrationToolset.close)
- [ApplicationIntegrationToolset.get_tools()](google-adk.html#google.adk.tools.application_integration_tool.ApplicationIntegrationToolset.get_tools)

`ApplicationIntegrationToolset.close()`

`ApplicationIntegrationToolset.get_tools()`

`IntegrationConnectorTool`

- [IntegrationConnectorTool.EXCLUDE_FIELDS](google-adk.html#google.adk.tools.application_integration_tool.IntegrationConnectorTool.EXCLUDE_FIELDS)
- [IntegrationConnectorTool.OPTIONAL_FIELDS](google-adk.html#google.adk.tools.application_integration_tool.IntegrationConnectorTool.OPTIONAL_FIELDS)
- [IntegrationConnectorTool.run_async()](google-adk.html#google.adk.tools.application_integration_tool.IntegrationConnectorTool.run_async)

`IntegrationConnectorTool.EXCLUDE_FIELDS`

`IntegrationConnectorTool.OPTIONAL_FIELDS`

`IntegrationConnectorTool.run_async()`

- [AuthenticatedFunctionTool](google-adk.html#google.adk.tools.authenticated_function_tool.AuthenticatedFunctionTool)
AuthenticatedFunctionTool.run_async()

`AuthenticatedFunctionTool`

- [AuthenticatedFunctionTool.run_async()](google-adk.html#google.adk.tools.authenticated_function_tool.AuthenticatedFunctionTool.run_async)

`AuthenticatedFunctionTool.run_async()`

- [BaseAuthenticatedTool](google-adk.html#google.adk.tools.base_authenticated_tool.BaseAuthenticatedTool)
BaseAuthenticatedTool.run_async()

`BaseAuthenticatedTool`

- [BaseAuthenticatedTool.run_async()](google-adk.html#google.adk.tools.base_authenticated_tool.BaseAuthenticatedTool.run_async)

`BaseAuthenticatedTool.run_async()`

- [BaseTool](google-adk.html#google.adk.tools.base_tool.BaseTool)
BaseTool.description
BaseTool.from_config()
BaseTool.is_long_running
BaseTool.name
BaseTool.process_llm_request()
BaseTool.run_async()
- [BaseToolConfig](google-adk.html#google.adk.tools.base_tool.BaseToolConfig)
- [ToolArgsConfig](google-adk.html#google.adk.tools.base_tool.ToolArgsConfig)
- [ToolConfig](google-adk.html#google.adk.tools.base_tool.ToolConfig)
ToolConfig.args
ToolConfig.name

`BaseTool`

- [BaseTool.description](google-adk.html#google.adk.tools.base_tool.BaseTool.description)
- [BaseTool.from_config()](google-adk.html#google.adk.tools.base_tool.BaseTool.from_config)
- [BaseTool.is_long_running](google-adk.html#google.adk.tools.base_tool.BaseTool.is_long_running)
- [BaseTool.name](google-adk.html#google.adk.tools.base_tool.BaseTool.name)
- [BaseTool.process_llm_request()](google-adk.html#google.adk.tools.base_tool.BaseTool.process_llm_request)
- [BaseTool.run_async()](google-adk.html#google.adk.tools.base_tool.BaseTool.run_async)

`BaseTool.description`

`BaseTool.from_config()`

`BaseTool.is_long_running`

`BaseTool.name`

`BaseTool.process_llm_request()`

`BaseTool.run_async()`

`BaseToolConfig`

`ToolArgsConfig`

`ToolConfig`

- [ToolConfig.args](google-adk.html#google.adk.tools.base_tool.ToolConfig.args)
- [ToolConfig.name](google-adk.html#google.adk.tools.base_tool.ToolConfig.name)

`ToolConfig.args`

`ToolConfig.name`

- [BaseToolset](google-adk.html#google.adk.tools.base_toolset.BaseToolset)
BaseToolset.close()
BaseToolset.get_tools()
BaseToolset.process_llm_request()
- [ToolPredicate](google-adk.html#google.adk.tools.base_toolset.ToolPredicate)

`BaseToolset`

- [BaseToolset.close()](google-adk.html#google.adk.tools.base_toolset.BaseToolset.close)
- [BaseToolset.get_tools()](google-adk.html#google.adk.tools.base_toolset.BaseToolset.get_tools)
- [BaseToolset.process_llm_request()](google-adk.html#google.adk.tools.base_toolset.BaseToolset.process_llm_request)

`BaseToolset.close()`

`BaseToolset.get_tools()`

`BaseToolset.process_llm_request()`

`ToolPredicate`

- [BigQueryCredentialsConfig](google-adk.html#google.adk.tools.bigquery.BigQueryCredentialsConfig)
BigQueryCredentialsConfig.client_id
BigQueryCredentialsConfig.client_secret
BigQueryCredentialsConfig.credentials
BigQueryCredentialsConfig.scopes
- [BigQueryTool](google-adk.html#google.adk.tools.bigquery.BigQueryTool)
BigQueryTool.run_async()
- [BigQueryToolset](google-adk.html#google.adk.tools.bigquery.BigQueryToolset)
BigQueryToolset.close()
BigQueryToolset.get_tools()

`BigQueryCredentialsConfig`

- [BigQueryCredentialsConfig.client_id](google-adk.html#google.adk.tools.bigquery.BigQueryCredentialsConfig.client_id)
- [BigQueryCredentialsConfig.client_secret](google-adk.html#google.adk.tools.bigquery.BigQueryCredentialsConfig.client_secret)
- [BigQueryCredentialsConfig.credentials](google-adk.html#google.adk.tools.bigquery.BigQueryCredentialsConfig.credentials)
- [BigQueryCredentialsConfig.scopes](google-adk.html#google.adk.tools.bigquery.BigQueryCredentialsConfig.scopes)

`BigQueryCredentialsConfig.client_id`

`BigQueryCredentialsConfig.client_secret`

`BigQueryCredentialsConfig.credentials`

`BigQueryCredentialsConfig.scopes`

`BigQueryTool`

- [BigQueryTool.run_async()](google-adk.html#google.adk.tools.bigquery.BigQueryTool.run_async)

`BigQueryTool.run_async()`

`BigQueryToolset`

- [BigQueryToolset.close()](google-adk.html#google.adk.tools.bigquery.BigQueryToolset.close)
- [BigQueryToolset.get_tools()](google-adk.html#google.adk.tools.bigquery.BigQueryToolset.get_tools)

`BigQueryToolset.close()`

`BigQueryToolset.get_tools()`

- [CrewaiTool](google-adk.html#google.adk.tools.crewai_tool.CrewaiTool)
CrewaiTool.tool

`CrewaiTool`

- [CrewaiTool.tool](google-adk.html#google.adk.tools.crewai_tool.CrewaiTool.tool)

`CrewaiTool.tool`

- [EnterpriseWebSearchTool](google-adk.html#google.adk.tools.enterprise_search_tool.EnterpriseWebSearchTool)
EnterpriseWebSearchTool.description
EnterpriseWebSearchTool.name
EnterpriseWebSearchTool.process_llm_request()

`EnterpriseWebSearchTool`

- [EnterpriseWebSearchTool.description](google-adk.html#google.adk.tools.enterprise_search_tool.EnterpriseWebSearchTool.description)
- [EnterpriseWebSearchTool.name](google-adk.html#google.adk.tools.enterprise_search_tool.EnterpriseWebSearchTool.name)
- [EnterpriseWebSearchTool.process_llm_request()](google-adk.html#google.adk.tools.enterprise_search_tool.EnterpriseWebSearchTool.process_llm_request)

`EnterpriseWebSearchTool.description`

`EnterpriseWebSearchTool.name`

`EnterpriseWebSearchTool.process_llm_request()`

- [ExampleTool](google-adk.html#google.adk.tools.example_tool.ExampleTool)
ExampleTool.examples
ExampleTool.process_llm_request()

`ExampleTool`

- [ExampleTool.examples](google-adk.html#google.adk.tools.example_tool.ExampleTool.examples)
- [ExampleTool.process_llm_request()](google-adk.html#google.adk.tools.example_tool.ExampleTool.process_llm_request)

`ExampleTool.examples`

`ExampleTool.process_llm_request()`

- [exit_loop()](google-adk.html#google.adk.tools.exit_loop_tool.exit_loop)

`exit_loop()`

- [FunctionTool](google-adk.html#google.adk.tools.function_tool.FunctionTool)
FunctionTool.func
FunctionTool.run_async()

`FunctionTool`

- [FunctionTool.func](google-adk.html#google.adk.tools.function_tool.FunctionTool.func)
- [FunctionTool.run_async()](google-adk.html#google.adk.tools.function_tool.FunctionTool.run_async)

`FunctionTool.func`

`FunctionTool.run_async()`

- [get_user_choice()](google-adk.html#google.adk.tools.get_user_choice_tool.get_user_choice)

`get_user_choice()`

- [BigQueryToolset](google-adk.html#google.adk.tools.google_api_tool.BigQueryToolset)
- [CalendarToolset](google-adk.html#google.adk.tools.google_api_tool.CalendarToolset)
- [DocsToolset](google-adk.html#google.adk.tools.google_api_tool.DocsToolset)
- [GmailToolset](google-adk.html#google.adk.tools.google_api_tool.GmailToolset)
- [GoogleApiTool](google-adk.html#google.adk.tools.google_api_tool.GoogleApiTool)
GoogleApiTool.configure_auth()
GoogleApiTool.configure_sa_auth()
GoogleApiTool.description
GoogleApiTool.name
GoogleApiTool.run_async()
- [GoogleApiToolset](google-adk.html#google.adk.tools.google_api_tool.GoogleApiToolset)
GoogleApiToolset.close()
GoogleApiToolset.configure_auth()
GoogleApiToolset.configure_sa_auth()
GoogleApiToolset.get_tools()
GoogleApiToolset.set_tool_filter()
- [SheetsToolset](google-adk.html#google.adk.tools.google_api_tool.SheetsToolset)
- [SlidesToolset](google-adk.html#google.adk.tools.google_api_tool.SlidesToolset)
- [YoutubeToolset](google-adk.html#google.adk.tools.google_api_tool.YoutubeToolset)

`BigQueryToolset`

`CalendarToolset`

`DocsToolset`

`GmailToolset`

`GoogleApiTool`

- [GoogleApiTool.configure_auth()](google-adk.html#google.adk.tools.google_api_tool.GoogleApiTool.configure_auth)
- [GoogleApiTool.configure_sa_auth()](google-adk.html#google.adk.tools.google_api_tool.GoogleApiTool.configure_sa_auth)
- [GoogleApiTool.description](google-adk.html#google.adk.tools.google_api_tool.GoogleApiTool.description)
- [GoogleApiTool.name](google-adk.html#google.adk.tools.google_api_tool.GoogleApiTool.name)
- [GoogleApiTool.run_async()](google-adk.html#google.adk.tools.google_api_tool.GoogleApiTool.run_async)

`GoogleApiTool.configure_auth()`

`GoogleApiTool.configure_sa_auth()`

`GoogleApiTool.description`

`GoogleApiTool.name`

`GoogleApiTool.run_async()`

`GoogleApiToolset`

- [GoogleApiToolset.close()](google-adk.html#google.adk.tools.google_api_tool.GoogleApiToolset.close)
- [GoogleApiToolset.configure_auth()](google-adk.html#google.adk.tools.google_api_tool.GoogleApiToolset.configure_auth)
- [GoogleApiToolset.configure_sa_auth()](google-adk.html#google.adk.tools.google_api_tool.GoogleApiToolset.configure_sa_auth)
- [GoogleApiToolset.get_tools()](google-adk.html#google.adk.tools.google_api_tool.GoogleApiToolset.get_tools)
- [GoogleApiToolset.set_tool_filter()](google-adk.html#google.adk.tools.google_api_tool.GoogleApiToolset.set_tool_filter)

`GoogleApiToolset.close()`

`GoogleApiToolset.configure_auth()`

`GoogleApiToolset.configure_sa_auth()`

`GoogleApiToolset.get_tools()`

`GoogleApiToolset.set_tool_filter()`

`SheetsToolset`

`SlidesToolset`

`YoutubeToolset`

- [GoogleSearchTool](google-adk.html#google.adk.tools.google_search_tool.GoogleSearchTool)
GoogleSearchTool.description
GoogleSearchTool.name
GoogleSearchTool.process_llm_request()

`GoogleSearchTool`

- [GoogleSearchTool.description](google-adk.html#google.adk.tools.google_search_tool.GoogleSearchTool.description)
- [GoogleSearchTool.name](google-adk.html#google.adk.tools.google_search_tool.GoogleSearchTool.name)
- [GoogleSearchTool.process_llm_request()](google-adk.html#google.adk.tools.google_search_tool.GoogleSearchTool.process_llm_request)

`GoogleSearchTool.description`

`GoogleSearchTool.name`

`GoogleSearchTool.process_llm_request()`

- [LangchainTool](google-adk.html#google.adk.tools.langchain_tool.LangchainTool)

`LangchainTool`

- [LoadArtifactsTool](google-adk.html#google.adk.tools.load_artifacts_tool.LoadArtifactsTool)
LoadArtifactsTool.description
LoadArtifactsTool.name
LoadArtifactsTool.process_llm_request()
LoadArtifactsTool.run_async()

`LoadArtifactsTool`

- [LoadArtifactsTool.description](google-adk.html#google.adk.tools.load_artifacts_tool.LoadArtifactsTool.description)
- [LoadArtifactsTool.name](google-adk.html#google.adk.tools.load_artifacts_tool.LoadArtifactsTool.name)
- [LoadArtifactsTool.process_llm_request()](google-adk.html#google.adk.tools.load_artifacts_tool.LoadArtifactsTool.process_llm_request)
- [LoadArtifactsTool.run_async()](google-adk.html#google.adk.tools.load_artifacts_tool.LoadArtifactsTool.run_async)

`LoadArtifactsTool.description`

`LoadArtifactsTool.name`

`LoadArtifactsTool.process_llm_request()`

`LoadArtifactsTool.run_async()`

- [LoadMemoryResponse](google-adk.html#google.adk.tools.load_memory_tool.LoadMemoryResponse)
LoadMemoryResponse.memories
- [LoadMemoryTool](google-adk.html#google.adk.tools.load_memory_tool.LoadMemoryTool)
LoadMemoryTool.process_llm_request()
- [load_memory()](google-adk.html#google.adk.tools.load_memory_tool.load_memory)

`LoadMemoryResponse`

- [LoadMemoryResponse.memories](google-adk.html#google.adk.tools.load_memory_tool.LoadMemoryResponse.memories)

`LoadMemoryResponse.memories`

`LoadMemoryTool`

- [LoadMemoryTool.process_llm_request()](google-adk.html#google.adk.tools.load_memory_tool.LoadMemoryTool.process_llm_request)

`LoadMemoryTool.process_llm_request()`

`load_memory()`

- [load_web_page()](google-adk.html#google.adk.tools.load_web_page.load_web_page)

`load_web_page()`

- [LongRunningFunctionTool](google-adk.html#google.adk.tools.long_running_tool.LongRunningFunctionTool)
LongRunningFunctionTool.is_long_running

`LongRunningFunctionTool`

- [LongRunningFunctionTool.is_long_running](google-adk.html#google.adk.tools.long_running_tool.LongRunningFunctionTool.is_long_running)

`LongRunningFunctionTool.is_long_running`

- [MCPTool](google-adk.html#google.adk.tools.mcp_tool.MCPTool)
- [MCPToolset](google-adk.html#google.adk.tools.mcp_tool.MCPToolset)
MCPToolset.close()
MCPToolset.get_tools()
- [SseConnectionParams](google-adk.html#google.adk.tools.mcp_tool.SseConnectionParams)
SseConnectionParams.url
SseConnectionParams.headers
SseConnectionParams.timeout
SseConnectionParams.sse_read_timeout
SseConnectionParams.headers
SseConnectionParams.sse_read_timeout
SseConnectionParams.timeout
SseConnectionParams.url
- [StdioConnectionParams](google-adk.html#google.adk.tools.mcp_tool.StdioConnectionParams)
StdioConnectionParams.server_params
StdioConnectionParams.timeout
StdioConnectionParams.server_params
StdioConnectionParams.timeout
- [StreamableHTTPConnectionParams](google-adk.html#google.adk.tools.mcp_tool.StreamableHTTPConnectionParams)
StreamableHTTPConnectionParams.url
StreamableHTTPConnectionParams.headers
StreamableHTTPConnectionParams.timeout
StreamableHTTPConnectionParams.sse_read_timeout
StreamableHTTPConnectionParams.terminate_on_close
StreamableHTTPConnectionParams.headers
StreamableHTTPConnectionParams.sse_read_timeout
StreamableHTTPConnectionParams.terminate_on_close
StreamableHTTPConnectionParams.timeout
StreamableHTTPConnectionParams.url
- [adk_to_mcp_tool_type()](google-adk.html#google.adk.tools.mcp_tool.adk_to_mcp_tool_type)
- [gemini_to_json_schema()](google-adk.html#google.adk.tools.mcp_tool.gemini_to_json_schema)

`MCPTool`

`MCPToolset`

- [MCPToolset.close()](google-adk.html#google.adk.tools.mcp_tool.MCPToolset.close)
- [MCPToolset.get_tools()](google-adk.html#google.adk.tools.mcp_tool.MCPToolset.get_tools)

`MCPToolset.close()`

`MCPToolset.get_tools()`

`SseConnectionParams`

- [SseConnectionParams.url](google-adk.html#google.adk.tools.mcp_tool.SseConnectionParams.url)
- [SseConnectionParams.headers](google-adk.html#google.adk.tools.mcp_tool.SseConnectionParams.headers)
- [SseConnectionParams.timeout](google-adk.html#google.adk.tools.mcp_tool.SseConnectionParams.timeout)
- [SseConnectionParams.sse_read_timeout](google-adk.html#google.adk.tools.mcp_tool.SseConnectionParams.sse_read_timeout)
- [SseConnectionParams.headers](google-adk.html#id83)
- [SseConnectionParams.sse_read_timeout](google-adk.html#id84)
- [SseConnectionParams.timeout](google-adk.html#id85)
- [SseConnectionParams.url](google-adk.html#id86)

`SseConnectionParams.url`

`SseConnectionParams.headers`

`SseConnectionParams.timeout`

`SseConnectionParams.sse_read_timeout`

`SseConnectionParams.headers`

`SseConnectionParams.sse_read_timeout`

`SseConnectionParams.timeout`

`SseConnectionParams.url`

`StdioConnectionParams`

- [StdioConnectionParams.server_params](google-adk.html#google.adk.tools.mcp_tool.StdioConnectionParams.server_params)
- [StdioConnectionParams.timeout](google-adk.html#google.adk.tools.mcp_tool.StdioConnectionParams.timeout)
- [StdioConnectionParams.server_params](google-adk.html#id87)
- [StdioConnectionParams.timeout](google-adk.html#id88)

`StdioConnectionParams.server_params`

`StdioConnectionParams.timeout`

`StdioConnectionParams.server_params`

`StdioConnectionParams.timeout`

`StreamableHTTPConnectionParams`

- [StreamableHTTPConnectionParams.url](google-adk.html#google.adk.tools.mcp_tool.StreamableHTTPConnectionParams.url)
- [StreamableHTTPConnectionParams.headers](google-adk.html#google.adk.tools.mcp_tool.StreamableHTTPConnectionParams.headers)
- [StreamableHTTPConnectionParams.timeout](google-adk.html#google.adk.tools.mcp_tool.StreamableHTTPConnectionParams.timeout)
- [StreamableHTTPConnectionParams.sse_read_timeout](google-adk.html#google.adk.tools.mcp_tool.StreamableHTTPConnectionParams.sse_read_timeout)
- [StreamableHTTPConnectionParams.terminate_on_close](google-adk.html#google.adk.tools.mcp_tool.StreamableHTTPConnectionParams.terminate_on_close)
- [StreamableHTTPConnectionParams.headers](google-adk.html#id89)
- [StreamableHTTPConnectionParams.sse_read_timeout](google-adk.html#id90)
- [StreamableHTTPConnectionParams.terminate_on_close](google-adk.html#id91)
- [StreamableHTTPConnectionParams.timeout](google-adk.html#id92)
- [StreamableHTTPConnectionParams.url](google-adk.html#id93)

`StreamableHTTPConnectionParams.url`

`StreamableHTTPConnectionParams.headers`

`StreamableHTTPConnectionParams.timeout`

`StreamableHTTPConnectionParams.sse_read_timeout`

`StreamableHTTPConnectionParams.terminate_on_close`

`StreamableHTTPConnectionParams.headers`

`StreamableHTTPConnectionParams.sse_read_timeout`

`StreamableHTTPConnectionParams.terminate_on_close`

`StreamableHTTPConnectionParams.timeout`

`StreamableHTTPConnectionParams.url`

`adk_to_mcp_tool_type()`

`gemini_to_json_schema()`

- [OpenAPIToolset](google-adk.html#google.adk.tools.openapi_tool.OpenAPIToolset)
OpenAPIToolset.close()
OpenAPIToolset.get_tool()
OpenAPIToolset.get_tools()
- [RestApiTool](google-adk.html#google.adk.tools.openapi_tool.RestApiTool)
RestApiTool.call()
RestApiTool.configure_auth_credential()
RestApiTool.configure_auth_scheme()
RestApiTool.description
RestApiTool.from_parsed_operation()
RestApiTool.from_parsed_operation_str()
RestApiTool.name
RestApiTool.run_async()

`OpenAPIToolset`

- [OpenAPIToolset.close()](google-adk.html#google.adk.tools.openapi_tool.OpenAPIToolset.close)
- [OpenAPIToolset.get_tool()](google-adk.html#google.adk.tools.openapi_tool.OpenAPIToolset.get_tool)
- [OpenAPIToolset.get_tools()](google-adk.html#google.adk.tools.openapi_tool.OpenAPIToolset.get_tools)

`OpenAPIToolset.close()`

`OpenAPIToolset.get_tool()`

`OpenAPIToolset.get_tools()`

`RestApiTool`

- [RestApiTool.call()](google-adk.html#google.adk.tools.openapi_tool.RestApiTool.call)
- [RestApiTool.configure_auth_credential()](google-adk.html#google.adk.tools.openapi_tool.RestApiTool.configure_auth_credential)
- [RestApiTool.configure_auth_scheme()](google-adk.html#google.adk.tools.openapi_tool.RestApiTool.configure_auth_scheme)
- [RestApiTool.description](google-adk.html#google.adk.tools.openapi_tool.RestApiTool.description)
- [RestApiTool.from_parsed_operation()](google-adk.html#google.adk.tools.openapi_tool.RestApiTool.from_parsed_operation)
- [RestApiTool.from_parsed_operation_str()](google-adk.html#google.adk.tools.openapi_tool.RestApiTool.from_parsed_operation_str)
- [RestApiTool.name](google-adk.html#google.adk.tools.openapi_tool.RestApiTool.name)
- [RestApiTool.run_async()](google-adk.html#google.adk.tools.openapi_tool.RestApiTool.run_async)

`RestApiTool.call()`

`RestApiTool.configure_auth_credential()`

`RestApiTool.configure_auth_scheme()`

`RestApiTool.description`

`RestApiTool.from_parsed_operation()`

`RestApiTool.from_parsed_operation_str()`

`RestApiTool.name`

`RestApiTool.run_async()`

- [PreloadMemoryTool](google-adk.html#google.adk.tools.preload_memory_tool.PreloadMemoryTool)
PreloadMemoryTool.description
PreloadMemoryTool.name
PreloadMemoryTool.process_llm_request()

`PreloadMemoryTool`

- [PreloadMemoryTool.description](google-adk.html#google.adk.tools.preload_memory_tool.PreloadMemoryTool.description)
- [PreloadMemoryTool.name](google-adk.html#google.adk.tools.preload_memory_tool.PreloadMemoryTool.name)
- [PreloadMemoryTool.process_llm_request()](google-adk.html#google.adk.tools.preload_memory_tool.PreloadMemoryTool.process_llm_request)

`PreloadMemoryTool.description`

`PreloadMemoryTool.name`

`PreloadMemoryTool.process_llm_request()`

- [BaseRetrievalTool](google-adk.html#google.adk.tools.retrieval.BaseRetrievalTool)
BaseRetrievalTool.description
BaseRetrievalTool.name
- [FilesRetrieval](google-adk.html#google.adk.tools.retrieval.FilesRetrieval)
FilesRetrieval.description
FilesRetrieval.name
- [LlamaIndexRetrieval](google-adk.html#google.adk.tools.retrieval.LlamaIndexRetrieval)
LlamaIndexRetrieval.description
LlamaIndexRetrieval.name
LlamaIndexRetrieval.run_async()
- [VertexAiRagRetrieval](google-adk.html#google.adk.tools.retrieval.VertexAiRagRetrieval)
VertexAiRagRetrieval.description
VertexAiRagRetrieval.name
VertexAiRagRetrieval.process_llm_request()
VertexAiRagRetrieval.run_async()

`BaseRetrievalTool`

- [BaseRetrievalTool.description](google-adk.html#google.adk.tools.retrieval.BaseRetrievalTool.description)
- [BaseRetrievalTool.name](google-adk.html#google.adk.tools.retrieval.BaseRetrievalTool.name)

`BaseRetrievalTool.description`

`BaseRetrievalTool.name`

`FilesRetrieval`

- [FilesRetrieval.description](google-adk.html#google.adk.tools.retrieval.FilesRetrieval.description)
- [FilesRetrieval.name](google-adk.html#google.adk.tools.retrieval.FilesRetrieval.name)

`FilesRetrieval.description`

`FilesRetrieval.name`

`LlamaIndexRetrieval`

- [LlamaIndexRetrieval.description](google-adk.html#google.adk.tools.retrieval.LlamaIndexRetrieval.description)
- [LlamaIndexRetrieval.name](google-adk.html#google.adk.tools.retrieval.LlamaIndexRetrieval.name)
- [LlamaIndexRetrieval.run_async()](google-adk.html#google.adk.tools.retrieval.LlamaIndexRetrieval.run_async)

`LlamaIndexRetrieval.description`

`LlamaIndexRetrieval.name`

`LlamaIndexRetrieval.run_async()`

`VertexAiRagRetrieval`

- [VertexAiRagRetrieval.description](google-adk.html#google.adk.tools.retrieval.VertexAiRagRetrieval.description)
- [VertexAiRagRetrieval.name](google-adk.html#google.adk.tools.retrieval.VertexAiRagRetrieval.name)
- [VertexAiRagRetrieval.process_llm_request()](google-adk.html#google.adk.tools.retrieval.VertexAiRagRetrieval.process_llm_request)
- [VertexAiRagRetrieval.run_async()](google-adk.html#google.adk.tools.retrieval.VertexAiRagRetrieval.run_async)

`VertexAiRagRetrieval.description`

`VertexAiRagRetrieval.name`

`VertexAiRagRetrieval.process_llm_request()`

`VertexAiRagRetrieval.run_async()`

- [ToolContext](google-adk.html#google.adk.tools.tool_context.ToolContext)
ToolContext.invocation_context
ToolContext.function_call_id
ToolContext.event_actions
ToolContext.actions
ToolContext.get_auth_response()
ToolContext.request_credential()
ToolContext.search_memory()

`ToolContext`

- [ToolContext.invocation_context](google-adk.html#google.adk.tools.tool_context.ToolContext.invocation_context)
- [ToolContext.function_call_id](google-adk.html#google.adk.tools.tool_context.ToolContext.function_call_id)
- [ToolContext.event_actions](google-adk.html#google.adk.tools.tool_context.ToolContext.event_actions)
- [ToolContext.actions](google-adk.html#google.adk.tools.tool_context.ToolContext.actions)
- [ToolContext.get_auth_response()](google-adk.html#google.adk.tools.tool_context.ToolContext.get_auth_response)
- [ToolContext.request_credential()](google-adk.html#google.adk.tools.tool_context.ToolContext.request_credential)
- [ToolContext.search_memory()](google-adk.html#google.adk.tools.tool_context.ToolContext.search_memory)

`ToolContext.invocation_context`

`ToolContext.function_call_id`

`ToolContext.event_actions`

`ToolContext.actions`

`ToolContext.get_auth_response()`

`ToolContext.request_credential()`

`ToolContext.search_memory()`

- [ToolboxToolset](google-adk.html#google.adk.tools.toolbox_toolset.ToolboxToolset)
ToolboxToolset.close()
ToolboxToolset.get_tools()

`ToolboxToolset`

- [ToolboxToolset.close()](google-adk.html#google.adk.tools.toolbox_toolset.ToolboxToolset.close)
- [ToolboxToolset.get_tools()](google-adk.html#google.adk.tools.toolbox_toolset.ToolboxToolset.get_tools)

`ToolboxToolset.close()`

`ToolboxToolset.get_tools()`

- [transfer_to_agent()](google-adk.html#google.adk.tools.transfer_to_agent_tool.transfer_to_agent)

`transfer_to_agent()`

- [UrlContextTool](google-adk.html#google.adk.tools.url_context_tool.UrlContextTool)
UrlContextTool.description
UrlContextTool.name
UrlContextTool.process_llm_request()

`UrlContextTool`

- [UrlContextTool.description](google-adk.html#google.adk.tools.url_context_tool.UrlContextTool.description)
- [UrlContextTool.name](google-adk.html#google.adk.tools.url_context_tool.UrlContextTool.name)
- [UrlContextTool.process_llm_request()](google-adk.html#google.adk.tools.url_context_tool.UrlContextTool.process_llm_request)

`UrlContextTool.description`

`UrlContextTool.name`

`UrlContextTool.process_llm_request()`

- [VertexAiSearchTool](google-adk.html#google.adk.tools.vertex_ai_search_tool.VertexAiSearchTool)
VertexAiSearchTool.data_store_id
VertexAiSearchTool.search_engine_id
VertexAiSearchTool.process_llm_request()

`VertexAiSearchTool`

- [VertexAiSearchTool.data_store_id](google-adk.html#google.adk.tools.vertex_ai_search_tool.VertexAiSearchTool.data_store_id)
- [VertexAiSearchTool.search_engine_id](google-adk.html#google.adk.tools.vertex_ai_search_tool.VertexAiSearchTool.search_engine_id)
- [VertexAiSearchTool.process_llm_request()](google-adk.html#google.adk.tools.vertex_ai_search_tool.VertexAiSearchTool.process_llm_request)

`VertexAiSearchTool.data_store_id`

`VertexAiSearchTool.search_engine_id`

`VertexAiSearchTool.process_llm_request()`