"""Orchestration pipeline tying subsystems together."""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any

from emotions_ai.core.cognition.engine import HeuristicCognitiveEngine
from emotions_ai.core.common_sense.engine import HeuristicCommonSenseEngine
from emotions_ai.core.emotion_development.engine import DefaultEmotionDevelopmentEngine
from emotions_ai.core.emotion_regulation.engine import EmotionRegulationEngine
from emotions_ai.core.emotion_transformation.engine import DefaultTransformationEngine
from emotions_ai.core.emotional_resonance.engine import HeuristicResonanceEngine
from emotions_ai.core.response.expression import ResponseExpressionEngine
from emotions_ai.core.state.events import Experience
from emotions_ai.core.state.schema import StateCollection
from emotions_ai.core.temporal_evolution.engine import DefaultTemporalEvolutionEngine
from emotions_ai.memory.fusion.engine import MemoryFusionEngine
from emotions_ai.memory.manager import MemoryManager
from emotions_ai.runtime.adapters.base import ModelAdapter
from emotions_ai.runtime.sessions.manager import SessionManager


class ChatResult:
    def __init__(
        self,
        text: str,
        emotional_summary: dict[str, Any],
        guidance: dict[str, Any],
        state_collection: StateCollection,
        memories_used: list[dict[str, Any]],
        cognitive_summary: str = "",
    ) -> None:
        self.text = text
        self.emotional_summary = emotional_summary
        self.guidance = guidance
        self.state_collection = state_collection
        self.memories_used = memories_used
        self.cognitive_summary = cognitive_summary

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "emotional_summary": self.emotional_summary,
            "guidance": self.guidance,
            "cognitive_summary": self.cognitive_summary,
            "memories_used": self.memories_used,
        }


class Pipeline:
    def __init__(
        self,
        adapter: ModelAdapter,
        memory: MemoryManager,
        sessions: SessionManager,
        *,
        common_sense=None,
        cognition=None,
        resonance=None,
        development=None,
        transformation=None,
        temporal=None,
        regulation=None,
        expression=None,
    ) -> None:
        self.adapter = adapter
        self.memory = memory
        self.fusion = MemoryFusionEngine(memory)
        self.sessions = sessions
        self.common_sense = common_sense or HeuristicCommonSenseEngine()
        self.cognition = cognition or HeuristicCognitiveEngine()
        self.resonance = resonance or HeuristicResonanceEngine()
        self.development = development or DefaultEmotionDevelopmentEngine()
        self.transformation = transformation or DefaultTransformationEngine()
        self.temporal = temporal or DefaultTemporalEvolutionEngine()
        self.regulation = regulation or EmotionRegulationEngine()
        self.expression = expression or ResponseExpressionEngine()

    async def run(
        self,
        user_id: str,
        message: str,
        session_id: str = "default",
        context_id: str | None = None,
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> ChatResult:
        now = datetime.now(UTC)
        self.sessions.get_or_create(user_id, session_id)
        collection = self.sessions.load_state(user_id, session_id)

        # temporal update since last interaction
        self.temporal.apply_time(collection, now)

        # retrieve fused memories (LLM turns + emotional/experience)
        memories = self.fusion.retrieve_fused(user_id, message, session_id=None, top_k=5)
        mem_dicts = [{"memory_id": m.memory_id, "content": m.content, "type": m.memory_type} for m in memories]
        history = [{"role": "user", "content": m.content} for m in memories]  # lightweight

        # experience
        exp = Experience(
            user_id=user_id,
            session_id=session_id,
            context_id=context_id,
            content=message,
            source="user",
        )

        # common sense
        assessment = self.common_sense.assess(exp, history)
        # cognitive
        cognitive = self.cognition.process(exp, assessment, history, collection.states)
        # resonance
        resonance = self.resonance.resonate(exp, assessment, cognitive, history)

        # development
        self.development.develop(collection, exp, assessment, cognitive, resonance, mem_dicts, now=now)

        # transformation
        transitions = self.transformation.evaluate(collection, cognitive, {"message": message})
        self.transformation.apply(collection, transitions, now=now)

        # regulation
        self.regulation.regulate(collection, None)

        # expression guidance
        guidance = self.expression.guidance(collection)
        system_prompt = self.expression.build_system_prompt(guidance, collection.summary())

        # build messages for model
        messages = [{"role": "system", "content": system_prompt}]
        fused_context = self.fusion.build_context(memories)
        if fused_context:
            messages.append({"role": "system", "content": f"Fused memory context:\n{fused_context}"})
        messages.append({"role": "user", "content": message})

        # generate
        text = await self.adapter.generate(messages, temperature=temperature, max_tokens=max_tokens)

        # store LLM turns (fused memory)
        self.fusion.add_turn(user_id=user_id, session_id=session_id, role="user", content=message, importance=resonance.significance)
        self.fusion.add_turn(user_id=user_id, session_id=session_id, role="assistant", content=text, importance=0.3)
        # store emotional memory summary
        self.memory.add(
            user_id=user_id,
            session_id=session_id,
            content=f"Emotional state after message: {collection.summary()}",
            memory_type="emotional",
            importance=0.3,
        )

        # persist state
        self.sessions.save_state(collection, reason="chat")

        result = ChatResult(
            text=text,
            emotional_summary=collection.summary(),
            guidance=guidance,
            state_collection=collection,
            memories_used=mem_dicts,
            cognitive_summary=cognitive.summary,
        )
        return result

    async def run_stream(self, **kwargs) -> AsyncIterator[str]:
        # For simplicity, run then yield text in chunks
        result = await self.run(**kwargs)
        for chunk in result.text.split():
            yield chunk + " "