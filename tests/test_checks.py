from phase0.checks import base_checks
from phase0.models import RepoMeta


def test_base_checks_flags_missing_license_file():
    meta = RepoMeta(
        owner="o",
        repo="r",
        url="https://github.com/o/r",
        stars=10,
        forks=2,
        pushed_at="2026-01-01",
        license_spdx="MIT",
        default_branch="main",
        archived=False,
    )
    checks = base_checks(meta, file_license=None, file_name=None)
    names = {c.name for c in checks}
    assert "license_file" in names
    lic_check = next(c for c in checks if c.name == "license_file")
    assert lic_check.status == "fail"
