#!/usr/bin/env python3
"""
Workflow Agent Examples
Demonstrates sequential, parallel, and loop workflow patterns
"""

import os
import sys
from typing import List
from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent, LoopAgent
from google.adk.runners import InMemoryRunner


def create_sequential_workflow() -> SequentialAgent:
    """Create a sequential workflow with multiple steps."""
    print("\n" + "="*60)
    print("CREATING SEQUENTIAL WORKFLOW")
    print("="*60)
    
    # Step 1: Data gatherer
    data_gatherer = LlmAgent(
        name="data-gatherer",
        model="gemini-2.0-flash",
        instruction="""You are the first step in a data processing pipeline.
        Your role is to gather and structure initial information.
        Extract key facts, dates, numbers, and entities.
        Pass structured data to the next step.""",
        description="Gathers and structures initial data"
    )
    
    # Step 2: Data analyzer
    data_analyzer = LlmAgent(
        name="data-analyzer",
        model="gemini-2.0-flash",
        instruction="""You are the analysis step in the pipeline.
        Analyze the structured data from the previous step.
        Identify patterns, trends, and anomalies.
        Calculate relevant metrics and statistics.""",
        description="Analyzes structured data"
    )
    
    # Step 3: Report generator
    report_generator = LlmAgent(
        name="report-generator",
        model="gemini-2.0-flash",
        instruction="""You are the final step - report generation.
        Take the analysis from the previous step.
        Create a clear, professional report with:
        - Executive summary
        - Key findings
        - Recommendations
        Format for easy reading.""",
        description="Generates final report"
    )
    
    # Create sequential workflow
    workflow = SequentialAgent(
        name="data-processing-pipeline",
        sub_agents=[data_gatherer, data_analyzer, report_generator],
        description="Sequential data processing workflow"
    )
    
    print(f"✓ Created sequential workflow: {workflow.name}")
    print(f"  - Steps: {len(workflow.sub_agents)}")
    for i, agent in enumerate(workflow.sub_agents, 1):
        print(f"    {i}. {agent.name}")
    
    return workflow


def create_parallel_workflow() -> ParallelAgent:
    """Create a parallel workflow for concurrent processing."""
    print("\n" + "="*60)
    print("CREATING PARALLEL WORKFLOW")
    print("="*60)
    
    # Create multiple parallel analyzers
    sentiment_analyzer = LlmAgent(
        name="sentiment-analyzer",
        model="gemini-2.0-flash",
        instruction="""Analyze sentiment and emotional tone.
        Identify: positive, negative, neutral sentiments.
        Note emotional indicators and intensity.""",
        description="Sentiment analysis specialist"
    )
    
    keyword_extractor = LlmAgent(
        name="keyword-extractor",
        model="gemini-2.0-flash",
        instruction="""Extract key terms and phrases.
        Identify: main topics, important entities, technical terms.
        Rank by relevance and frequency.""",
        description="Keyword extraction specialist"
    )
    
    summary_generator = LlmAgent(
        name="summary-generator",
        model="gemini-2.0-flash",
        instruction="""Create concise summaries.
        Focus on: main points, key decisions, action items.
        Keep summaries brief but comprehensive.""",
        description="Summary generation specialist"
    )
    
    fact_checker = LlmAgent(
        name="fact-checker",
        model="gemini-2.0-flash",
        instruction="""Verify factual claims and statements.
        Check: dates, numbers, names, technical facts.
        Flag uncertain or unverifiable claims.""",
        description="Fact verification specialist"
    )
    
    # Create parallel workflow
    workflow = ParallelAgent(
        name="multi-analysis-workflow",
        sub_agents=[sentiment_analyzer, keyword_extractor, summary_generator, fact_checker],
        description="Parallel multi-aspect analysis"
    )
    
    print(f"✓ Created parallel workflow: {workflow.name}")
    print(f"  - Parallel agents: {len(workflow.sub_agents)}")
    for agent in workflow.sub_agents:
        print(f"    • {agent.name}")
    
    return workflow


