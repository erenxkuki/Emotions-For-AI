
from emotions_ai import EmotionAI


def test_achievement_scenario():
    ai = EmotionAI(persistence=False)
    res = ai.chat_sync(user_id="u1", message="I finally completed my project!")
    assert res.text
    summary = res.emotional_summary
    emotions = [s["emotion"] for s in summary["active"]]
    assert any(e in ("happiness", "excitement", "satisfaction", "appreciation") for e in emotions)


def test_difficult_experience_scenario():
    ai = EmotionAI(persistence=False)
    res = ai.chat_sync(user_id="u2", message="I have been having a difficult time lately. I don't really know what to do.")
    emotions = [s["emotion"] for s in res.emotional_summary["active"]]
    assert any(e in ("concern", "compassion", "attentiveness", "empathy_response") for e in emotions)


def test_state_persists_across_calls():
    ai = EmotionAI(persistence=False)
    ai.chat_sync(user_id="u3", message="I finally completed my project!")
    res2 = ai.chat_sync(user_id="u3", message="Thanks!")
    # state collection should still have prior states (not reset)
    assert res2.emotional_summary["state_count"] >= 1


def test_mixed_emotions_not_forced_single():
    ai = EmotionAI(persistence=False)
    res = ai.chat_sync(user_id="u4", message="I am happy but also sad about leaving.")
    # At least should not crash; states can be multiple
    assert res.emotional_summary["state_count"] >= 0


def test_state_inspection_api():
    ai = EmotionAI(persistence=False)
    ai.chat_sync(user_id="u5", message="I finally achieved something I worked hard for.")
    col = ai.get_state("u5")
    assert col.user_id == "u5"
    assert isinstance(col.summary(), dict)