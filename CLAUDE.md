## Memory Bank System
- **Active context**: `/memory-bank/` - Living project documents
  - `context.md` - Session handoffs and current state
  - `architecture.md` - Technical patterns and decisions  
  - `progress.md` - Development status tracking
  - `decisions.md` - Key project decisions log
- **Archived docs**: `/memory-bank/archive/` - Completed plans

## IMPORTANT DIRECTIONS TO FOLLOW
- KISS: Keep implementations simple and straightforward
- Fail fast with clear error messages
- Local dev environment mirrors production
- Clean code over backwards compatibility (pre-launch)
- You are an LLM with a training cutoff before Google’s ADK was released, so you are not trained on it. Reference the documentation frequently and consistently. Do not make assumptions or guess how to use ADK without consulting the documentation: https://google.github.io/adk-docs/

## Google ADK Documentation
When encountering ADK-related issues, consult official documentation first:
- Main Docs: https://google.github.io/adk-docs/
- GitHub: https://github.com/google/adk-python
- API Reference: https://google.github.io/adk-docs/api-reference/python/