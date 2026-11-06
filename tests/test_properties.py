import random
from datetime import UTC, datetime, timedelta

from emotions_ai.core.emotion_regulation.engine import EmotionRegulationEngine
from emotions_ai.core.state.schema import PersistencePolicy, StateCollection, new_state
from emotions_ai.core.temporal_evolution.engine import DefaultTemporalEvolutionEngine


def test_state_values_bounded_random():
    rng = random.Random(42)
    col = StateCollection(user_id="u", session_id="s")
    for _ in range(50):
        st = new_state(
            rng.choice(["curiosity", "happiness", "concern", "frustration"]),
            intensity=rng.random(),
            valence=rng.uniform(-1, 1),
            arousal=rng.random(),
            confidence=rng.random(),
            relevance=rng.random(),
            uncertainty=rng.random(),
        )
        col.add(st)
    for s in col.states:
        assert 0.0 <= s.intensity <= 1.0
        assert -1.0 <= s.valence <= 1.0
        assert 0.0 <= s.arousal <= 1.0
        assert 0.0 <= s.confidence <= 1.0
        assert 0.0 <= s.relevance <= 1.0
        assert 0.0 <= s.uncertainty <= 1.0


def test_decay_never_increases_intensity():
    rng = random.Random(7)
    eng = DefaultTemporalEvolutionEngine()
    for _ in range(20):
        col = StateCollection(user_id="u", session_id="s")
        st = new_state("curiosity", intensity=rng.uniform(0.2, 1.0), persistence_policy=PersistencePolicy.CONTEXTUAL)
        col.add(st)
        before = col.states[0].intensity
        if col.updated_at.tzinfo is None:
            col.updated_at = col.updated_at.replace(tzinfo=UTC)
        col.updated_at = col.updated_at.astimezone(UTC) - timedelta(hours=1)
        eng.apply_time(col, datetime.now(UTC))
        assert col.states[0].intensity <= before + 1e-9


def test_regulation_caps_states():
    rng = random.Random(99)
    reg = EmotionRegulationEngine(max_states=5)
    col = StateCollection(user_id="u", session_id="s")
    for i in range(20):
        col.add(new_state(f"state_{i}", intensity=rng.random()))
    reg.regulate(col)
    assert len(col.states) <= 5
    for s in col.states:
        assert s.intensity <= 0.95 + 1e-9