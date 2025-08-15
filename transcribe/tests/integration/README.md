# Integration Tests

Integration tests verify that components work together correctly and that external services are properly configured.

## Test Files

### `test_api_keys.py`
**Purpose**: Validates that all API keys are properly configured and functional.

**Tests**:
- AssemblyAI API key authentication
- OpenAI API key authentication  
- Google API key authentication
- S3/AWS credentials validation

**Usage**:
```bash
python test_api_keys.py
```

### `test_providers.py`
**Purpose**: Tests individual transcription providers with real API calls.

**Tests**:
- S3Manager file operations
- AssemblyAI client with real audio
- OpenAI client with real audio
- End-to-end provider pipeline

**Usage**:
```bash
python test_providers.py
```

## Requirements

These tests require:
- All API keys configured in `.env` file
- Real S3 bucket access
- Network connectivity to external APIs
- Test audio files in `tests/fixtures/`

## Notes

- These tests make actual API calls and may incur costs
- Use for debugging provider integration issues
- For automated testing, use the pytest-based tests in `tests/regression/`