def create_loop_workflow() -> LoopAgent:
    """Create a loop workflow for iterative refinement."""
    print("\n" + "="*60)
    print("CREATING LOOP WORKFLOW")
    print("="*60)
    
    # Create the iterative refinement agent
    refiner = LlmAgent(
        name="content-refiner",
        model="gemini-2.0-flash",
        instruction="""You are an iterative content refiner.
        Each iteration should:
        1. Review the current content
        2. Identify areas for improvement
        3. Make specific enhancements
        4. Check if quality goals are met
        
        Improvements can include:
        - Clarity and readability
        - Accuracy and precision
        - Completeness
        - Professional tone
        - Grammar and style
        
        Stop when content meets high quality standards.""",
        description="Iterative content refinement",
        temperature=0.3  # Consistent refinements
    )
    
    # Create loop workflow
    workflow = LoopAgent(
        name="refinement-loop",
        sub_agent=refiner,
        max_iterations=5,
        description="Iterative content refinement loop"
    )
    
    print(f"✓ Created loop workflow: {workflow.name}")
    print(f"  - Sub-agent: {workflow.sub_agent.name}")
    print(f"  - Max iterations: {workflow.max_iterations}")
    
    return workflow


def create_nested_workflow() -> SequentialAgent:
    """Create a complex nested workflow combining patterns."""
    print("\n" + "="*60)
    print("CREATING NESTED WORKFLOW")
    print("="*60)
    
    # Phase 1: Initial processing (parallel)
    initial_analyzer = LlmAgent(
        name="initial-analyzer",
        model="gemini-2.0-flash",
        instruction="Perform initial analysis of input",
        temperature=0.3
    )
    
    initial_validator = LlmAgent(
        name="initial-validator",
        model="gemini-2.0-flash",
        instruction="Validate input format and completeness",
        temperature=0.2
    )
    
    phase1_parallel = ParallelAgent(
        name="phase1-parallel-processing",
        sub_agents=[initial_analyzer, initial_validator],
        description="Parallel initial processing"
    )
    
    # Phase 2: Deep analysis (sequential)
    deep_analyzer = LlmAgent(
        name="deep-analyzer",
        model="gemini-2.0-flash",
        instruction="Perform deep analysis on validated data",
        temperature=0.4
    )
    
    insight_generator = LlmAgent(
        name="insight-generator",
        model="gemini-2.0-flash",
        instruction="Generate insights from deep analysis",
        temperature=0.5
    )
    
    phase2_sequential = SequentialAgent(
        name="phase2-deep-processing",
        sub_agents=[deep_analyzer, insight_generator],
        description="Sequential deep processing"
    )
    
    # Phase 3: Refinement (loop)
    refiner = LlmAgent(
        name="output-refiner",
        model="gemini-2.0-flash",
        instruction="Refine and polish the final output",
        temperature=0.3
    )
    
    phase3_loop = LoopAgent(
        name="phase3-refinement",
        sub_agent=refiner,
        max_iterations=3,
        description="Iterative refinement"
    )
    
    # Combine all phases into main workflow
    main_workflow = SequentialAgent(
        name="complex-nested-workflow",
        sub_agents=[phase1_parallel, phase2_sequential, phase3_loop],
        description="Complex multi-phase nested workflow"
    )
    
    print(f"✓ Created nested workflow: {main_workflow.name}")
    print(f"  - Total phases: {len(main_workflow.sub_agents)}")
    print("  - Structure:")
    print("    1. Phase 1: Parallel processing (2 agents)")
    print("    2. Phase 2: Sequential processing (2 agents)")
    print("    3. Phase 3: Loop refinement (1 agent, max 3 iterations)")
    
    return main_workflow


