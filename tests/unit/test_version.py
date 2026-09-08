from scripts.check_version import SEMVER, read_versions


def test_release_versions_are_synchronized_semver() -> None:
    project_version, manifest_version = read_versions()

    assert project_version == manifest_version
    assert SEMVER.fullmatch(project_version)
