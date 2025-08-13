
## Development Philosophy
- KISS: Keep implementations simple and straightforward
- Fail fast with clear error messages
- Local dev environment mirrors production
- Clean code over backwards compatibility (pre-launch)

## Memory Bank System
- **Active context**: `/memory-bank/` - Contains living project documents
  - `context.md` - Session handoffs and current state
  - `architecture.md` - Technical patterns and decisions
  - `progress.md` - Development status tracking
  - `decisions.md` - Key project decisions log
- **Archived docs**: `/memory-bank/archive/` - Completed plans and trackers

- don't use timelines. this will be completed by Claude Code, an agentic coding tool and traditional project management conventions like timeline are irrelevant.

- If you encounter confusion or errors, consult the Google ADK documentation first. Avoid trial-and-error debugging, as it can lead you away from the correct use of Google ADK and cause downstream issues. 
**Documentation References**: 
- Main Docs: https://google.github.io/adk-docs/
- GitHub: https://github.com/google/adk-python
- API Reference: https://google.github.io/adk-docs/api-reference/python/