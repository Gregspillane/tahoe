# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview



### Service Independence
- Each service is **completely self-contained** with its own:
  - API endpoints and authentication
  - Database schema (within shared PostgreSQL)
  - Cache namespace (within shared Redis)
  - Deployment configuration
  - DNS/domain (e.g., agent.tahoe.com, auth.tahoe.com)
- Services communicate via **service-to-service tokens**
- No centralized API gateway - each service exposes its own API
- **Centralized configuration**: All services use the monorepo root `.env` with service-specific prefixes

### Data Architecture
- **PostgreSQL**: Shared instance with service-specific schemas
  - `agent_engine` schema for agent-engine service
  - `auth` schema for auth service (future)
  - `billing` schema for billing service (future)
- **Redis**: Shared instance with namespaced keys
  - `agent-engine:*` keys for agent-engine
  - `auth:*` keys for auth service
  - Services cannot access each other's data directly

### agent-engine Service
The `agent-engine` service is the core intelligence layer providing multi-agent orchestration for compliance analysis. It operates independently at its own domain and coordinates specialized AI agents.

**Key Technologies (agent-engine)**:
- **Language**: Python 3.11
- **Framework**: FastAPI for API layer
- **Agent Framework**: Google ADK (Agent Development Kit)
- **Database**: PostgreSQL with Prisma ORM
- **Cache**: Redis
- **Models**: Gemini (primary), with support for OpenAI and Anthropic

## Core Development Principles

### Apply These Fundamental Guidelines
- **KISS (Keep It Simple, Stupid)**: Choose the most straightforward solution that works. Avoid unnecessary complexity. 
- **Incremental Progress**: Make small, testable changes rather than large sweeping modifications.
- **Configuration-Driven**: Agents and workflows are defined through database configuration, not code changes

The memory bank provides persistent context across sessions:

### Active Context
- **Location**: `/memory-bank/` - Contains living project documents
- **Key Files**:
  - `context.md` - Session handoffs and current state
  - `architecture.md` - Technical patterns and decisions
  - `progress.md` - Development status tracking
  - `decisions.md` - Key project decisions log

### Archived Documentation
- **Location**: `/memory-bank/archive/` - Completed plans and historical trackers
- Move documents here when they're no longer actively needed
- Maintain organized subdirectories by date or feature

### Using the Memory Bank
1. **Start of session**: Read `context.md` for current state
2. **During work**: Update relevant documents as you progress
3. **End of session**: Write handoff notes in `context.md`
4. **Major decisions**: Log in `decisions.md` with reasoning

## Development Workflow Guidelines

### Before Making Changes
1. **Understand the context**: Read relevant files and documentation
2. **Plan your approach**: Think through the implementation before coding
3. **Check for impacts**: Consider downstream effects of changes
4. **Validate assumptions**: Verify your understanding with the user when uncertain

### During Development
1. **Make incremental changes**: Small, focused commits
2. **Test as you go**: Verify each change works before moving on
3. **Document your reasoning**: Add comments for non-obvious decisions
4. **Keep the user informed**: Report progress and any issues encountered

### After Changes
1. **Verify functionality**: Ensure changes work as intended
2. **Check for regressions**: Confirm nothing else broke
3. **Update documentation**: Keep README and other docs current
4. **Clean up**: Remove debug code and temporary files

## Code Quality Standards

### General Best Practices
- Write clear, self-documenting code
- Use meaningful variable and function names
- Keep functions small and focused (single responsibility)
- Handle errors gracefully with proper error messages
- Add comments for complex logic or business rules
- Follow existing code patterns and conventions

### Testing Philosophy
- Write tests for critical functionality
- Test edge cases and error conditions
- Keep tests simple and readable
- Use descriptive test names that explain what's being tested
- Maintain test coverage without obsessing over percentages

### Performance Considerations
- Optimize only when necessary (measure first)
- Consider scalability in design decisions
- Be mindful of resource usage (memory, CPU, network)
- Cache expensive operations when appropriate
- Profile before optimizing

## Core Principles

- **No Mocks or Workarounds**: Implement real solutions that will scale to production. Avoid temporary fixes or placeholder code.
- **Root Cause Focus**: Always address the underlying architectural issue rather than patching symptoms.
- **KISS with Sustainability**: Keep implementations simple while ensuring they're maintainable and extensible for long-term growth.
- **Fail Fast Philosophy**: No silent failures or fallback behaviors. Systems should fail explicitly and early when issues occur.
- **Clean Architecture First**: As a pre-launch application, prioritize establishing proper architectural patterns over quick feature delivery.

## Implementation Standards

- Build every component as if it's going into production tomorrow
- Design for observability and debugging from the start
- Ensure all error states are explicit and actionable
- Create clear separation of concerns in all architectural decisions