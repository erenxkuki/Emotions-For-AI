# Security Audit (Phase 9)

Checklist:
- No hardcoded secrets; credentials via env vars.
- Per-user isolation in memory and state stores.
- User-controlled deletion and export.
- Sensitive data not retained by default.
- Emotional states never override safety, privacy, or factual accuracy.
- Plugins cannot silently access other users' memory (interface boundary).
- Input validation via Pydantic.
- No arbitrary code execution in core.

Known limitations: heuristic engines not adversarially robust; dashboard unauthenticated (dev only).