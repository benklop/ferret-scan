"""Application services (device backends decoupled from wx GUI)."""

__all__ = ['FerretRgbdService']


def __getattr__(name):
    if name == 'FerretRgbdService':
        from ferret_scan.services.ferret_rgbd import FerretRgbdService

        return FerretRgbdService
    raise AttributeError(name)
