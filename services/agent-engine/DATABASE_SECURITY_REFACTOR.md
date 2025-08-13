# DATABASE_SECURITY_REFACTOR.md

## Goal
Secure database configuration and implement proper connection management with transactions for the agent-engine service

## Current State
- **Config**: Database credentials hardcoded in `src/config.py` (DATABASE_PASSWORD="tahoe")
- **Connections**: Direct Prisma client usage without pooling configuration in `src/models/database.py`
- **Transactions**: No transaction boundaries for multi-step operations in `src/orchestrator.py`
- **Schema**: Well-structured but missing CASCADE rules and unique constraints in `prisma/schema.prisma`
- **Validation**: Limited input validation for JSON fields across API endpoints

## Plan
1. Move database credentials to environment variables in `src/config.py`
2. Configure Prisma connection pooling in `src/models/database.py` and `prisma/schema.prisma`
3. Implement transaction wrapper for analysis creation/update in `src/orchestrator.py`
4. Add CASCADE delete rules to schema relationships in `prisma/schema.prisma`
5. Create Pydantic models for JSON field validation in `src/models/api.py`
6. Add retry logic for database operations in `src/models/database.py`
7. Implement rate limiting middleware in `src/main.py`
8. Add unique constraints for business keys in `prisma/schema.prisma`

## Progress
- [x] Step 1 - Environment variables configured and .env.example updated
- [x] Step 2 - Connection pool with 10 connections configured
- [x] Step 3 - Transaction wrapper implemented for analyze_interaction
- [x] Step 6 - Exponential backoff retry logic added (3 retries, 1-2-4 seconds)
- [ ] Step 4 - CASCADE rules added to all foreign key relationships
- [ ] Step 5 - JSON field validators created for modelConfig, requirements, results
- [ ] Step 7 - Rate limiter added (100 requests/minute per IP)
- [ ] Step 8 - Unique constraints on portfolio.name, tool.name verified

## Key Files
- `src/config.py` - Remove hardcoded credentials, use env vars only
- `src/models/database.py` - Add connection pooling, retry logic, transaction context
- `src/orchestrator.py` - Wrap analysis operations in transactions
- `prisma/schema.prisma` - Add CASCADE, unique constraints, pool config
- `src/models/api.py` - Add Pydantic validators for JSON fields
- `src/main.py` - Add rate limiting middleware
- `.env.example` - Document all required environment variables

## Context & Decisions
- **Critical**: Database password "tahoe" is exposed in source code
- **Pattern**: Use Prisma's built-in connection pooling (connection_limit=10)
- **Transaction Strategy**: Use Prisma's interactive transactions for multi-step operations
- **Retry Policy**: Only retry on connection errors, not business logic failures
- **Rate Limiting**: Use slowapi library for FastAPI rate limiting
- **Validation**: All JSON fields must have corresponding Pydantic models
- **Migration Safety**: Test all schema changes with rollback before applying

## Session Notes
### Session 1 - 2025-08-13
- Completed comprehensive code quality analysis
- Identified critical security issue with hardcoded database password
- Found missing transaction boundaries in orchestrator
- Discovered N+1 query risks in scorecard endpoints
- **COMPLETED**: Secured database credentials (removed hardcoded password)
- **COMPLETED**: Added connection pooling (10 connections, 30s timeout)
- **COMPLETED**: Implemented retry logic with exponential backoff
- **COMPLETED**: Added transaction wrapper in database manager
- **COMPLETED**: Updated orchestrator to use database manager
- **TESTED**: All security improvements verified with test script
- Next: Optional improvements (CASCADE rules, rate limiting, validators)

## Verification
- [ ] No hardcoded credentials in codebase (grep for PASSWORD, SECRET, KEY)
- [ ] Database operations handle connection failures gracefully
- [ ] Multi-step operations rollback on failure
- [ ] API endpoints reject invalid JSON input with 400 errors
- [ ] Load test shows connection pool handles 100 concurrent requests
- [ ] CASCADE deletes work correctly (test with portfolio deletion)
- [ ] Rate limiting returns 429 status when exceeded
- [ ] All existing tests still pass
- [ ] New integration tests for transactions pass