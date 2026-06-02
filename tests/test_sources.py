import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from kurir.sources.url import UrlSource
from kurir.sources.file import FileSource
from kurir.sources.github import GithubSource, KNOWN_SOURCES


# --- UrlSource ---

def test_url_source_parses_lines():
    mock_resp = MagicMock()
    mock_resp.content = b"1.1.1.1:80\n2.2.2.2:8080\n"
    mock_resp.raise_for_status = MagicMock()

    with patch("kurir.sources.url.requests.get", return_value=mock_resp):
        result = UrlSource("http://example.com/proxies.txt").fetch()

    assert result == ["1.1.1.1:80", "2.2.2.2:8080"]


def test_url_source_skips_blank_lines():
    mock_resp = MagicMock()
    mock_resp.content = b"1.1.1.1:80\n\n\n2.2.2.2:8080\n"
    mock_resp.raise_for_status = MagicMock()

    with patch("kurir.sources.url.requests.get", return_value=mock_resp):
        result = UrlSource("http://example.com").fetch()

    assert result == ["1.1.1.1:80", "2.2.2.2:8080"]


def test_url_source_handles_invalid_utf8():
    mock_resp = MagicMock()
    mock_resp.content = b"1.1.1.1:80\n\xff\xfe\n2.2.2.2:80\n"
    mock_resp.raise_for_status = MagicMock()

    with patch("kurir.sources.url.requests.get", return_value=mock_resp):
        result = UrlSource("http://example.com").fetch()

    assert "1.1.1.1:80" in result
    assert "2.2.2.2:80" in result


# --- FileSource ---

def test_file_source_reads_lines(tmp_path: Path):
    f = tmp_path / "proxies.txt"
    f.write_text("1.1.1.1:80\n2.2.2.2:8080\n")
    result = FileSource(f).fetch()
    assert result == ["1.1.1.1:80", "2.2.2.2:8080"]


def test_file_source_skips_blank_lines(tmp_path: Path):
    f = tmp_path / "proxies.txt"
    f.write_text("1.1.1.1:80\n\n2.2.2.2:8080\n")
    result = FileSource(f).fetch()
    assert result == ["1.1.1.1:80", "2.2.2.2:8080"]


def test_file_source_missing_file_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        FileSource(tmp_path / "nonexistent.txt").fetch()


# --- GithubSource ---

def test_github_source_known_name_resolves():
    mock_resp = MagicMock()
    mock_resp.content = b"1.1.1.1:80\n"
    mock_resp.raise_for_status = MagicMock()

    with patch("kurir.sources.url.requests.get", return_value=mock_resp):
        result = GithubSource("thesspeedx_http").fetch()

    assert result == ["1.1.1.1:80"]


def test_github_source_unknown_name_raises():
    with pytest.raises(ValueError, match="Unknown source"):
        GithubSource("does_not_exist")


def test_github_source_available_sources_returns_all():
    sources = GithubSource.available_sources()
    assert set(sources) == set(KNOWN_SOURCES)
