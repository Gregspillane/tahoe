from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()
load_dotenv(f"config/{os.getenv('ENVIRONMENT', 'development')}.env")

app = FastAPI(
    title="Agent Engine",
    description="Universal agent orchestration platform",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "agent-engine"}