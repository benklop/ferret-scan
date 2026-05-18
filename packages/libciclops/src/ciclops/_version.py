from packaging.version import Version


def version_gt(left: str, right: str) -> bool:
    return Version(left) > Version(right)


def version_gte(left: str, right: str) -> bool:
    return Version(left) >= Version(right)
