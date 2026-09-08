import pytest

from scripts.bump_version import bump_version
from scripts.check_version import SEMVER, read_version


def test_project_version_is_semver() -> None:
    project_version = read_version()

    assert SEMVER.fullmatch(project_version)


@pytest.mark.parametrize(
    ("part", "expected"),
    [("patch", "1.2.4"), ("minor", "1.3.0"), ("major", "2.0.0")],
)
def test_bump_version_updates_requested_part(part: str, expected: str) -> None:
    content, version = bump_version('version = "1.2.3"\n', part)

    assert version == expected
    assert content == f'version = "{expected}"\n'


def test_bump_version_rejects_unknown_part() -> None:
    with pytest.raises(ValueError, match="Unsupported version part"):
        bump_version('version = "1.2.3"\n', "unknown")
