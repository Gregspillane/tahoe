- don't use timelines. this will be completed by Claude Code, an agentic coding tool and traditional project management conventions like timeline are irrelevant.

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