"""Storage handler for print history using Home Assistant Store."""

from datetime import datetime
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import STORAGE_KEY, STORAGE_VERSION


class PrintRecord:
    """Represents a single print record."""

    def __init__(
        self,
        start_time: datetime,
        end_time: datetime,
        energy_kwh: float,
    ) -> None:
        """Initialize print record."""
        self.start_time = start_time
        self.end_time = end_time
        self.energy_kwh = energy_kwh

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "energy_kwh": self.energy_kwh,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PrintRecord":
        """Create from dictionary."""
        return cls(
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]),
            energy_kwh=float(data["energy_kwh"]),
        )


class ActivePrint:
    """Represents an active print session."""

    def __init__(
        self,
        start_time: datetime,
        start_energy: float,
    ) -> None:
        """Initialize active print."""
        self.start_time = start_time
        self.start_energy = start_energy

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "start_time": self.start_time.isoformat(),
            "start_energy": self.start_energy,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ActivePrint":
        """Create from dictionary."""
        return cls(
            start_time=datetime.fromisoformat(data["start_time"]),
            start_energy=float(data["start_energy"]),
        )


class PrintStorage:
    """Handle persistence of print records."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize storage."""
        self.hass = hass
        self._store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._prints: list[PrintRecord] = []
        self._active_print: ActivePrint | None = None

    async def async_load(self) -> None:
        """Load print history from storage."""
        data = await self._store.async_load()
        if data:
            self._prints = [
                PrintRecord.from_dict(record) for record in data.get("prints", [])
            ]
            active_data = data.get("active_print")
            if active_data:
                self._active_print = ActivePrint.from_dict(active_data)
        else:
            self._prints = []
            self._active_print = None

    async def async_save(self) -> None:
        """Save print history to storage."""
        data = {
            "prints": [record.to_dict() for record in self._prints],
            "active_print": self._active_print.to_dict() if self._active_print else None,
        }
        await self._store.async_save(data)

    def add_print(self, record: PrintRecord) -> None:
        """Add a completed print record."""
        self._prints.append(record)

    def set_active_print(self, active_print: ActivePrint | None) -> None:
        """Set or clear active print."""
        self._active_print = active_print

    def get_active_print(self) -> ActivePrint | None:
        """Get active print if any."""
        return self._active_print

    def get_all_prints(self) -> list[PrintRecord]:
        """Get all completed print records."""
        return self._prints.copy()

    def get_total_energy(self) -> float:
        """Calculate total energy across all prints."""
        return sum(print_record.energy_kwh for print_record in self._prints)

    def get_print_count(self) -> int:
        """Get total number of completed prints."""
        return len(self._prints)

    def get_last_print(self) -> PrintRecord | None:
        """Get the most recent print record."""
        return self._prints[-1] if self._prints else None
