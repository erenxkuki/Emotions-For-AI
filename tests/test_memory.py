from emotions_ai.memory.manager import MemoryManager


def test_memory_add_and_retrieve():
    mm = MemoryManager()
    mm.add(user_id="u", content="completed project", memory_type="experience", importance=0.8)
    res = mm.retrieve(user_id="u", query="project")
    assert len(res) >= 1


def test_sensitive_not_retained_by_default():
    mm = MemoryManager()
    rec = mm.add(user_id="u", content="my password is 1234", memory_type="experience")
    # sensitive -> expires immediately, should_retain false -> None
    assert rec is None


def test_user_isolation_memory():
    mm = MemoryManager()
    mm.add(user_id="a", content="hello from a")
    mm.add(user_id="b", content="hello from b")
    assert all(r.user_id == "a" for r in mm.retrieve(user_id="a", query="hello"))
    assert mm.retrieve(user_id="a", query="hello")[0].content == "hello from a"


def test_delete_user_memory():
    mm = MemoryManager()
    mm.add(user_id="u", content="hello")
    n = mm.delete_user("u")
    assert n >= 1
    assert mm.retrieve(user_id="u", query="hello") == []