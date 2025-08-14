# Generated ADK agent module for code_helper
# Source: examples/code_helper

from google.adk.agents import Agent

# Tool definitions
# Tool: analyze_code
def analyze_code(code: str, language: str = "python") -> dict:
    """Analyze code for basic metrics and patterns."""
    lines = code.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    
    return {
        "total_lines": len(lines),
        "code_lines": len(non_empty_lines),
        "language": language,
        "has_functions": "def " in code or "function " in code,
        "has_classes": "class " in code,
        "complexity": "high" if len(non_empty_lines) > 50 else "medium" if len(non_empty_lines) > 20 else "low"
    }

tool_0 = analyze_code


# Agent: code_helper
# Description: Programming assistant for code help, debugging, and explanations
root_agent = Agent(
    model='gemini-2.5-flash-lite',
    name='code_helper',
    description='''Programming assistant for code help, debugging, and explanations''',
    instruction='''You are a helpful programming assistant specialized in  development.
You help with code review, debugging, optimization, and explanations.

Your expertise includes:
- Code review and best practices
- Debugging and troubleshooting
- Performance optimization
- Code explanation and documentation
- Architecture and design patterns

Guidelines:
- Provide working code examples
- Explain your reasoning
- Suggest best practices
- Point out potential issues
- Include comments in code snippets
- Consider security implications''',
    tools=[tool_0]
)
