# Persistence

Emotional persistence is mandatory. States do not auto-reset on new messages.

Policies: temporary, contextual, long_lasting, unresolved. Decay by policy
half-life adjusted by relevance. Cross-session via SQLite or in-memory cache.
Per-user isolation. User-controlled deletion and export. Sensitive data not retained
by default.