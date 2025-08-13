# Task Completion Validation

## Your Task
Validate the just-completed task implementation against @MASTERPLAN.md before proceeding to the next task. Ensure we're building the right thing with production-quality code that serves the application's intended purpose.

## Validation Steps

### 1. Task Implementation Review
Review what was just built:
- Core functionality delivered
- Integration points created
- Business logic implemented
- Technical decisions made

### 2. Spirit of the Application Check
Beyond literal compliance, verify the implementation serves the application's purpose:
- **User Experience**: Does this make the intended workflow better/easier?
- **Business Goals**: Does it advance the core value proposition?
- **System Coherence**: Does it fit naturally with existing components?
- **Future Readiness**: Does it enable planned features without blocking them?

### 3. Masterplan Alignment
Cross-reference implementation with @MASTERPLAN.md:
- Matches specified architecture patterns
- Follows documented user journeys
- Implements business rules correctly
- Respects technical constraints

### 4. Code Quality Scan
Check for issues that will cause problems later:
- Workarounds or temporary fixes
- TODOs/FIXMEs left in code
- Missing error handling
- Code duplication or complexity
- Untested critical paths

### 5. Cross-Task Impact
Verify this task's implementation:
- Properly integrates with previous tasks
- Sets up clean interfaces for upcoming tasks
- Doesn't break existing functionality
- Maintains consistent patterns

## Output Format

```markdown
# Task Validation Report

## Implementation Summary
- **Completed Task**: [ID and name from context]
- **Next Task**: [ID and name from context]
- **Core Deliverables**: [What was built]
- **Key Integration Points**: [How it connects]

## Spirit Alignment
✅ **Advances Application Goals**:
- [How it improves user experience]
- [How it serves business purpose]

⚠️ **Concerns**:
- [Any divergence from intended spirit]
- [Potential user friction points]

## Technical Validation
✅ **Correct Implementation**:
- [Matches masterplan architecture]
- [Business logic properly implemented]

❌ **Must Fix Before Next Task**:
- [Critical issues]
- [Breaking changes needed]

🔧 **Technical Debt Found**:
- [Workarounds to replace]
- [TODOs to complete]
- [Missing tests/validation]

## Next Task Readiness
- **Prerequisites Met**: [Yes/No + details]
- **Clean Handoff Points**: [Interfaces ready for next task]
- **Blocking Issues**: [What must be fixed first]

## Decision
[ ] ✅ Ready to proceed to next task
[ ] 🔧 Fix issues first, then proceed
[ ] ❌ Major correction needed

## Fix List (if applicable)
1. [Specific fix with file/line]
2. [Another fix]
3. [Continue until all issues resolved]