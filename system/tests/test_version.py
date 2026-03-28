import sys
import types
import unittest
from pathlib import Path


def bootstrap_openpilot_shims() -> None:
  repo_root = Path(__file__).resolve().parents[2]
  openpilot_root = repo_root / "openpilot"

  openpilot_pkg = sys.modules.get("openpilot")
  if openpilot_pkg is None:
    openpilot_pkg = types.ModuleType("openpilot")
    openpilot_pkg.__path__ = [str(openpilot_root)]
    sys.modules["openpilot"] = openpilot_pkg

  for package_name in ("common", "system", "selfdrive", "sunnypilot", "third_party", "tools"):
    shim_path = openpilot_root / package_name
    if not shim_path.is_file():
      continue

    target_path = (openpilot_root / shim_path.read_text().strip()).resolve()
    package = types.ModuleType(f"openpilot.{package_name}")
    package.__path__ = [str(target_path)]
    sys.modules[f"openpilot.{package_name}"] = package

  basedir_module = types.ModuleType("openpilot.common.basedir")
  basedir_module.BASEDIR = str(repo_root)
  sys.modules["openpilot.common.basedir"] = basedir_module

  swaglog_module = types.ModuleType("openpilot.common.swaglog")

  class CloudlogStub:
    def exception(self, *_args, **_kwargs):
      pass

  swaglog_module.cloudlog = CloudlogStub()
  sys.modules["openpilot.common.swaglog"] = swaglog_module

  git_module = types.ModuleType("openpilot.common.git")
  git_module.get_commit = lambda *_args, **_kwargs: "unknown"
  git_module.get_origin = lambda *_args, **_kwargs: "https://github.com/MostlyClueless94/openpilot.git"
  git_module.get_branch = lambda *_args, **_kwargs: "MostlyClueless"
  git_module.get_short_branch = lambda *_args, **_kwargs: "MostlyClueless"
  git_module.get_commit_date = lambda *_args, **_kwargs: "now"
  sys.modules["openpilot.common.git"] = git_module


try:
  from openpilot.system.version import build_metadata_from_dict
except ModuleNotFoundError:
  bootstrap_openpilot_shims()
  from openpilot.system.version import build_metadata_from_dict


def make_build_metadata(channel: str):
  return build_metadata_from_dict({
    "channel": channel,
    "openpilot": {
      "version": "1.0.0",
      "release_notes": "notes",
      "git_commit": "abc123",
      "git_origin": "https://github.com/MostlyClueless94/openpilot.git",
      "git_commit_date": "now",
      "build_style": "test",
    },
  })


class TestVersionMetadata(unittest.TestCase):
  def test_subipilot_branch_roles(self):
    development = make_build_metadata("MostlyClueless")
    self.assertTrue(development.development_channel)
    self.assertFalse(development.tested_channel)
    self.assertFalse(development.release_channel)
    self.assertEqual(development.channel_type, "development")

    staging = make_build_metadata("subi-staging")
    self.assertFalse(staging.development_channel)
    self.assertTrue(staging.tested_channel)
    self.assertFalse(staging.release_channel)
    self.assertEqual(staging.channel_type, "staging")

    release = make_build_metadata("subi-1.0")
    self.assertFalse(release.development_channel)
    self.assertTrue(release.tested_channel)
    self.assertTrue(release.release_channel)
    self.assertEqual(release.channel_type, "release")

  def test_tici_compatible_subipilot_branches(self):
    for channel in ("MostlyClueless", "subi-staging", "subi-1.0", "release-tici"):
      with self.subTest(channel=channel):
        self.assertTrue(make_build_metadata(channel).tici_compatible_channel)

    for channel in ("feature-branch", "release-mici", "nightly"):
      with self.subTest(channel=channel):
        self.assertFalse(make_build_metadata(channel).tici_compatible_channel)


if __name__ == "__main__":
  unittest.main()
