"""Abstract scanner and turntable backend interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List

from ferret_scan.hardware.types import DeviceCapabilities, PreferenceField

if TYPE_CHECKING:
    from ferret_scan.settings.schema import Settings


class ScannerBackend(ABC):
    id: str
    label: str

    @abstractmethod
    def is_available(self) -> bool:
        pass

    @abstractmethod
    def preference_fields(self) -> List[PreferenceField]:
        pass

    @abstractmethod
    def scanner_capabilities(self) -> DeviceCapabilities:
        pass

    def sync_legacy_settings(self, settings: 'Settings') -> None:
        """Write scanner_mode for backward compatibility."""
        pass


class TurntableBackend(ABC):
    id: str
    label: str

    @abstractmethod
    def is_available(self) -> bool:
        pass

    @abstractmethod
    def preference_fields(self) -> List[PreferenceField]:
        pass

    def turntable_capabilities(self) -> DeviceCapabilities:
        return DeviceCapabilities(scanner_id='', turntable_id=self.id)

    def sync_legacy_settings(self, settings: 'Settings') -> None:
        pass

    def create_board(self, parent=None):
        raise NotImplementedError
