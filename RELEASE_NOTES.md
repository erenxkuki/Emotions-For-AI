# Release Notes

## v0.1.0 — EFA Core 0.1 (First Public Release)

**Date:** 2026-11-06

### Highlights

- Model-independent emotional intelligence framework (Python 3.11+).
- Core state engine with multidimensional emotional states and flexible taxonomy.
- Mandatory emotional persistence across messages and sessions.
- Hybrid temporal evolution (event-driven + time-driven) with simulation.
- Emotion transformation, regulation, and response expression engines.
- Cognitive processing, common sense, and emotional resonance interfaces.
- Emotion memory system with SQLite/in-memory storage and privacy-aware policies.
- Runtime attachable framework: sync/async/streaming API, FastAPI REST + WebSocket,
  multi-user sessions, provider-agnostic adapters (echo, OpenAI-compatible).
- Research dashboard (`/dashboard`).
- Native training scaffolding (Phase 7): EmotionConfig, datasets, objectives,
  optional PyTorch heads, Transformers integration, evaluation tasks.
- Validation: 32 tests, property-based tests, benchmarks, install verifier.

### Validation

- `pytest` → 32 passed
- `ruff check` → all checks passed
- `scripts/verify_install.py` → OK
- Benchmarks: chat ~1400 ops/s, 24h simulation ~0.004s

### Known Limitations

- Heuristic engines are research baselines, not production-grade.
- No real trained model weights shipped (training scaffolding only).
- Dashboard is unauthenticated (development use).
- JavaScript/TypeScript SDK not yet implemented.

### License

MIT