"""Smoke and unit tests. Run with: python -m pytest"""
import os
import sys

import pandas as pd
from streamlit.testing.v1 import AppTest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
APP = os.path.join(ROOT, "project1.py")


def test_app_renders_all_tabs(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    at = AppTest.from_file(APP).run(timeout=30)
    assert not at.exception
    assert at.title[0].value == "Usability Testing Tool"
    labels = [t.label for t in at.tabs]
    assert labels == ["Home", "Consent", "Demographics", "Task", "Exit Questionnaire", "Report"]


def test_consent_requires_checkbox(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    at = AppTest.from_file(APP).run(timeout=30)
    submit = next(b for b in at.button if b.label == "Submit Consent")
    submit.click().run(timeout=30)
    assert any("must agree" in w.value for w in at.warning)
    assert not (tmp_path / "data" / "consent_data.csv").exists()


def test_save_and_load_csv_round_trip(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    import project1

    path = tmp_path / "rows.csv"
    project1.save_to_csv({"a": 1, "b": "x"}, str(path))
    project1.save_to_csv({"a": 2, "b": "y"}, str(path))
    df = project1.load_from_csv(str(path))
    assert list(df.columns) == ["a", "b"]
    assert df["a"].tolist() == [1, 2]
    # header is written once, not on every append
    assert path.read_text().count("a,b") == 1


def test_load_missing_csv_returns_empty(tmp_path):
    import project1

    assert project1.load_from_csv(str(tmp_path / "missing.csv")).equals(pd.DataFrame())
