#!/usr/bin/env python3
"""
Tool Usage Examples
Demonstrates automatic and explicit tool wrapping patterns
"""

import os
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool, google_search
from google.adk.runners import InMemoryRunner


def automatic_wrapping_example():
    """Demonstrate automatic function wrapping."""
    print("\n" + "="*60)
    print("AUTOMATIC TOOL WRAPPING")
    print("="*60)
    
    # Define simple tools that will be automatically wrapped
    def calculate_statistics(numbers: List[float]) -> Dict[str, float]:
        """Calculate basic statistics for a list of numbers."""
        if not numbers:
            return {"error": "Empty list provided"}
        
        sorted_nums = sorted(numbers)
        n = len(numbers)
        
        return {
            "count": n,
            "sum": sum(numbers),
            "mean": sum(numbers) / n,
            "min": min(numbers),
            "max": max(numbers),
            "median": sorted_nums[n // 2] if n % 2 else (sorted_nums[n//2-1] + sorted_nums[n//2]) / 2,
            "range": max(numbers) - min(numbers)
        }
    
    def text_processor(
        text: str, 
        operation: str = "analyze",
        case_sensitive: bool = False
    ) -> Dict[str, Any]:
        """Process text with various operations."""
        if not case_sensitive:
            text_to_process = text.lower()
        else:
            text_to_process = text
        
        result = {"original_length": len(text)}
        
        if operation == "analyze":
            words = text.split()
            unique_words = set(text_to_process.split())
            result.update({
                "word_count": len(words),
                "unique_words": len(unique_words),
                "average_word_length": sum(len(w) for w in words) / len(words) if words else 0,
                "sentences": text.count('.') + text.count('!') + text.count('?'),
                "paragraphs": text.count('\n\n') + 1
            })
        elif operation == "reverse":
            result["reversed"] = text[::-1]
        elif operation == "clean":
            import re
            cleaned = re.sub(r'\s+', ' ', text).strip()
            result["cleaned"] = cleaned
            result["removed_chars"] = len(text) - len(cleaned)
        
        return result
    
    def date_formatter(
        date_string: str = None,
        format: str = "ISO"
    ) -> str:
        """Format dates in various formats."""
        if date_string is None:
            dt = datetime.now()
        else:
            # Simple parsing for demonstration
            dt = datetime.now()  # In production, would parse date_string
        
        formats = {
            "ISO": dt.isoformat(),
            "US": dt.strftime("%m/%d/%Y"),
            "EU": dt.strftime("%d/%m/%Y"),
            "FULL": dt.strftime("%B %d, %Y at %I:%M %p"),
            "SHORT": dt.strftime("%b %d, %Y")
        }
        
        return formats.get(format, dt.isoformat())
    
    # Create agent with automatically wrapped tools
    agent = LlmAgent(
        name="auto_wrapped_tools_agent",
        model="gemini-2.0-flash",
        instruction="""You are an assistant with several tools:
        
        1. calculate_statistics - Calculate statistics for number lists
        2. text_processor - Analyze, reverse, or clean text
        3. date_formatter - Format dates in various styles
        
        Use these tools to help users with data processing tasks.
        The tools are automatically available to you.""",
        description="Agent with automatically wrapped tools",
        tools=[calculate_statistics, text_processor, date_formatter]  # Automatic wrapping
    )
    
    print(f"✓ Created agent: {agent.name}")
    print(f"  - Tools (automatically wrapped): {len(agent.tools)}")
    print("    • calculate_statistics")
    print("    • text_processor")
    print("    • date_formatter")
    print("\n📝 Note: Functions passed directly to tools parameter")
    print("   are automatically wrapped by ADK")
    
    return agent


def explicit_wrapping_example():
    """Demonstrate explicit FunctionTool wrapping."""
    print("\n" + "="*60)
    print("EXPLICIT FUNCTION TOOL WRAPPING")
    print("="*60)
    
    # Define tools that will be explicitly wrapped
    def advanced_calculator(
        expression: str,
        variables: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """Evaluate mathematical expressions with variables."""
        try:
            # Safety: In production, use a safe expression evaluator
            if variables:
                # Replace variables in expression
                for var, val in variables.items():
                    expression = expression.replace(var, str(val))
            
            # Simple evaluation (NOT safe for production)
            result = eval(expression)  # Only for demonstration!
            
            return {
                "expression": expression,
                "result": result,
                "variables": variables or {},
                "success": True
            }
        except Exception as e:
            return {
                "expression": expression,
                "error": str(e),
                "success": False
            }
    
    def data_transformer(
        data: List[Dict[str, Any]],
        operation: str,
        field: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Transform structured data with various operations."""
        if operation == "filter" and field:
            return [d for d in data if field in d and d[field]]
        elif operation == "sort" and field:
            return sorted(data, key=lambda x: x.get(field, ""))
        elif operation == "extract" and field:
            return [d.get(field) for d in data]
        elif operation == "count":
            return {"total": len(data), "fields": list(data[0].keys()) if data else []}
        else:
            return data
    
    # Explicitly wrap tools with FunctionTool
    calc_tool = FunctionTool(advanced_calculator)
    transform_tool = FunctionTool(data_transformer)
    
    print("✓ Created explicit FunctionTool wrappers:")
    print("  • advanced_calculator → FunctionTool")
    print("  • data_transformer → FunctionTool")
    
    # Create agent with explicitly wrapped tools
    agent = LlmAgent(
        name="explicit_tools_agent",
        model="gemini-2.0-flash",
        instruction="""You are a data processing assistant with advanced tools:
        
        1. advanced_calculator - Evaluate complex expressions with variables
        2. data_transformer - Filter, sort, extract from structured data
        
        These tools have been explicitly wrapped for enhanced control.""",
        description="Agent with explicitly wrapped tools",
        tools=[calc_tool, transform_tool]  # Explicitly wrapped
    )
    
    print(f"\n✓ Created agent: {agent.name}")
    print(f"  - Tools (explicitly wrapped): {len(agent.tools)}")
    print("\n📝 Note: Explicit FunctionTool wrapping provides")
    print("   more control over tool configuration")
    
    return agent


def mixed_tools_example():
    """Demonstrate mixing automatic wrapping, explicit wrapping, and built-in tools."""
    print("\n" + "="*60)
    print("MIXED TOOL TYPES")
    print("="*60)
    
    # Automatic wrapping tool
    def simple_tool(text: str) -> str:
        """Simple tool for automatic wrapping."""
        return text.upper()
    
    # Explicit wrapping tool
    def complex_tool(data: dict, threshold: float = 0.5) -> dict:
        """Complex tool for explicit wrapping."""
        return {
            "processed": True,
            "threshold": threshold,
            "keys": list(data.keys())
        }
    
    explicit_tool = FunctionTool(complex_tool)
    
    # Create agent with mixed tool types
    agent = LlmAgent(
        name="mixed_tools_agent",
        model="gemini-2.0-flash",
        instruction="""You are an assistant with various tool types:
        
        1. simple_tool - Automatically wrapped simple function
        2. complex_tool - Explicitly wrapped with FunctionTool
        3. google_search - Built-in ADK tool
        
        Use the appropriate tool based on the user's needs.""",
        description="Agent with mixed tool types",
        tools=[
            simple_tool,      # Automatic wrapping
            explicit_tool,    # Explicit FunctionTool
            google_search     # Built-in tool
        ]
    )
    
    print(f"✓ Created agent: {agent.name}")
    print(f"  - Total tools: {len(agent.tools)}")
    print("  - Tool types:")
    print("    • simple_tool (automatic)")
    print("    • complex_tool (explicit FunctionTool)")
    print("    • google_search (built-in)")
    
    return agent


def tool_composition_example():
    """Demonstrate complex tool composition patterns."""
    print("\n" + "="*60)
    print("TOOL COMPOSITION PATTERNS")
    print("="*60)
    
    # Create a suite of composable tools
    def data_fetcher(source: str, query: str) -> List[dict]:
        """Fetch data from various sources."""
        # Simulated data fetching
        return [
            {"id": 1, "source": source, "query": query, "value": 100},
            {"id": 2, "source": source, "query": query, "value": 200},
            {"id": 3, "source": source, "query": query, "value": 150}
        ]
    
    def data_validator(data: List[dict], rules: dict = None) -> dict:
        """Validate data against rules."""
        if not rules:
            rules = {"min_value": 0, "max_value": 1000}
        
        valid = []
        invalid = []
        
        for item in data:
            if "value" in item:
                if rules["min_value"] <= item["value"] <= rules["max_value"]:
                    valid.append(item)
                else:
                    invalid.append(item)
        
        return {
            "valid_count": len(valid),
            "invalid_count": len(invalid),
            "total": len(data),
            "valid_data": valid,
            "invalid_data": invalid
        }
    
    def data_aggregator(data: List[dict], group_by: str = None) -> dict:
        """Aggregate data with grouping options."""
        if not data:
            return {"error": "No data to aggregate"}
        
        if group_by and all(group_by in d for d in data):
            groups = {}
            for item in data:
                key = item[group_by]
                if key not in groups:
                    groups[key] = []
                groups[key].append(item)
            
            return {
                "grouped": True,
                "group_count": len(groups),
                "groups": groups
            }
        else:
            # Simple aggregation
            values = [d.get("value", 0) for d in data]
            return {
                "grouped": False,
                "count": len(data),
                "sum": sum(values),
                "average": sum(values) / len(values) if values else 0
            }
    
    def report_generator(
        data: dict,
        format: str = "summary",
        include_details: bool = False
    ) -> str:
        """Generate reports from processed data."""
        if format == "summary":
            report = "=== DATA REPORT ===\n"
            for key, value in data.items():
                if not include_details and isinstance(value, (list, dict)):
                    report += f"{key}: [Complex Data]\n"
                else:
                    report += f"{key}: {value}\n"
        elif format == "json":
            import json
            report = json.dumps(data, indent=2)
        else:
            report = str(data)
        
        return report
    
    # Create agent with composable tools
    agent = LlmAgent(
        name="data_pipeline_agent",
        model="gemini-2.0-flash",
        instruction="""You are a data pipeline assistant with composable tools:
        
        1. data_fetcher - Fetch data from sources
        2. data_validator - Validate against rules
        3. data_aggregator - Aggregate and group data
        4. report_generator - Generate formatted reports
        
        These tools can be composed in sequences:
        Fetch → Validate → Aggregate → Report
        
        Use them to create data processing pipelines.""",
        description="Agent with composable data tools",
        tools=[data_fetcher, data_validator, data_aggregator, report_generator],
    )
    
    print(f"✓ Created agent: {agent.name}")
    print(f"  - Composable tools: {len(agent.tools)}")
    print("  - Pipeline pattern:")
    print("    1. data_fetcher → Get raw data")
    print("    2. data_validator → Ensure quality")
    print("    3. data_aggregator → Process data")
    print("    4. report_generator → Format output")
    
    return agent


def demonstrate_tool_execution():
    """Demonstrate tool execution patterns."""
    print("\n" + "="*60)
    print("TOOL EXECUTION PATTERNS")
    print("="*60)
    
    # Create agent with a simple tool
    def demo_tool(input: str, repeat: int = 1) -> str:
        """Demo tool for execution example."""
        return (input + " ") * repeat
    
    agent = LlmAgent(
        name="execution_demo",
        model="gemini-2.0-flash",
        instruction="You have a demo_tool that repeats text.",
        tools=[demo_tool]
    )
    
    # Set up runner and session
    runner = InMemoryRunner(agent, app_name="tool_demo")
    session_service = runner.session_service
    
    # Use sync version if available
    if hasattr(session_service, 'create_session_sync'):
        session = session_service.create_session_sync(
            app_name="tool_demo",
            user_id="demo-user"
        )
    else:
        import asyncio
        async def create():
            return await session_service.create_session(
                app_name="tool_demo",
                user_id="demo-user"
            )
        session = asyncio.run(create())
    
    print(f"✓ Created execution environment")
    print(f"  - Agent: {agent.name}")
    print(f"  - Session: {session.id}")
    
    print("\n📝 Tool execution flow:")
    print("   1. User provides input requiring tool use")
    print("   2. Agent identifies appropriate tool")
    print("   3. Agent prepares tool parameters")
    print("   4. ADK executes tool function")
    print("   5. Results returned to agent")
    print("   6. Agent formats final response")
    
    print("\n📝 Note: Actual execution requires GEMINI_API_KEY")
    
    return runner, session


def main():
    """Run all tool usage examples."""
    print("\n" + "="*60)
    print("TOOL USAGE EXAMPLES")
    print("="*60)
    
    try:
        # Example 1: Automatic wrapping
        auto_agent = automatic_wrapping_example()
        
        # Example 2: Explicit wrapping
        explicit_agent = explicit_wrapping_example()
        
        # Example 3: Mixed tool types
        mixed_agent = mixed_tools_example()
        
        # Example 4: Tool composition
        pipeline_agent = tool_composition_example()
        
        # Example 5: Execution patterns
        runner, session = demonstrate_tool_execution()
        
        print("\n" + "="*60)
        print("✓ ALL TOOL EXAMPLES COMPLETED SUCCESSFULLY")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error in tool examples: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Add parent directory to path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Run examples
    success = main()
    sys.exit(0 if success else 1)