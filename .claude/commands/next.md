# Task Accuracy Validation

## Your Task
Validate that the next task you are about to implement accurately reflects the requirements in @MASTERPLAN.md. Identify any misalignments or missing elements before you begin coding.

## Validation Process

### 1. Extract Task Requirements
From the task YAML, identify:
- What it claims to implement
- Business logic it covers
- User flows it enables
- Technical specifications

### 2. Cross-Reference Masterplan
Find corresponding sections in @MASTERPLAN.md:
- Locate the user journey/workflow
- Find the business rules
- Check technical specifications
- Verify integration requirements

### 3. Gap Analysis
Compare task against masterplan to find:
- **Missing Requirements**: What the task doesn't cover
- **Incorrect Specifications**: Where task deviates from plan
- **Incomplete Logic**: Business rules not fully captured
- **Wrong Assumptions**: Misunderstood requirements

## Output Format

```markdown
# Task Validation: [Task ID]

## Task Claims vs Masterplan Reality

✅ **Correctly Specified**:
- [Accurate requirement]

❌ **Inaccurate/Missing**:
- **Task says**: [What task specifies]
  **Masterplan says**: [Actual requirement]
  **Impact**: [What happens if built as specified]

⚠️ **Incomplete Coverage**:
- **Missing**: [Required element not in task]
  **Found in**: [@MASTERPLAN.md#section]

## Required Task Corrections
1. [Specific fix needed]
2. [Additional requirement to add]
3. [Logic to correct]

## Risk Assessment
- **If built as-is**: [What breaks or doesn't work]
- **Severity**: [High/Medium/Low]
```

## Focus On
- User workflow accuracy
- Business logic completeness  
- Integration requirements
- Data model alignment
- Success criteria validity

Skip minor wording differences - focus on implementation-impacting discrepancies.