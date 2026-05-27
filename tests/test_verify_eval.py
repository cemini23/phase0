from pathlib import Path

from phase0.license_file import detect_license_in_text, read_license_file
from phase0.verify_eval import compare_licenses, extract_eval_entries

FIXTURES = Path(__file__).parent / "fixtures"


def test_extract_eval_entries():
    text = (FIXTURES / "sample_eval.md").read_text(encoding="utf-8")
    entries = extract_eval_entries(text)
    urls = {e.repo for e in entries}
    assert "Hello-World" in urls
    assert "Spoon-Knife" in urls
    assert "gitignore" in urls


def test_compare_licenses_match():
    status, _ = compare_licenses("MIT", "MIT", "MIT")
    assert status == "match"


def test_compare_licenses_false_negative():
    status, detail = compare_licenses("NO LICENSE FOUND", "MIT", "MIT")
    assert status == "mismatch"
    assert "no license" in detail.lower()


def test_read_license_file():
    lic, name = read_license_file(FIXTURES / "repo_mit")
    assert name == "LICENSE"
    assert lic == "MIT"


def test_detect_spdx_line():
    text = "SPDX-License-Identifier: Apache-2.0\n"
    assert detect_license_in_text(text) == "Apache-2.0"
