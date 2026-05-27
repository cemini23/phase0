from phase0.github import normalize_license, parse_github_url


def test_parse_github_url():
    assert parse_github_url("https://github.com/foo/bar") == ("foo", "bar")
    assert parse_github_url("https://github.com/foo/bar.git") == ("foo", "bar")
    assert parse_github_url("https://example.com/x") is None


def test_normalize_license():
    assert normalize_license("MIT") == "MIT"
    assert normalize_license("NO LICENSE FOUND") == "NONE"
    assert normalize_license("Apache-2.0") == "Apache-2.0"
