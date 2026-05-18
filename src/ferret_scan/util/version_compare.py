"""OpenCV version comparisons (replaces distutils.version.LooseVersion)."""

from packaging.version import Version


def parse_version(version_str: str) -> Version:
    return Version(version_str)


def version_gt(left: str, right: str) -> bool:
    return Version(left) > Version(right)


def version_gte(left: str, right: str) -> bool:
    return Version(left) >= Version(right)
