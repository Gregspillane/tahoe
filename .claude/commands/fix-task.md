# Task Correction Implementation with Documentation Verification

## Your Task
Based on the validation results provided, update the task YAML to accurately reflect the requirements from @MASTERPLAN.md while ensuring all ADK (Agent Development Kit) components align with the official documentation.

## Pre-Correction Verification

### 1. Documentation Cross-Reference
Before making corrections, verify ADK-specific components against official documentation:

**USE WEB SEARCH** to validate the following at https://google.github.io/adk-docs/:
- **ADK Class Structures**: Verify correct class names, methods, and inheritance patterns
- **Import Statements**: Confirm proper import paths and module organization
- **Agent Lifecycle**: Validate agent initialization, execution, and cleanup patterns
- **Parallel/Sequential Execution**: Check correct implementation of ParallelAgent and SequentialAgent
- **Context Passing**: Verify proper context and state management between agents
- **Result Aggregation**: Confirm aggregation patterns and interfaces
- **Error Handling**: Validate ADK-specific error handling and recovery patterns
- **Configuration**: Check scorecard and agent configuration structures

### 2. Search Queries to Execute
Perform targeted searches for:
site:google.github.io/adk-docs/ [specific component]

Priority searches:
- `site:google.github.io/adk-docs/ Agent class`
- `site:google.github.io/adk-docs/ ParallelAgent SequentialAgent`
- `site:google.github.io/adk-docs/ AgentFactory`
- `site:google.github.io/adk-docs/ ResultAggregator`
- `site:google.github.io/adk-docs/ context passing`
- `site:google.github.io/adk-docs/ orchestration`
- `site:google.github.io/adk-docs/ scorecard configuration`

## Correction Process

### 1. Review Validation Results
Analyze the validation output to understand:
- What needs to be corrected (❌ sections)
- What's missing (⚠️ sections)
- Required corrections list
- Risk assessment implications

### 2. Verify Against ADK Documentation
**CRITICAL**: Before implementing corrections:
- Search ADK docs for each component mentioned in validation
- Confirm correct class signatures and methods
- Validate import paths match documentation
- Ensure architectural patterns align with ADK best practices
- Check for any deprecated or updated patterns

### 3. Apply Corrections to Task YAML
Update the task structure to:
- Fix incorrect specifications based on BOTH masterplan AND ADK docs
- Add missing requirements with proper ADK patterns
- Correct file paths and names per ADK conventions
- Include proper imports verified against documentation
- Add missing methods with correct ADK signatures
- Align with both masterplan architecture and ADK standards

### 4. Preserve Working Elements
Keep intact:
- Correctly specified items (✅ sections)
- Valid workflow phases that match ADK patterns
- Accurate implementation logic
- Proper integration points

## Output Format

Provide the complete, corrected task YAML with:
1. All inaccuracies fixed
2. Missing elements added
3. Proper alignment with masterplan
4. ADK documentation compliance verified
5. Comments marking significant changes:
   - `# CORRECTED: [reason]`
   - `# ADDED: [from masterplan/ADK docs]`
   - `# VERIFIED: [ADK docs section]`

## Documentation Alignment Checklist

Verify these ADK components are correctly specified:
- [ ] Agent base class inheritance
- [ ] Proper agent initialization parameters
- [ ] Correct execute() method signature
- [ ] Valid context object structure
- [ ] Proper result format
- [ ] Correct error handling patterns
- [ ] Valid scorecard trigger rules format
- [ ] Proper agent configuration schema
- [ ] Correct factory pattern implementation
- [ ] Valid aggregation interfaces

## Correction Guidelines

- **ADK Compliance**: Every ADK component must match official documentation
- **File Structure**: Ensure files match both masterplan and ADK conventions
- **Imports/Dependencies**: Include all required imports with verified paths
- **Methods/Functions**: Add all helper methods with correct signatures
- **Class Structure**: Align with ADK's class hierarchy
- **Integration Points**: Include proper stubs matching ADK interfaces
- **Implementation Details**: Match both masterplan and ADK specifications

## Focus Areas

1. **Documentation Accuracy**: All ADK components verified against official docs
2. **Critical Fixes**: Address items that would cause runtime errors
3. **Architectural Alignment**: Ensure structure matches both masterplan and ADK
4. **Interface Consistency**: Maintain correct ADK interfaces for future integration
5. **Complete Coverage**: Include all required functionality per documentation

## Validation Note
If any ADK component cannot be verified in documentation:
- Note it with `# UNVERIFIED: Could not find in ADK docs`
- Provide best interpretation based on masterplan
- Flag for manual review

Update the YAML file so its ready for implementation with full ADK compliance. The end result should be a fully accurate YAML file that we can use for development. 