def create_conditional_workflow_example():
    """Example of how to implement conditional workflow logic."""
    print("\n" + "="*60)
    print("CONDITIONAL WORKFLOW PATTERN")
    print("="*60)
    
    # Create specialized agents for different conditions
    technical_expert = LlmAgent(
        name="technical-expert",
        model="gemini-2.0-flash",
        instruction="""You are a technical expert.
        Handle technical questions about:
        - Programming and software
        - System architecture
        - Technical specifications
        Provide detailed, accurate technical responses.""",
        temperature=0.2
    )
    
    business_expert = LlmAgent(
        name="business-expert",
        model="gemini-2.0-flash",
        instruction="""You are a business expert.
        Handle business questions about:
        - Strategy and planning
        - Market analysis
        - Business operations
        Provide strategic business insights.""",
        temperature=0.4
    )
    
    creative_expert = LlmAgent(
        name="creative-expert",
        model="gemini-2.0-flash",
        instruction="""You are a creative expert.
        Handle creative tasks:
        - Content creation
        - Design concepts
        - Creative problem solving
        Provide innovative, creative solutions.""",
        temperature=0.8
    )
    
    # Router agent (would determine which expert to use)
    router = LlmAgent(
        name="request-router",
        model="gemini-2.0-flash",
        instruction="""You are a request router.
        Analyze incoming requests and determine:
        - Is this a technical question? → technical-expert
        - Is this a business question? → business-expert
        - Is this a creative task? → creative-expert
        
        Route to the appropriate expert.""",
        temperature=0.1  # Very deterministic routing
    )
    
    print("✓ Created conditional workflow components:")
    print(f"  - Router: {router.name}")
    print(f"  - Expert agents: 3")
    print("    • technical-expert")
    print("    • business-expert")
    print("    • creative-expert")
    
    print("\n📝 Note: In production, conditional routing would be")
    print("   implemented using the router's output to select experts")
    
    return router, [technical_expert, business_expert, creative_expert]


def demonstrate_workflow_execution():
    """Demonstrate workflow execution setup."""
    print("\n" + "="*60)
    print("WORKFLOW EXECUTION SETUP")
    print("="*60)
    
    # Create a simple workflow
    workflow = create_sequential_workflow()
    
    # Create runner for the workflow
    runner = InMemoryRunner(workflow, app_name="workflow-app")
    print(f"\n✓ Created InMemoryRunner for workflow: {workflow.name}")
    
    # Create session
    session_service = runner.session_service()
    session = session_service.create_session(
        app_name="workflow-app",
        user_id="workflow-user"
    )
    
    print(f"✓ Created session for workflow execution")
    print(f"  - Session ID: {session.id}")
    print(f"  - User ID: {session.user_id}")
    
    print("\n📝 Workflow execution pattern:")
    print("   1. Runner processes the workflow agent")
    print("   2. Each sub-agent executes in sequence/parallel/loop")
    print("   3. Results flow between agents as configured")
    print("   4. Final output returned from workflow")
    
    return runner, session


def main():
    """Run all workflow examples."""
    print("\n" + "="*60)
    print("WORKFLOW AGENT EXAMPLES")
    print("="*60)
    
    try:
        # Example 1: Sequential workflow
        sequential = create_sequential_workflow()
        
        # Example 2: Parallel workflow
        parallel = create_parallel_workflow()
        
        # Example 3: Loop workflow
        loop = create_loop_workflow()
        
        # Example 4: Nested workflow
        nested = create_nested_workflow()
        
        # Example 5: Conditional pattern
        router, experts = create_conditional_workflow_example()
        
        # Example 6: Execution setup
        runner, session = demonstrate_workflow_execution()
        
        print("\n" + "="*60)
        print("✓ ALL WORKFLOW EXAMPLES COMPLETED SUCCESSFULLY")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error in workflow examples: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Add parent directory to path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Run examples
    success = main()
    sys.exit(0 if success else 1)