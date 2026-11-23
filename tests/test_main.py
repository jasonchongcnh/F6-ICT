import pytest

from main import validate_python_version


@pytest.mark.parametrize("version", [(3, 11), (3, 12), (3, 13)])
def test_supported_python_versions(version):
    validate_python_version(version)


@pytest.mark.parametrize("version", [(3, 10), (3, 14), (4, 0)])
def test_unsupported_python_versions_have_clear_macos_help(version):
    with pytest.raises(SystemExit, match="setup_macos.command"):
        validate_python_version(version)

