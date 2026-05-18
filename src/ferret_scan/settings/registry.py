"""Plugin registry for settings domains."""

from typing import Callable, List

from ferret_scan.settings.schema import Settings

_registrars: List[Callable[[Settings], None]] = []


def register(registrar: Callable[[Settings], None]) -> None:
    _registrars.append(registrar)


def run_registered(settings: Settings) -> None:
    from ferret_scan.settings import ferret as ferret_settings

    ferret_settings.register_ferret_settings(settings)
    for fn in _registrars:
        fn(settings)


def clear() -> None:
    _registrars.clear()
