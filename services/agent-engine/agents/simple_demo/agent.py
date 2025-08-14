# Generated ADK agent module for simple_demo
# Source: examples/simple_demo

from google.adk.agents import Agent

# Tool definitions
# Tool: simple_calculator
def simple_calculator(operation: str, a: float, b: float) -> dict:
    """Perform basic mathematical operations."""
    result = None
    
    if operation == "add":
        result = a + b
    elif operation == "subtract":
        result = a - b
    elif operation == "multiply":
        result = a * b
    elif operation == "divide":
        result = a / b if b != 0 else "Error: Division by zero"
    else:
        return {"error": f"Unknown operation: {operation}"}
    
    return {
        "operation": operation,
        "input_a": a,
        "input_b": b,
        "result": result,
        "expression": f"{a} {operation} {b} = {result}"
    }

tool_0 = simple_calculator

# Tool: word_counter
def word_counter(text: str) -> dict:
    """Count words, characters, and sentences in text."""
    words = text.split()
    sentences = text.split('.') + text.split('!') + text.split('?')
    sentences = [s for s in sentences if s.strip()]
    
    return {
        "text_length": len(text),
        "word_count": len(words),
        "character_count": len(text),
        "sentence_count": len(sentences),
        "average_word_length": sum(len(word) for word in words) / len(words) if words else 0
    }

tool_1 = word_counter


# Agent: simple_demo
# Description: Simple demonstration agent for testing basic Dev UI functionality
root_agent = Agent(
    model='gemini-2.0-flash',
    name='simple_demo',
    description='''Simple demonstration agent for testing basic Dev UI functionality''',
    instruction='''You are a simple demo agent for testing the Tahoe Dev UI.

Your purpose:
- Demonstrate basic agent functionality
- Provide clear, simple responses
- Show how tools work in the Dev UI
- Help users understand agent capabilities

Guidelines:
- Keep responses short and clear
- Explain what you're doing
- Mention when you're using tools
- Be friendly and helpful''',
    tools=[tool_0, tool_1]
)
