from pipeline import config, main


def test_run_end_to_end(tmp_path, monkeypatch, raw_sample):
    monkeypatch.setattr(config, "DATABASE_URL", f"sqlite:///{tmp_path / 'e.db'}")
    monkeypatch.setattr(main, "extract", lambda blocks: raw_sample)
    main.run(weeks=1, export_dir=str(tmp_path / "out"))
    assert (tmp_path / "out" / "daily_mix.csv").exists()
    assert (tmp_path / "out" / "energy_hourly.csv").exists()
