import yaml

from ocr_eval.plan import plan


def _repo(tmp_path, configs, reported=()):
    (tmp_path / "configs").mkdir()
    for name, ci in configs.items():
        body = {"name": name, "ci": ci, "model": {"type": "tesseract"}, "datasets": [{"name": "x"}]}
        (tmp_path / "configs" / f"{name}.yaml").write_text(yaml.safe_dump(body))
    for name in reported:
        (tmp_path / "reports" / name).mkdir(parents=True)
        (tmp_path / "reports" / name / "index.json").write_text("[]")
    return tmp_path


def names(sel):
    return [s["name"] for s in sel]


def test_first_run_launches_everything_that_is_ci(tmp_path):
    root = _repo(tmp_path, {"a": True, "b": True, "manual": False})
    assert names(plan(root, [])) == ["a", "b"]  # never reported; `ci: false` stays out


def test_only_the_touched_config_runs_once_reports_exist(tmp_path):
    root = _repo(tmp_path, {"a": True, "b": True}, reported=["a", "b"])
    assert plan(root, ["evaluation/README.md"]) == []
    sel = plan(root, ["evaluation/configs/b.yaml"])
    assert sel == [{"config": "configs/b.yaml", "name": "b", "extra": "tesseract"}]


def test_code_or_dependency_change_runs_all(tmp_path):
    root = _repo(tmp_path, {"a": True, "b": True}, reported=["a", "b"])
    for f in ("evaluation/src/ocr_eval/metrics.py", "evaluation/uv.lock"):
        assert names(plan(root, [f])) == ["a", "b"]


def test_new_config_runs_alone_next_to_reported_ones(tmp_path):
    root = _repo(tmp_path, {"a": True, "new": True}, reported=["a"])
    assert names(plan(root, ["evaluation/configs/new.yaml"])) == ["new"]


def test_run_all(tmp_path):
    root = _repo(tmp_path, {"a": True}, reported=["a"])
    assert names(plan(root, [], run_all=True)) == ["a"]
