from emotions_ai.memory.fusion.engine import MemoryFusionEngine


def test_fusion_add_and_retrieve():
    f = MemoryFusionEngine()
    f.add_turn(user_id="u", session_id="s", role="user", content="I finished my project")
    f.add_turn(user_id="u", session_id="s", role="assistant", content="Great job!")
    recs = f.retrieve_fused(user_id="u", query="project", top_k=5)
    assert len(recs) >= 1
    ctx = f.build_context(recs)
    assert "project" in ctx.lower() or "Great job" in ctx


def test_fusion_dedup():
    f = MemoryFusionEngine()
    f.add_turn(user_id="u", session_id="s", role="user", content="hello")
    f.add_turn(user_id="u", session_id="s", role="user", content="hello")
    recs = f.retrieve_fused(user_id="u", query="hello", top_k=5)
    contents = [r.content for r in recs]
    assert len(contents) == len(set(contents))