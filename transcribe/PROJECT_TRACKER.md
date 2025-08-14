# Transcription Service - MVP Project Tracker

**Version**: 1.0 MVP  
**Status**: Active Development  
**Reference**: `/memory-bank/archive/masterplan.md`  
**Last Updated**: [Session Date]

---

## MVP Scope

Building a functional transcription service with production architecture but MVP hardening:
- Full multi-provider transcription (AssemblyAI + OpenAI gpt-4o-transcribe)
- GPT-5-mini reconciliation for accuracy
- Proper queue-based processing with Redis/Bull
- PostgreSQL with Prisma for data management
- S3 for file storage
- Basic API endpoints

**Core Principle**: Production architecture, MVP polish. Build it right, but don't over-engineer.

---

## Phase Status Overview

| Phase | Status | Sessions | Priority |
|-------|--------|----------|----------|
| **Phase 1**: Foundation | 🟡 In Progress | 2-3 | Critical |
| **Phase 2**: Queue System | ⬜ Not Started | 2 | Critical |
| **Phase 3**: Transcription Core | ⬜ Not Started | 3 | Critical |
| **Phase 4**: Reconciliation | ⬜ Not Started | 2 | Critical |
| **Phase 5**: API & Integration | ⬜ Not Started | 2 | Critical |

**Legend**: ✅ Complete | 🟡 In Progress | ⬜ Not Started

---

## Phase 1: Foundation & Infrastructure
*Establish the correct architecture from the start*

### Tasks:
- [ ] **1.1 Project Structure & Docker**
  - Full project structure per masterplan
  - Docker setup with PostgreSQL, Redis, main service
  - Prisma schema with all core tables
  - Environment configuration
  - **Output**: Complete development environment

- [ ] **1.2 Core Models & Database**
  - Prisma models (TranscriptionJob, TranscriptionMetrics, DiscrepancyLog, Webhook)
  - Database migrations
  - Basic model operations
  - S3 client setup
  - **Output**: Database ready with S3 integration

- [ ] **1.3 Configuration & File Discovery**
  - Settings management with pydantic
  - S3 file discovery service
  - Basic logging setup
  - Folder structure per masterplan
  - **Output**: Can discover and track S3 files

---

## Phase 2: Queue System
*Redis/Bull queue with workers - basic but solid*

### Tasks:
- [ ] **2.1 Queue Infrastructure**
  - Bull queue setup with Redis
  - Job model and persistence
  - Worker pool (2-4 workers)
  - Basic retry logic
  - **Output**: Functional job queue system

- [ ] **2.2 Job Processing Pipeline**
  - Job states (pending, processing, complete, failed)
  - Worker claiming mechanism
  - Error handling and retries
  - Status updates
  - **Output**: End-to-end job processing

---

## Phase 3: Transcription Core
*Both providers working with proper error handling*

### Tasks:
- [ ] **3.1 AssemblyAI Integration**
  - Client with error handling
  - Upload and transcription flow
  - Polling for results (no webhooks yet)
  - Speaker diarization extraction
  - **Output**: Complete AssemblyAI pipeline

- [ ] **3.2 OpenAI GPT-4o Integration**
  - OpenAI client setup
  - Audio preparation and chunking
  - Transcription with timestamps
  - Response parsing
  - **Output**: Complete OpenAI pipeline

- [ ] **3.3 Parallel Processing**
  - Orchestrate both providers
  - Handle partial failures
  - Store raw outputs in S3
  - Update job status
  - **Output**: Both providers run in parallel

---

## Phase 4: Intelligent Reconciliation
*GPT-5-mini reconciliation - the key differentiator*

### Tasks:
- [ ] **4.1 Discrepancy Detection**
  - Segment alignment
  - Difference identification
  - Confidence comparison
  - Format normalization
  - **Output**: Structured discrepancy data

- [ ] **4.2 GPT-5-Mini Reconciliation**
  - Reconciliation prompts
  - LLM integration
  - Decision parsing
  - Final transcript assembly
  - **Output**: Reconciled high-accuracy transcripts

---

## Phase 5: API & Storage
*Basic API and output management*

### Tasks:
- [ ] **5.1 Output & Storage**
  - Format transcripts (Markdown + JSON)
  - S3 storage with proper structure
  - Metadata persistence
  - Job completion handling
  - **Output**: Transcripts stored and accessible

- [ ] **5.2 Basic API**
  - FastAPI setup with auth
  - Submit transcription endpoint
  - Status checking endpoint
  - Retrieve transcript endpoint
  - Simple webhook notifications
  - **Output**: Functional API for integration

---

## Session Management

### Handoff Protocol
**End of session**: Update `/memory-bank/context.md` with:
- Task completed
- Key decisions made
- Next task to tackle
- Any blockers

**Start of session**: 
```bash
# Reference current task from tracker
"Continue with task X.X from the project tracker"
```

### Flexibility Points
- Combine small tasks if momentum is good
- Split complex tasks if needed
- Skip non-critical features for MVP
- Add hardening tasks after MVP works

### Key Decisions to Track
- [ ] Webhook implementation (polling vs webhooks for AssemblyAI)
- [ ] Error retry strategy (exponential backoff details)
- [ ] Reconciliation prompt optimization
- [ ] Queue concurrency settings

---

## Progress Tracking

### Current Focus
**Active Task**: 1.1 Project Structure & Docker  
**Phase Goal**: Foundation & Infrastructure  
**Next Target**: Get development environment running

### Completed Tasks
<!-- Update after each session -->
- [ ] Session 1: [Date] - [Tasks]
- [ ] Session 2: [Date] - [Tasks]

### MVP Success Criteria
- [ ] Can discover files from S3
- [ ] Processes files through queue
- [ ] Gets transcripts from both providers
- [ ] Reconciles with GPT-5-mini
- [ ] Stores results in S3
- [ ] Basic API works
- [ ] Handles errors gracefully

---

## Quick Start Commands

```bash
# For next session:
claude  # Start Claude Code
# "Let's work on task 1.1 - set up the complete project structure 
#  with Docker, Prisma, and the folder structure from the masterplan"

# After foundation is done:
docker-compose up  # Should start everything
npm run prisma:migrate  # Run migrations
python main.py  # Start the service
```

---

## What We're NOT Doing (Yet)
- Advanced monitoring/metrics
- Comprehensive webhook system  
- Multiple output formats beyond MD/JSON
- Admin UI
- Cost optimization
- Performance tuning
- Extensive error recovery
- Security hardening
- Rate limiting
- Caching layers

*These can be added after MVP proves the core concept*

---

*This tracker maintains architectural alignment with the full vision while focusing on getting a working system quickly.*