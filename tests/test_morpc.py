import os
import subprocess

import pytest

import morpc


class FakeCompleted:
    def __init__(self):
        self.stdout = ""
        self.stderr = ""


def test_curl_builds_expected_command(monkeypatch, tmp_path):
    calls = {}

    def fake_run(cmd, **kwargs):
        calls['cmd'] = cmd
        calls['kwargs'] = kwargs
        return FakeCompleted()

    monkeypatch.setattr(subprocess, "run", fake_run)

    archive_dir = str(tmp_path / "input_data")
    morpc.curl("https://example.com/file.zip", archive_dir=archive_dir, verbose=False)

    expected_path = os.path.normpath(f'./{archive_dir}/file.zip')
    assert calls['cmd'] == ['curl', 'https://example.com/file.zip', '-o', expected_path]
    assert calls['kwargs']['shell'] is False
    assert calls['kwargs']['check'] is True


def test_curl_shell_passthrough(monkeypatch, tmp_path):
    calls = {}

    def fake_run(cmd, **kwargs):
        calls['kwargs'] = kwargs
        return FakeCompleted()

    monkeypatch.setattr(subprocess, "run", fake_run)

    morpc.curl("https://example.com/file.zip", archive_dir=str(tmp_path / "d"), shell=True, verbose=False)
    assert calls['kwargs']['shell'] is True


def test_curl_uses_basename_when_no_filename(monkeypatch, tmp_path):
    calls = {}

    def fake_run(cmd, **kwargs):
        calls['cmd'] = cmd
        return FakeCompleted()

    monkeypatch.setattr(subprocess, "run", fake_run)

    archive_dir = str(tmp_path / "d")
    morpc.curl("https://example.com/data/tiger.shp", archive_dir=archive_dir, verbose=False)
    assert calls['cmd'][-1] == os.path.normpath(f'./{archive_dir}/tiger.shp')


def test_curl_custom_filename(monkeypatch, tmp_path):
    calls = {}

    def fake_run(cmd, **kwargs):
        calls['cmd'] = cmd
        return FakeCompleted()

    monkeypatch.setattr(subprocess, "run", fake_run)

    archive_dir = str(tmp_path / "d")
    morpc.curl("https://example.com/file.zip", archive_dir=archive_dir, filename="renamed.zip", verbose=False)
    assert calls['cmd'][-1] == os.path.normpath(f'./{archive_dir}/renamed.zip')


def test_curl_creates_archive_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(subprocess, "run", lambda cmd, **kwargs: FakeCompleted())

    archive_dir = tmp_path / "newdir"
    assert not archive_dir.exists()
    morpc.curl("https://example.com/file.zip", archive_dir=str(archive_dir), verbose=False)
    assert archive_dir.exists()


def test_curl_return_filepath(monkeypatch, tmp_path):
    monkeypatch.setattr(subprocess, "run", lambda cmd, **kwargs: FakeCompleted())

    archive_dir = str(tmp_path / "d")
    result = morpc.curl(
        "https://example.com/file.zip",
        archive_dir=archive_dir,
        return_filepath=True,
        verbose=False,
    )
    assert result == os.path.normpath(f'./{archive_dir}/file.zip')


def test_curl_no_return_by_default(monkeypatch, tmp_path):
    monkeypatch.setattr(subprocess, "run", lambda cmd, **kwargs: FakeCompleted())

    result = morpc.curl("https://example.com/file.zip", archive_dir=str(tmp_path / "d"), verbose=False)
    assert result is None
