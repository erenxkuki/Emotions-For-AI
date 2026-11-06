# Emotions for AI

An experimental, model-independent emotional intelligence framework for AI systems.

## Status

EFA Core 0.1 — shared emotional-state engine, persistence, temporal evolution,
transformation, common sense and emotional resonance interfaces, plus a runtime
attachment layer. Research-driven; not a claim of consciousness or subjective feeling.

## Install

```bash
pip install -e .
```

Optional extras:

```bash
pip install -e ".[api,http]"
```

## Quick start

```python
from emotions_ai import EmotionAI

ai = EmotionAI(persistence=True)
result = ai.chat_sync(user_id="user_001", message="I finally completed my project!")
print(result.text)
print(result.emotional_summary)
```

## Async / streaming

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

## Inspect state

```python
col = ai.get_state("user_001")
print(col.summary())
print(ai.state_history("user_001"))
```

## Run tests

```bash
pytest
```

## Run API

```bash
uvicorn emotions_ai.api.app:create_app --factory
```

## Philosophy

Emotions are not assigned to responses. They develop as evolving internal
computational states influenced by experiences, reasoning, memories,
interpretations and time. See `docs/`.

## License

MIT
```

Let me create docs files.<|end|><|start|>start<|channel|>analysis <|constrain|>xml<|message|><rfl:parameter name="command">
cd "C:\Users\Acer\Desktop\Emotions For AI"; echo done