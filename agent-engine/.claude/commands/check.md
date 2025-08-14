# Python + Database Code Quality Check

Perform a comprehensive code quality analysis of this Python project with Prisma/PostgreSQL:

## 1. **Code Structure & Standards**
   - Check PEP 8 compliance (line length, naming conventions, imports)
   - Verify proper module/package organization
   - Identify missing docstrings for classes and functions

## 2. **Database & Prisma Analysis**
   - **Schema Validation**: Check Prisma schema for proper relationships, indexes, and constraints
   - **Migration Safety**: Verify migrations don't risk data loss or breaking changes
   - **Query Efficiency**: Identify N+1 queries, missing indexes, or inefficient database calls
   - **Connection Management**: Check for proper connection pooling and cleanup
   - **Transaction Handling**: Verify proper transaction boundaries and rollback strategies

## 3. **Database Testing Coverage**
   - **Unit Tests**: Check for database model/repository unit tests
   - **Integration Tests**: Verify database integration test coverage
   - **Migration Tests**: Ensure migration rollback/forward testing
   - **Performance Tests**: Check for slow query identification
   - **Data Integrity Tests**: Verify constraint and validation testing

## 4. **Security & Best Practices**
   - Scan for SQL injection vulnerabilities
   - Check for hardcoded database credentials
   - Verify proper error handling for database operations
   - Validate input sanitization for database queries

## 5. **Performance & Efficiency**
   - Identify inefficient database query patterns
   - Check for missing database indexes
   - Verify proper use of Prisma's query optimization features
   - Spot potential connection leaks or resource management issues

## 6. **Testing & Maintainability**
   - Assess database test coverage gaps
   - Check for proper test database setup/teardown
   - Verify mock vs real database testing strategy
   - Identify overly complex database operations

## 7. **Dependencies & Configuration**
   - Verify Prisma client generation and version compatibility
   - Check database environment configuration
   - Validate connection string security and parameterization

**Output Format:**
- ✅ **Passed**: List compliant areas
- ⚠️  **Warnings**: List minor issues with quick fixes  
- ❌ **Critical**: List serious issues requiring immediate attention
- 🗄️ **Database Issues**: Specific Prisma/PostgreSQL concerns
- 📋 **Recommendations**: Suggest improvements for early-stage development

Focus on issues that matter most for a project in early development phase, with special attention to database integrity and performance foundations.