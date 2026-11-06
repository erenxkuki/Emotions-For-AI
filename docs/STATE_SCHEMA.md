# State Schema

See `emotions_ai/core/state/schema.py`.

`EmotionalState` fields: schema_version, state_id, emotion, intensity, valence,
arousal, confidence, relevance, uncertainty, origin, context_id, created_at,
updated_at, last_reinforced_at, persistence_policy, temporal_duration,
development_history, related_memory_ids, metadata.

`StateCollection` holds multiple states per user/session.

Serialization: JSON via Pydantic. Versioned. Import/export supported.