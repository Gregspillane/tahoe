# Transcription Service - Development Masterplan

**Version**: 1.0  
**Date**: August 2025  
**Status**: Local Development Focus

---

## Executive Summary

The Transcription Service is a standalone Docker-based service that pulls audio files from S3, transcribes them using multiple providers (AssemblyAI and OpenAI gpt-4o-transcribe), intelligently reconciles discrepancies using GPT-5-mini reasoning, and produces high-accuracy transcripts formatted for downstream analysis. This masterplan focuses on building a robust, queue-based processing system with emphasis on accuracy over speed, optimized for compliance call monitoring.

---

## Critical Implementation Guidelines

### 1. Multi-Provider Transcription Strategy
**Core principle: Accuracy through redundancy and intelligent reconciliation**
- **Parallel transcription** using AssemblyAI and OpenAI gpt-4o-transcribe
- **LLM-based reconciliation** using GPT-5-mini to resolve discrepancies
- **Confidence scoring** to weight provider outputs
- **Format optimization** for downstream consumption
- **Fallback mechanisms** when one provider fails

### 2. KISS Principle (Keep It Simple, Stupid)
- **Start with S3 polling** - simple file discovery mechanism
- **Use proven queue patterns** - Redis or RabbitMQ for job management
- **PostgreSQL for state** - consistent database choice
- **Structured output formats** - Markdown or YAML for easy parsing
- **Incremental complexity** - add features only when needed

### 3. No Mocks, No Stubs - Build Real Functionality
- **Connect to real S3** from day one
- **Use actual transcription APIs** with real credentials
- **Implement real LLM reconciliation** using GPT-5-mini
- **Store actual transcripts** in S3 with proper structure
- **Real queue processing** with actual parallel workers

### 4. Transcription Model Configuration
**Primary Models for Multi-Provider Strategy:**
- **AssemblyAI**: Industry-leading accuracy with built-in features for compliance
- **OpenAI**: `gpt-4o-transcribe` for superior Word Error Rate (WER)
- **Reconciliation LLM**: `gpt-5-mini-2025-08-07` for discrepancy resolution
- **API Key Management**: Environment variables in .env file
- **Parallel processing**: Both providers transcribe simultaneously for comparison

---

## Service Architecture

### High-Level Flow

```
[S3 Audio Files] → [File Discovery] → [Job Queue]
                                           ↓
                                    [Worker Pool]
                                           ↓
                            ┌──────────────┴──────────────┐
                            ↓                             ↓
                      [AssemblyAI]              [OpenAI GPT-4o-transcribe]
                            ↓                             ↓
                            └──────────────┬──────────────┘
                                           ↓
                              [Reconciliation (GPT-5-mini)]
                                           ↓
                                   [Format Optimization]
                                           ↓
                                    [S3 Storage]
                                           ↓
                                 [Webhook Notifications]
```

### Core Components

1. **File Discovery Service**
   - Polls S3 bucket for new MP3 files
   - Maintains processing state in PostgreSQL
   - Creates jobs in processing queue
   - Handles retry logic for failed files

2. **Queue Management**
   - Redis-based job queue with Bull framework
   - Priority queuing based on client/urgency
   - Dead letter queue for failed jobs
   - Job status tracking and monitoring

3. **Transcription Workers**
   - Parallel processing pool (configurable size)
   - Handles both Google and OpenAI API calls
   - Implements retry logic with exponential backoff
   - Captures confidence scores and timestamps

4. **Reconciliation System**
   - LLM-based discrepancy resolution using GPT-5-mini
   - Weighted merging based on confidence scores
   - Segment-by-segment comparison
   - Generates reconciliation report

5. **Format Optimization**
   - Structured output generation (Markdown/YAML)
   - Metadata extraction and enrichment
   - Speaker identification and labeling
   - Compliance-focused formatting

6. **Storage & Delivery**
   - S3 storage with organized structure
   - PostgreSQL for metadata and state
   - Webhook notifications for completion events
   - API for transcript retrieval

---

## Multi-Provider Transcription Strategy

### AssemblyAI
- **Industry-leading accuracy**: 95%+ accuracy on call center audio
- **Built-in compliance features**: PII redaction, sentiment analysis
- **Speaker diarization**: Automatic speaker identification
- **Auto chapters**: Segments conversation into topics
- **Entity detection**: Identifies names, numbers, dates
- **Real-time and batch**: Support for both processing modes
- **Confidence scores**: Word-level confidence metrics
- **Custom vocabulary**: Add domain-specific terms

