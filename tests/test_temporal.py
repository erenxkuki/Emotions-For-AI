from datetime import UTC, datetime, timedelta

from emotions_ai.core.state.schema import PersistencePolicy, StateCollection, new_state
from emotions_ai.core.temporal_evolution.engine import DefaultTemporalEvolutionEngine


def test_time_decay_reduces_intensity():
    col = StateCollection(user_id="u", session_id="s")
    st = new_state("curiosity", intensity=0.8, persistence_policy=PersistencePolicy.CONTEXTUAL)
    col.add(st)
    now = datetime.now(UTC)
    col.updated_at = now - timedelta(hours=1)
    eng = DefaultTemporalEvolutionEngine()
    eng.apply_time(col, now)
    assert col.states[0].intensity < 0.8


def test_simulation_returns_timeline():
    col = StateCollection(user_id="u", session_id="s")
    col.add(new_state("happiness", intensity=0.6))
    eng = DefaultTemporalEvolutionEngine()
    tl = eng.simulate(col, duration_seconds=600, step_seconds=60)
    assert len(tl) > 1
    assert "t" in tl[0]
    assert "states" in tl[0]