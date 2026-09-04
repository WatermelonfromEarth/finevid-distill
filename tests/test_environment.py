from finevid_distill.environment import build_report, resolve_device


def test_explicit_device_is_preserved() -> None:
    assert resolve_device("cpu") == "cpu"


def test_environment_report_contains_device_and_versions(monkeypatch) -> None:
    monkeypatch.setattr(
        "finevid_distill.environment.package_versions",
        lambda: {"torch": "test-version"},
    )
    report = build_report({"runtime": {"device": "cpu"}})

    assert "Configured device: cpu" in report
    assert "Resolved device: cpu" in report
    assert "Package versions:" in report
    assert "torch: test-version" in report
