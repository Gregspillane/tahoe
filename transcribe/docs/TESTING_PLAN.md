# Testing Infrastructure Plan

**Created**: August 15, 2025  
**Status**: Planning Phase  
**Priority**: High (Regression Prevention)

## Overview

With the dual-provider transcription pipeline now fully operational, we need comprehensive testing infrastructure to prevent regressions and ensure reliable development.

## Current Testing Gaps

### 🚨 Critical Issues Discovered
- **Parameter Reference Bugs**: `original_google` → `original_openai` errors could recur
- **Provider Integration**: No automated validation of AssemblyAI + OpenAI client changes
- **Reconciliation Logic**: Complex Gemini reasoning needs systematic testing
- **JSON Schema**: Format changes could break provider compatibility

## Proposed Directory Structure

```
tests/
├── unit/
│   ├── test_assemblyai_client.py         # AssemblyAI client unit tests
│   ├── test_openai_client.py             # OpenAI client unit tests  
│   ├── test_gemini_client.py             # Gemini reconciliation unit tests
│   ├── test_reconciler.py                # Reconciliation orchestrator tests
│   └── test_s3_manager.py                # S3 operations unit tests
├── integration/
│   ├── test_dual_provider_pipeline.py    # End-to-end pipeline tests
│   ├── test_reconciliation_scenarios.py  # Various reconciliation test cases
│   └── test_worker_pipeline.py           # Full worker processing tests
├── fixtures/
│   ├── sample_assemblyai_response.json   # Mock AssemblyAI responses
│   ├── sample_openai_response.json       # Mock OpenAI responses
│   ├── sample_audio_metadata.json        # Test audio file metadata
│   └── reconciliation_test_cases.json    # Standard reconciliation scenarios
├── regression/
│   ├── test_parameter_consistency.py     # Prevent google→openai parameter bugs
│   ├── test_json_schema_validation.py    # Ensure consistent JSON output
│   └── test_name_correction.py           # Hunt & Henriques validation
└── conftest.py                          # PyTest configuration and fixtures
```

## Test Categories

### 1. Unit Tests
**Purpose**: Validate individual components in isolation

- **AssemblyAI Client**: Mock HTTP responses, test error handling
- **OpenAI Client**: Validate `verbose_json` format handling  
- **Gemini Client**: Test prompt generation and response parsing
- **S3Manager**: Mock S3 operations, credential handling

### 2. Integration Tests  
**Purpose**: Validate component interactions

- **Dual-Provider Pipeline**: Full AssemblyAI + OpenAI → Gemini flow
- **Reconciliation Scenarios**: Various text differences and corrections
- **Worker Processing**: Complete job lifecycle with mock providers

### 3. Regression Tests
**Purpose**: Prevent specific bugs from recurring

- **Parameter Consistency**: Automated check for `original_google` references
- **JSON Schema Validation**: Ensure provider output compatibility  
- **Name Correction**: Validate Hunt & Henriques scenario always works

### 4. Fixtures & Mock Data
**Purpose**: Standardized test data for consistent testing

- **Provider Responses**: Realistic mock data from both providers
- **Audio Metadata**: Various file types and configurations
- **Reconciliation Cases**: Standard scenarios for testing reasoning

## Implementation Priority

### Phase 1: Critical Regression Prevention
1. **test_parameter_consistency.py**: Scan codebase for `original_google` patterns
2. **test_name_correction.py**: Automated Hunt & Henriques validation
3. **test_json_schema_validation.py**: Provider output format verification

### Phase 2: Component Validation  
1. **Provider client unit tests**: Individual AssemblyAI/OpenAI validation
2. **Reconciliation unit tests**: Gemini client response parsing
3. **Integration test framework**: End-to-end pipeline validation

### Phase 3: Production Readiness
1. **Real audio file testing**: Resolve S3 credential issues
2. **Performance testing**: Load testing with multiple concurrent jobs
3. **Error scenario testing**: Network failures, API timeouts, malformed responses

## Test Execution Strategy

### Continuous Integration
```bash
# Fast feedback loop - unit tests only
pytest tests/unit/ --verbose

# Regression prevention - critical bug checks  
pytest tests/regression/ --verbose

# Full validation - all tests including integration
pytest tests/ --verbose --slow
```

### Pre-deployment Validation
```bash
# Name correction validation
pytest tests/regression/test_name_correction.py -v

# Parameter consistency check
pytest tests/regression/test_parameter_consistency.py -v

# Provider compatibility validation  
pytest tests/integration/test_dual_provider_pipeline.py -v
```

## Testing Tools & Frameworks

### Core Testing Stack
- **PyTest**: Primary testing framework with fixtures
- **pytest-mock**: Mocking for external API calls
- **pytest-asyncio**: Async test support for worker pipelines
- **pytest-cov**: Code coverage reporting

### Mock & Fixture Strategy
- **requests-mock**: Mock HTTP calls to AssemblyAI/OpenAI/Gemini
- **moto**: Mock AWS S3 operations for storage testing
- **Factory pattern**: Generate test data with realistic variations

## Success Metrics

### Code Quality
- **90%+ test coverage** on core reconciliation logic
- **Zero regression bugs** in parameter references  
- **Automated validation** of name correction capabilities

### Developer Experience  
- **< 30 second** unit test execution time
- **Clear error messages** when tests fail
- **Easy test data creation** with fixture factories

### Production Confidence
- **Automated pre-deployment checks** preventing broken releases
- **Real audio file validation** before production updates
- **Performance benchmarks** ensuring system scales

## Next Steps

1. **Create directory structure**: Set up `tests/` with proper organization
2. **Implement regression tests**: Focus on parameter consistency first  
3. **Build fixture framework**: Standardized mock data for all test types
4. **Integrate with development workflow**: Automated testing on code changes
5. **Document testing procedures**: Guide for future developers

This comprehensive testing infrastructure will ensure the dual-provider transcription pipeline remains reliable and maintainable as the system evolves.