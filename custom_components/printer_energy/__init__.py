"""Printer Energy Tracker integration for Home Assistant."""

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

from .const import DOMAIN
from .coordinator import PrinterEnergyCoordinator
from .storage import PrintStorage

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Printer Energy Tracker from a config entry."""
    # Initialize storage
    storage = PrintStorage(hass)
    await storage.async_load()

    # Create coordinator
    coordinator = PrinterEnergyCoordinator(hass, entry.data, storage)

    # Store coordinator in hass data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Start coordinator (sets up listeners)
    await coordinator.async_start()

    # Forward entry setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # Remove coordinator from hass data
        coordinator: PrinterEnergyCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        # Save storage before unloading
        await coordinator._storage.async_save()

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
