import pytest

import main
from config import load_config


def test_deploy_does_not_dispatch_parent_repository_workflow(tmp_path, monkeypatch):
    config = load_config(tmp_path / "firstread")
    (config.root.parent / ".github" / "workflows").mkdir(parents=True)
    (config.root.parent / ".github" / "workflows" / "daily.yml").write_text(
        "name: unrelated workflow\n", encoding="utf-8"
    )
    monkeypatch.setattr(main.shutil, "which", lambda _name: "gh")
    monkeypatch.setattr(
        main.subprocess,
        "run",
        lambda *args, **kwargs: pytest.fail("The parent repository workflow was dispatched."),
    )

    with pytest.raises(FileNotFoundError, match=".github"):
        main._deploy(config)
