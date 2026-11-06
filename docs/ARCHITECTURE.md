# Architecture

Emotions for AI is model-independent. Core engine develops, persists and evolves
computational emotional states. Runtime layer attaches to any model via adapters.

## Major subsystems

- Emotion Development Engine (EDE)
- Emotional Persistence Engine
- Temporal Evolution Engine (TEE)
- Emotional Resonance Engine (ERE)
- Cognitive Processing Engine (CPE)
- Common Sense Engine (CSE)
- Emotion Memory System (EMS)
- Emotion Transformation Engine
- Emotion Regulation Engine
- Response Expression Engine

## Boundaries

- `core/`: shared state, engines, no model dependency.
- `memory/`: storage, retrieval, policy.
- `runtime/`: adapters, sessions, orchestration, facade.
- `training/`: native integration (experimental, future).
- `api/`, `simulation/`, `evaluation/`.

## Data flow (chat)

1. Load state collection (in-memory + optional DB).
2. Apply temporal decay.
3. Retrieve memories.
4. Common sense assessment.
5. Cognitive processing.
6. Emotional resonance.
7. State development.
8. Transformation.
9. Regulation.
10. Expression guidance.
11. Model generation.
12. Store memory + persist state.

## Compatibility

State schemas are versioned (`schema_version`) and shared between runtime and native.