from emotions_ai.core.cognition.engine import HeuristicCognitiveEngine
from emotions_ai.core.common_sense.engine import HeuristicCommonSenseEngine
from emotions_ai.core.emotional_resonance.engine import HeuristicResonanceEngine
from emotions_ai.core.state.events import Experience


def test_common_sense_assessment():
    cs = HeuristicCommonSenseEngine()
    exp = Experience(user_id="u", session_id="s", content="I finally completed my project!")
    a = cs.assess(exp, [])
    assert a.situation == "achievement_or_success"
    assert a.confidence > 0


def test_resonance_does_not_mirror_intensity():
    cs = HeuristicCommonSenseEngine()
    cog = HeuristicCognitiveEngine()
    res = HeuristicResonanceEngine()
    exp = Experience(user_id="u", session_id="s", content="I have been having a difficult time.")
    a = cs.assess(exp, [])
    c = cog.process(exp, a, [], [])
    r = res.resonate(exp, a, c, [])
    assert r.should_mirror_intensity is False
    assert "concern" in [next(iter(d.keys())) for d in r.suggested_internal_emotions]


def test_cognitive_contradiction():
    cs = HeuristicCommonSenseEngine()
    cog = HeuristicCognitiveEngine()
    exp1 = Experience(user_id="u", session_id="s", content="This is difficult.")
    a1 = cs.assess(exp1, [])
    cog.process(exp1, a1, [], [])
    exp2 = Experience(user_id="u", session_id="s", content="I completed it!")
    a2 = cs.assess(exp2, [])
    c2 = cog.process(exp2, a2, [{"content": "This is difficult."}], [])
    assert c2.interpretation_changed is True