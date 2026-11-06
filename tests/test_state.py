import pytest

from emotions_ai.core.state.schema import PersistencePolicy, StateCollection, new_state


def test_state_creation_and_summary():
    col = StateCollection(user_id="u1", session_id="s1")
    st = new_state("curiosity", intensity=0.7, origin="test")
    col.add(st)
    assert len(col.states) == 1
    s = col.summary()
    assert s["state_count"] == 1
    assert s["active"][0]["emotion"] == "curiosity"


def test_multiple_states_coexist():
    col = StateCollection(user_id="u1", session_id="s1")
    col.add(new_state("happiness", intensity=0.6))
    col.add(new_state("concern", intensity=0.5))
    assert len(col.states) == 2
    assert {s.emotion for s in col.states} == {"happiness", "concern"}


def test_persistence_policy_enum():
    st = new_state("joy", persistence_policy=PersistencePolicy.LONG_LASTING)
    assert st.persistence_policy.value == "long_lasting"


def test_serialization_roundtrip():
    col = StateCollection(user_id="u1", session_id="s1")
    col.add(new_state("curiosity", intensity=0.72, valence=0.65, arousal=0.58))
    dumped = col.model_dump_json()
    restored = StateCollection.model_validate_json(dumped)
    assert restored.states[0].intensity == pytest.approx(0.72)