### OpenAI GPT-4o-Transcribe
- **Latest model** with significantly improved Word Error Rate (WER)
- **Better accuracy** than original Whisper models
- **Detailed timestamps** at word and segment level
- **Response format**: Verbose JSON with confidence scores
- **File size limit**: 25MB per request
- **Supported formats**: MP3, MP4, MPEG, MPGA, M4A, WAV, WEBM
- **Language detection**: Automatic language identification

### GPT-5-Mini Reconciliation (2025-08-07)
- **Next-generation reasoning**: GPT-5 architecture with enhanced capabilities
- **Cost-effective**: Mini version optimized for efficiency
- **Superior context understanding**: Better at identifying contextual correctness
- **Enhanced accuracy**: Improved over GPT-4 models for reconciliation tasks
- **Structured outputs**: Advanced JSON mode for consistent formatting
- **Large context window**: Handles long transcripts efficiently
- **Fast inference**: Optimized for real-time processing
- **Batch processing**: Support for multiple segments simultaneously

### Intelligent Reconciliation Process
- **Discrepancy detection**: Identifies differences between AssemblyAI and OpenAI transcripts
- **Context-aware resolution**: Uses GPT-5-mini to determine most accurate version
- **Confidence weighting**: Considers both providers' confidence scores
- **Speaker preservation**: Maintains diarization from AssemblyAI
- **Compliance focus**: Ensures critical compliance phrases are accurate
- **Human review flags**: Marks low-confidence sections
- **Audit trail**: Keeps all provider outputs for analysis

---

## Queue-Based Processing System

### Job Queue Architecture
- **Redis backend** for high-performance queuing
- **Multiple queues**: Priority, normal, and failed job queues
- **Job persistence**: PostgreSQL for job state and history
- **Configurable workers**: Scale based on load
- **Timeout handling**: 30-minute default timeout per job

### Worker Pool Management
- **Parallel processing**: Multiple workers process jobs concurrently
- **CPU-based scaling**: Default workers = CPU count
- **Memory management**: Prevents memory leaks with job isolation
- **Error recovery**: Automatic retries with backoff
- **Health monitoring**: Worker status and performance metrics

### Processing Pipeline
1. File discovery creates job in queue
2. Worker claims job and updates status
3. Audio downloaded from S3
4. Parallel transcription with both providers
5. Reconciliation of results
6. Format optimization for output
7. Storage in S3 with metadata
8. Webhook notification sent
9. Job marked complete

---

## S3 Integration

### File Organization Structure
```
audio-bucket/
├── pending/           # New files to process
│   └── client_id/YYYY/MM/DD/filename.mp3
└── processed/         # Completed files
    └── client_id/YYYY/MM/DD/filename.mp3

transcript-bucket/
└── transcripts/
    └── client_id/YYYY/MM/DD/job_id/
        ├── formatted.md      # Final formatted transcript
        ├── reconciled.json   # Reconciliation result
        ├── google.json       # Raw Google output
        ├── openai.json       # Raw OpenAI output
        └── metadata.json     # Processing metadata
```

### File Discovery Process
- **Polling interval**: Configurable (default 60 seconds)
- **Batch processing**: Process multiple files per poll
- **Duplicate prevention**: Check if file already processed
- **Metadata extraction**: From file path and S3 tags
- **Auto-organization**: Move processed files automatically

---

## API Design

### Core Endpoints

**Health & Status**
- `GET /health` - Service health check
- `GET /status` - Overall service status and metrics

**Transcription Management**
- `POST /transcribe/submit` - Submit audio file for transcription
- `GET /transcribe/status/{job_id}` - Get job status
- `GET /transcribe/result/{job_id}` - Retrieve completed transcript
- `POST /transcribe/bulk-status` - Check multiple job statuses

**Webhook Management**
- `POST /webhooks/register` - Register webhook endpoint
- `DELETE /webhooks/{webhook_id}` - Remove webhook
- `GET /webhooks` - List registered webhooks

### Authentication
- **Service tokens**: JWT-based service-to-service auth
- **Header format**: `Authorization: Bearer <token>`
- **Token validation**: Middleware on all API routes
- **Excluded paths**: Health check and documentation

