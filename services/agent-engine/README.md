# Agent Engine Service

Universal agent orchestration platform built with Google ADK and FastAPI.

## Setup

### Prerequisites
- Python 3.9+
- Docker and Docker Compose
- Google Gemini API key

### Installation

1. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
- Copy `.env` file and update `GEMINI_API_KEY`
- Update other configuration as needed

### Running

#### Local Development
```bash
uvicorn src.main:app --reload --port 8001
```

#### Docker
```bash
docker-compose up
```

## API Endpoints

- `GET /health` - Health check endpoint

## Architecture

- FastAPI for REST API framework
- Google ADK for agent orchestration
- PostgreSQL for data persistence
- Redis for caching and queues