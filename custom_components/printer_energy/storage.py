"""Storage handler for Printer Energy integration."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import DOMAIN, STORAGE_KEY, STORAGE_VERSION


class PrinterEnergyStorage:
    """Handle storage for printer energy data."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize storage."""
        self.hass = hass
        self.store = Store(hass, STORAGE_VERSION, STORAGE_KEY)

    async def load(self) -> dict:
        """Load data from storage."""
        data = await self.store.async_load()
        if data is None:
            return {
                "total_energy": 0.0,
                "print_count": 0,
                "last_print_energy": 0.0,
                "last_print_start": None,
                "last_print_end": None,
                "total_material": 0.0,
                "last_print_material": 0.0,
                "total_energy_cost": 0.0,
                "total_material_cost": 0.0,
                "total_cost": 0.0,
                "last_print_energy_cost": 0.0,
                "last_print_material_cost": 0.0,
                "last_print_total_cost": 0.0,
            }
        # Ensure material fields exist for backward compatibility
        if "total_material" not in data:
            data["total_material"] = 0.0
        if "last_print_material" not in data:
            data["last_print_material"] = 0.0
        # Ensure cost fields exist for backward compatibility
        if "total_energy_cost" not in data:
            data["total_energy_cost"] = 0.0
        if "total_material_cost" not in data:
            data["total_material_cost"] = 0.0
        if "total_cost" not in data:
            data["total_cost"] = 0.0
        if "last_print_energy_cost" not in data:
            data["last_print_energy_cost"] = 0.0
        if "last_print_material_cost" not in data:
            data["last_print_material_cost"] = 0.0
        if "last_print_total_cost" not in data:
            data["last_print_total_cost"] = 0.0
        return data

    async def save(self, data: dict) -> None:
        """Save data to storage."""
        await self.store.async_save(data)
