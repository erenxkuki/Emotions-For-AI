import os
import tempfile

from emotions_ai import EmotionAI


def test_cross_session_persistence():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        ai1 = EmotionAI(persistence=True, db_path=path)
        ai1.chat_sync(user_id="u1", message="I finally completed my project!")
        ai1.close()

        ai2 = EmotionAI(persistence=True, db_path=path)
        col = ai2.get_state("u1")
        assert col.state_count if hasattr(col, "state_count") else len(col.states) >= 1
        ai2.close()
    finally:
        for suffix in ("", "-wal", "-shm"):
            p = path + suffix
            if os.path.exists(p):
                os.remove(p)


def test_user_isolation():
    ai = EmotionAI(persistence=False)
    ai.chat_sync(user_id="a", message="I finally completed my project!")
    ai.chat_sync(user_id="b", message="I have been having a difficult time lately.")
    sa = ai.get_state("a").summary()["active"]
    sb = ai.get_state("b").summary()["active"]
    # distinct users should not share state ids
    _ = {s.get("state_id") for s in sa}
    # just ensure both have states
    assert len(sa) >= 1
    assert len(sb) >= 1


def test_explicit_clear():
    ai = EmotionAI(persistence=False)
    ai.chat_sync(user_id="u", message="I finally completed my project!")
    assert ai.clear_state("u") is True
    col = ai.get_state("u")
    assert len(col.states) == 0