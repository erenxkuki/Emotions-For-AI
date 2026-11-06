import os
import tempfile

from emotions_ai.training.config import EmotionConfig
from emotions_ai.training.datasets.formats import (
    EmotionTrainingSample,
    load_jsonl,
    save_jsonl,
)
from emotions_ai.training.evaluation.tasks import ALL_TASKS, accuracy
from emotions_ai.training.objectives.emotion_state_prediction import (
    EmotionStatePredictionObjective,
)
from emotions_ai.training.objectives.memory_aware import MemoryAwareObjective


def test_emotion_config():
    c = EmotionConfig()
    assert c.emotional_reasoning is True
    assert c.num_emotions >= 1


def test_objective_compute():
    obj = EmotionStatePredictionObjective()
    preds = [[0.0, 1.0], [2.0, 0.0]]
    targets = [1, 0]
    loss = obj.compute(preds, targets)
    assert loss >= 0


def test_memory_aware():
    obj = MemoryAwareObjective()
    loss = obj.compute([0.5, 0.8], [1.0, 1.0])
    assert loss >= 0


def test_dataset_roundtrip():
    fd, path = tempfile.mkstemp(suffix=".jsonl")
    os.close(fd)
    try:
        samples = [EmotionTrainingSample(text="hi", target_emotions=["happiness"])]
        save_jsonl(samples, path)
        loaded = load_jsonl(path)
        assert len(loaded) == 1
        assert loaded[0].text == "hi"
    finally:
        os.remove(path)


def test_eval_accuracy():
    assert accuracy([1, 2, 3], [1, 2, 4]) == 2/3
    assert len(ALL_TASKS) >= 3


def test_torch_optional():
    from emotions_ai.training.modules.heads import torch_available
    # either True or False acceptable depending environment
    assert isinstance(torch_available(), bool)