# Emotions for AI

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-32%20passing-brightgreen.svg)](#validation)
[![Status](https://img.shields.io/badge/status-EFA%20Core%200.1-orange.svg)](#roadmap)

> **An experimental, model-independent emotional intelligence framework for AI systems.**
>
> Emotions should not simply be assigned to AI responses. They should develop as evolving internal computational states influenced by experiences, reasoning, memories, interpretations, and time.

---

## Table of Contents

- [Overview](#overview)
- [Core Philosophy](#core-philosophy)
- [Architecture](#architecture)
- [Integration Versions](#integration-versions)
- [Quick Start](#quick-start)
- [Public API](#public-api)
- [Research Dashboard](#research-dashboard)
- [Validation](#validation)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**Emotions for AI** is an open-source research and engineering framework that
investigates whether computational emotional states can *emerge* from continuous
cognitive processing, accumulated experiences, contextual interpretation, and
temporal development — rather than being manually assigned to every response.

It is **not** a chatbot, a personality generator, a prompt-template collection,
or a sentiment-analysis wrapper. It is a serious, long-term research project
with defined subsystems, documented interfaces, testable behavior, and clear
integration contracts.

The framework is **model-independent**: it works with local models, cloud APIs,
open-weight models, and custom inference servers through a provider-agnostic
adapter interface.

## Core Philosophy

Human emotions are not labels attached to sentences. They are influenced by
experiences, interpretations, memories, expectations, goals, discoveries,
uncertainty, and the passage of time.

This project applies that idea computationally:

```
Experience → Questioning → Exploration → Connection → Realization → Emotional-state update
```

A moment of realization is not necessarily the beginning of an emotion — it may
simply be when its significance becomes recognizable.

### Research Hypothesis

> Computational emotional states can emerge from continuous cognitive processing,
> accumulated experiences, contextual interpretation, and temporal development
> instead of being manually assigned to every response.

This is a **hypothesis, not an established conclusion**. The software makes no
claim of consciousness, sentience, or subjective feeling. It distinguishes
between:

- Computational emotional representations
- Emotion-related cognitive processing
- Emotionally informed behavior
- Subjective conscious experience (which this project cannot establish)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    EmotionAI (Facade)                       │
├─────────────────────────────────────────────────────────────┤
│  Runtime Layer: adapters · sessions · orchestration · API   │
├─────────────────────────────────────────────────────────────┤
│  Core Engines                                               │
│  ├── Emotion Development Engine (EDE)                      │
│  ├── Emotional Persistence Engine                          │
│  ├── Temporal Evolution Engine (TEE)                        │
│  ├── Emotional Resonance Engine (ERE)                       │
│  ├── Cognitive Processing Engine (CPE)                      │
│  ├── Common Sense Engine (CSE)                             │
│  ├── Emotion Transformation Engine                          │
│  ├── Emotion Regulation Engine                             │
│  └── Response Expression Engine                             │
├─────────────────────────────────────────────────────────────┤
│  Memory System (EMS): experience · emotional · contextual  │
├─────────────────────────────────────────────────────────────┤
│  State Layer: versioned schemas · persistence · history     │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Principles

- **Model independence** — the core engine has no LLM dependency.
- **Multi-state** — multiple emotional states coexist; no forced single label.
- **Persistence** — states survive across messages and sessions (mandatory feature).
- **Temporal evolution** — hybrid event-driven + time-driven updates.
- **Interpretability** — every transition has auditable metadata.
- **Safety first** — emotional state never overrides safety, privacy, or factual accuracy.

## Integration Versions

### Version A — Runtime / Attachable Framework

Attaches to an existing model without retraining. Works with OpenAI-compatible
endpoints, Hugging Face, Ollama, and custom HTTP servers.

### Version B — Native / Training Integration

For developers creating or fine-tuning models. Provides emotion-aware training
objectives, model heads, dataset formats, and evaluation tasks (PyTorch +
Hugging Face Transformers, optional).

Both versions share state schemas, emotion identifiers, transition definitions,
memory formats, event definitions, and configuration standards.

## Quick Start

### Install

```bash
pip install -e .
```

Optional extras:

```bash
pip install -e ".[api,http]"
```

### Basic Usage

```python
from emotions_ai import EmotionAI

ai = EmotionAI(persistence=True)

result = ai.chat_sync(
    user_id="user_001",
    message="I finally completed my project!"
)

print(result.text)
print(result.emotional_summary)
```

### Async & Streaming

```python
import asyncio

async def main():
    ai = EmotionAI()
    result = await ai.chat(user_id="u", message="hello")
    print(result.text)

    async for chunk in ai.chat_stream(user_id="u", message="tell me more"):
        print(chunk, end="")

asyncio.run(main())
```

### Inspect State

```python
col = ai.get_state("user_001")
print(col.summary())
print(ai.state_history("user_001"))
```

## Public API

| Method | Description |
|---|---|
| `chat(user_id, message, ...)` | Async chat |
| `chat_sync(user_id, message, ...)` | Synchronous chat |
| `chat_stream(user_id, message, ...)` | Streaming response |
| `get_state(user_id, session_id)` | Inspect state collection |
| `state_history(user_id, session_id)` | Development history |
| `clear_state(user_id, session_id)` | Explicit state clearing |
| `delete_user_memory(user_id)` | Delete user memory |
| `export_state(user_id, session_id)` | Export state as JSON |
| `simulate_time(user_id, ...)` | Temporal simulation |

### REST API

```bash
uvicorn emotions_ai.api.app:create_app --factory
```

Endpoints: `/health`, `/chat`, `/state/{user_id}`, `/state/{user_id}/history`,
`/state/{user_id}/timeline`, `/simulate`, `/dashboard`, `/memory/{user_id}`, `/ws`.

## Research Dashboard

A built-in research dashboard is available at `/dashboard` when running the API
server. It provides:

- Current active states
- State timeline (simulation)
- Development history
- Engine diagnostics
- Temporal simulation controls

## Validation

```bash
pytest                    # 32 tests
python scripts/verify_install.py
python scripts/benchmark.py
```

Test coverage includes state representation, temporal decay, emotion development,
persistence, memory, common sense, resonance, cognitive processing, API, training,
and property-based randomized tests.

## Project Structure

```
emotions-for-ai/
├── emotions_ai/
│   ├── core/          # shared state + engines (no LLM dependency)
│   ├── memory/        # storage, retrieval, policy
│   ├── runtime/       # adapters, sessions, orchestration, facade
│   ├── training/      # native training integration (Phase 7)
│   ├── api/           # FastAPI app + dashboard
│   ├── simulation/    # temporal simulation tools
│   ├── evaluation/    # benchmarks and tasks
│   └── plugins/       # extensibility
├── tests/
├── docs/
├── scripts/
├── examples/
├── pyproject.toml
├── README.md
├── LICENSE
└── DEVELOPMENT_STATUS.md
```

## Documentation

| Document | Description |
|---|---|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture and data flow |
| [RESEARCH_FOUNDATIONS.md](docs/RESEARCH_FOUNDATIONS.md) | Core research hypothesis |
| [EMOTION_MODEL.md](docs/EMOTION_MODEL.md) | Multidimensional emotion model |
| [STATE_SCHEMA.md](docs/STATE_SCHEMA.md) | State representation specification |
| [PERSISTENCE.md](docs/PERSISTENCE.md) | Persistence policies |
| [TEMPORAL_ENGINE.md](docs/TEMPORAL_ENGINE.md) | Temporal evolution |
| [COMMON_SENSE.md](docs/COMMON_SENSE.md) | Common sense engine |
| [EMOTIONAL_RESONANCE.md](docs/EMOTIONAL_RESONANCE.md) | Resonance engine |
| [RUNTIME_INTEGRATION.md](docs/RUNTIME_INTEGRATION.md) | Runtime attachment |
| [API_REFERENCE.md](docs/API_REFERENCE.md) | API reference |
| [SECURITY.md](docs/SECURITY.md) | Security and ethics |
| [SECURITY_AUDIT.md](docs/SECURITY_AUDIT.md) | Security audit checklist |
| [ROADMAP.md](docs/ROADMAP.md) | Development roadmap |
| [CONTRIBUTING.md](docs/CONTRIBUTING.md) | Contribution guide |
| [DEVELOPMENT_STATUS.md](DEVELOPMENT_STATUS.md) | Current development status |

## Roadmap

| Phase | Status |
|---|---|
| 0 — Research and specification | ✅ Complete |
| 1 — Core state engine | ✅ Complete |
| 2 — Emotional persistence | ✅ Complete |
| 3 — Temporal evolution | ✅ Complete |
| 4 — Cognitive and common-sense | ✅ Basic |
| 5 — Emotional resonance | ✅ Basic |
| 6 — Runtime integration | ✅ Complete |
| 7 — Native training integration | 🔧 Scaffolding |
| 8 — Dashboard and research tools | ✅ Basic |
| 9 — Validation and release | 🔧 In progress |

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) and
[docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) before submitting pull requests.

## Ethics

Emotional states in this framework are **computational representations**, not
proof of feelings. The system is designed to help people, not manipulate them:

- No intentional emotional dependency
- No exploitation of vulnerable users
- No covert persuasion
- No fabricated personal experiences
- No claims of suffering or consciousness
- Emotional state never overrides safety, privacy, or factual accuracy

## License

This project is licensed under the [MIT License](LICENSE).

---

**Project: Emotions for AI**

> *"Do not simply assign an emotion to an AI response. Build the internal
> computational processes through which an emotional state can develop,
> persist, evolve and influence behavior."*