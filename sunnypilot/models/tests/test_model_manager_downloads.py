import asyncio
import hashlib
from types import SimpleNamespace

import aiohttp
import pytest

from openpilot.sunnypilot.models import manager


GITLAB_RAW_URL = (
  "https://gitlab.com/sunnypilot/public/docs.sunnypilot.ai5/-/raw/main/"
  "models/recompiled14/model-North%20Nevada%20Model%20V2%20%28October%2008%2C%202025%29-101/"
  "driving_policy_nnmv2_metadata.pkl"
)
GITLAB_FALLBACK_URL = (
  "https://gitlab.com/api/v4/projects/sunnypilot%2Fpublic%2Fdocs.sunnypilot.ai5/repository/files/"
  "models%2Frecompiled14%2Fmodel-North%20Nevada%20Model%20V2%20%28October%2008%2C%202025%29-101%2F"
  "driving_policy_nnmv2_metadata.pkl/raw?ref=main"
)


class FakeContent:
  def __init__(self, chunks):
    self._chunks = chunks

  async def iter_chunked(self, _chunk_size):
    for chunk in self._chunks:
      yield chunk


class FakeResponse:
  def __init__(self, url, status, chunks=(), headers=None):
    self.url = url
    self.status = status
    self.content = FakeContent(chunks)
    self.headers = headers or {"content-length": str(sum(len(chunk) for chunk in chunks))}

  async def __aenter__(self):
    return self

  async def __aexit__(self, _exc_type, _exc, _tb):
    return False

  def raise_for_status(self):
    if self.status >= 400:
      raise aiohttp.ClientResponseError(
        request_info=SimpleNamespace(real_url=self.url),
        history=(),
        status=self.status,
        message="test failure",
        headers=self.headers,
      )


class FakeSession:
  def __init__(self, responses, seen_urls):
    self._responses = list(responses)
    self._seen_urls = seen_urls

  async def __aenter__(self):
    return self

  async def __aexit__(self, _exc_type, _exc, _tb):
    return False

  def get(self, url):
    self._seen_urls.append(url)
    assert self._responses, f"Unexpected download URL: {url}"
    return self._responses.pop(0)


def build_manager(download_index="1"):
  model_manager = manager.ModelManagerSP.__new__(manager.ModelManagerSP)
  model_manager._chunk_size = 128 * 1000
  model_manager._download_start_times = {}
  model_manager.params = SimpleNamespace(get=lambda _key: download_index)
  model_manager._calculate_eta = lambda _filename, _progress: 1
  model_manager._report_status = lambda: None
  return model_manager


def build_artifact(filename="model.pkl", url="https://example.com/model.pkl", content=b"model"):
  return SimpleNamespace(
    fileName=filename,
    downloadUri=SimpleNamespace(uri=url, sha256=hashlib.sha256(content).hexdigest()),
    downloadProgress=SimpleNamespace(status=None, progress=0, eta=0),
  )


def test_gitlab_raw_api_fallback_url_rewrites_encoded_path():
  assert manager.gitlab_raw_api_fallback_url(GITLAB_RAW_URL) == GITLAB_FALLBACK_URL


def test_gitlab_raw_api_fallback_url_ignores_non_gitlab_url():
  assert manager.gitlab_raw_api_fallback_url("https://example.com/models/model.pkl") is None


def test_download_file_uses_direct_url_when_successful(monkeypatch, tmp_path):
  url = "https://example.com/models/model.pkl"
  seen_urls = []
  content = b"direct model"
  monkeypatch.setattr(manager.aiohttp, "ClientSession", lambda: FakeSession([
    FakeResponse(url, 200, [content]),
  ], seen_urls))

  model_manager = build_manager()
  artifact = build_artifact(content=content)
  path = tmp_path / artifact.fileName

  asyncio.run(model_manager._download_file(url, str(path), artifact))

  assert seen_urls == [url]
  assert path.read_bytes() == content
  assert model_manager._download_start_times == {}


def test_download_file_retries_gitlab_api_raw_on_403(monkeypatch, tmp_path):
  seen_urls = []
  content = b"fallback model"
  monkeypatch.setattr(manager.aiohttp, "ClientSession", lambda: FakeSession([
    FakeResponse(GITLAB_RAW_URL, 403),
    FakeResponse(GITLAB_FALLBACK_URL, 200, [content]),
  ], seen_urls))

  model_manager = build_manager()
  artifact = build_artifact(url=GITLAB_RAW_URL, content=content)
  path = tmp_path / artifact.fileName

  asyncio.run(model_manager._download_file(GITLAB_RAW_URL, str(path), artifact))

  assert seen_urls == [GITLAB_RAW_URL, GITLAB_FALLBACK_URL]
  assert path.read_bytes() == content
  assert model_manager._download_start_times == {}


def test_process_artifact_marks_bundle_failed_when_gitlab_fallback_fails(monkeypatch, tmp_path):
  seen_urls = []
  monkeypatch.setattr(manager.aiohttp, "ClientSession", lambda: FakeSession([
    FakeResponse(GITLAB_RAW_URL, 403),
    FakeResponse(GITLAB_FALLBACK_URL, 500),
  ], seen_urls))

  model_manager = build_manager()
  model_manager.selected_bundle = SimpleNamespace(status=None)
  artifact = build_artifact(url=GITLAB_RAW_URL)

  with pytest.raises(aiohttp.ClientResponseError):
    asyncio.run(model_manager._process_artifact(artifact, str(tmp_path)))

  assert seen_urls == [GITLAB_RAW_URL, GITLAB_FALLBACK_URL]
  assert artifact.downloadProgress.status == manager.custom.ModelManagerSP.DownloadStatus.failed
  assert model_manager.selected_bundle.status == manager.custom.ModelManagerSP.DownloadStatus.failed


def test_process_artifact_aborts_when_download_index_is_cleared(monkeypatch, tmp_path):
  url = "https://example.com/models/model.pkl"
  seen_urls = []
  content = b"partial model"
  monkeypatch.setattr(manager.aiohttp, "ClientSession", lambda: FakeSession([
    FakeResponse(url, 200, [content]),
  ], seen_urls))

  model_manager = build_manager(download_index="")
  model_manager.selected_bundle = SimpleNamespace(status=None)
  artifact = build_artifact(url=url, content=content)

  with pytest.raises(Exception, match="Download cancelled"):
    asyncio.run(model_manager._process_artifact(artifact, str(tmp_path)))

  assert seen_urls == [url]
  assert not (tmp_path / artifact.fileName).exists()
  assert artifact.downloadProgress.status == manager.custom.ModelManagerSP.DownloadStatus.failed
  assert model_manager.selected_bundle.status == manager.custom.ModelManagerSP.DownloadStatus.failed
