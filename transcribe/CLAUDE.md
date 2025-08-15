# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Development Commands

### Service Management
```bash
# Start dependencies (PostgreSQL and Redis)
docker-compose up -d postgres redis

# Start main service with auto-reload
python main.py

# Full Docker stack
docker-compose up

# Run tests
pytest tests/

# Code formatting and linting
black .
isort .
mypy .
```

### Database Operations
```bash
# Generate Prisma client
prisma generate

# Apply database migrations
prisma db push

# Reset database (development only)
prisma db push --force-reset
```

### Testing API Endpoints
```bash
# Submit test job
curl -X POST "http://localhost:9100/test/submit-job?audio_file_url=s3://bucket/test.mp3"

# Check job status
curl "http://localhost:9100/test/job-status/{job_id}"

# Service health and metrics
curl "http://localhost:9100/health"
curl "http://localhost:9100/status"
```

## Architecture Overview

### Multi-Provider Transcription Service
This is a production-grade transcription service that processes audio files using multiple providers (AssemblyAI and Google Cloud Speech) with intelligent reconciliation. The service uses a queue-based architecture for scalable processing.

### Core Architecture Components

**Queue-Based Processing System**
- Redis-backed job queue with proper claiming/timeout mechanisms
- Worker pool manages parallel processing (default 4 workers)
- Job states: PENDING → PROCESSING → COMPLETED/FAILED
- Automatic retry logic with exponential backoff

**Multi-Provider Strategy**
- **AssemblyAI**: Primary provider with speaker diarization
- **Google Cloud Speech Chirp 2**: Secondary provider for cross-validation
- **Future**: GPT-5-mini reconciliation for discrepancy resolution
- Results stored separately before reconciliation

**S3 Integration Pattern**
- Unified S3Manager handles both download-to-temp and presigned URL patterns
- Different providers require different access methods
- Automatic cleanup of temporary files
- File validation and metadata extraction

**Database Design (Prisma/PostgreSQL)**
- `TranscriptionJob`: Main job tracking with provider results
- `TranscriptionMetrics`: Performance and confidence data per provider
- `DiscrepancyLog`: Reconciliation decisions and conflicts
- `Webhook`/`WebhookDelivery`: Event notification system
- `FileProcessingLog`: S3 file discovery audit trail

### Key Service Patterns

**Worker Pattern**
- `WorkerPoolManager` orchestrates multiple `TranscriptionWorker` instances
- Each worker claims jobs atomically from Redis queue
- Parallel provider execution within single job
- Comprehensive error handling and status updates

**Provider Abstraction**
- `AssemblyAIClient`: Upload-based workflow with polling
- `GoogleSpeechClient`: Presigned URL workflow with direct API calls
- Standardized result format for downstream reconciliation
- Provider-specific error handling and retry logic

**Configuration Management**
- Pydantic settings with environment variable validation
- Required: AWS credentials, provider API keys, database URLs
- Provider-specific settings (models, language codes, etc.)

## Development Context

### Current Project Status
The service is in MVP development phase with Phase 3 (Transcription Core) nearly complete. Both AssemblyAI and Google Speech providers are implemented and working. The next major milestone is Phase 4 (Intelligent Reconciliation) using GPT-5-mini.

**Known Issues:**
- Google Cloud Speech authentication occasionally requires credential refresh
- Reconciliation logic not yet implemented (currently returns combined results)

### Key Files and Responsibilities
- `main.py`: FastAPI application with service lifecycle management
- `jobs/job_manager.py`: Redis queue operations and job persistence
- `workers/`: Worker pool and individual transcription workers
- `transcription/`: Provider client implementations
- `storage/s3_manager.py`: Unified S3 operations
- `config/settings.py`: Pydantic configuration with environment validation

### Environment Requirements
```bash
# Required environment variables
DATABASE_URL=postgresql://user:pass@localhost:5433/transcription
REDIS_URL=redis://localhost:6379
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
S3_AUDIO_BUCKET=...
S3_TRANSCRIPT_BUCKET=...
ASSEMBLYAI_API_KEY=...
GOOGLE_PROJECT_ID=...
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
SERVICE_AUTH_TOKEN=...
```

### Testing Strategy
- Use `/test/` endpoints to bypass authentication during development
- Real provider integration (no mocks) for accurate testing
- Monitor `/status` endpoint for queue metrics and worker health
- Check `docker-compose logs` for detailed service logs

### Development Workflow
1. Start dependencies: `docker-compose up -d postgres redis`
2. Run service: `python main.py` (auto-reload enabled)
3. Submit test jobs via `/test/submit-job` endpoint
4. Monitor progress via `/test/job-status/{id}` and `/status`
5. Check database for detailed job history and metrics