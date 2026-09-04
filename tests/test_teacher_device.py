import pytest

from finevid_distill.models.teacher import QwenTeacher


def test_teacher_fails_fast_on_cpu_without_explicit_override() -> None:
    with pytest.raises(RuntimeError, match="requires an accelerator"):
        QwenTeacher(device="cpu")


def test_teacher_allows_explicit_small_cpu_diagnostic_without_loading_model() -> None:
    teacher = QwenTeacher(device="cpu", allow_cpu=True)

    assert teacher.device == "cpu"
    assert teacher._model is None