### Response Formats
- **Markdown**: Human-readable formatted transcript
- **JSON**: Structured data with segments and metadata
- **YAML**: Configuration-friendly format
- **SRT**: Subtitle format for video applications

---

## Database Schema

### Core Tables

**TranscriptionJob**
- Job tracking and status
- Audio file reference
- Processing timestamps
- Confidence scores
- Error handling fields

**TranscriptionMetrics**
- Provider performance metrics
- Processing times
- Confidence scores
- Cost tracking

**DiscrepancyLog**
- Reconciliation decisions
- Confidence deltas
- Review flags
- Resolution methods

**Webhook**
- Registered endpoints
- Event subscriptions
- Delivery status
- Retry tracking

**FileProcessingLog**
- File discovery audit
- Processing history
- Status tracking

---

## Docker Configuration

### Service Architecture
- **PostgreSQL**: Database for state management
- **Redis**: Queue backend for job processing
- **Transcription Service**: Main application container
- **Network isolation**: Services communicate via Docker network
- **Volume mounts**: Logs and configuration persistence

### Port Allocation
- **9100**: Main API port
- **9101**: Admin/monitoring UI port
- **5433**: PostgreSQL (avoiding conflicts)
- **6379**: Redis default port

### Environment Configuration
- Database connections
- AWS S3 credentials
- API keys for transcription services
- Service configuration parameters
- Development/production modes

---

## Environment Variables

### Required Configuration
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `AWS_ACCESS_KEY_ID` - S3 access
- `AWS_SECRET_ACCESS_KEY` - S3 secret
- `ASSEMBLYAI_API_KEY` - AssemblyAI API key
- `OPENAI_API_KEY` - For gpt-4o-transcribe and gpt-5-mini
- `SERVICE_AUTH_TOKEN` - Internal authentication

### Processing Configuration
- `POLL_INTERVAL` - File discovery interval (seconds)
- `WORKER_COUNT` - Number of parallel workers
- `MAX_RETRIES` - Retry attempts for failed jobs
- `JOB_TIMEOUT` - Maximum processing time
- `OPENAI_MODEL_TRANSCRIBE` - gpt-4o-transcribe
- `OPENAI_MODEL_REASONING` - gpt-5-mini-2025-08-07

---

## Project Structure

```
transcription-service/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .env
├── main.py
├── prisma/
│   └── schema.prisma
├── transcription/
│   ├── pipeline.py
│   ├── assemblyai_client.py
│   └── openai_client.py
├── reconciliation/
│   ├── reconciler.py
│   └── discrepancy_analyzer.py
├── formatting/
│   ├── formatter.py
│   └── templates/
├── queue/
│   ├── job_manager.py
│   └── redis_client.py
├── workers/
│   ├── transcription_worker.py
│   └── pool_manager.py
├── storage/
│   ├── s3_manager.py
│   └── file_discovery.py
├── services/
│   ├── webhook_service.py
│   └── metrics_service.py
├── middleware/
│   └── authentication.py
├── models/
│   ├── job.py
│   └── transcript.py
├── config/
│   └── settings.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
└── docs/
    ├── API.md
    ├── RECONCILIATION.md
    └── DEPLOYMENT.md
```

---

## Integration Points

### Output Storage
- Transcripts stored in S3 with structured paths
- Multiple formats available (Markdown, JSON, YAML)
- Metadata preserved for audit trail
- Signed URLs for secure access

### Webhook Notifications
- Event-driven notifications for job completion
- Configurable retry logic for failed deliveries
- Signature verification for security
- Support for multiple subscribers per event

### API Integration
- RESTful endpoints for job submission
- Bulk operations support
- Status polling for job tracking
- Direct transcript retrieval

---

## Development Workflow

### Initial Setup
1. Clone repository and configure environment
2. Set up AWS S3 buckets with proper structure
3. Configure API keys for transcription services
4. Initialize database with Prisma
5. Start Docker services

### Local Development
1. Start PostgreSQL and Redis containers
2. Run file discovery service
3. Start worker pool
4. Monitor logs for processing
5. Test with sample audio files

### Testing Strategy
- Unit tests for individual components
- Integration tests for provider APIs
- End-to-end tests with real audio
- Reconciliation accuracy validation
- Performance benchmarking

---