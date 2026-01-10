"""Button platform for Printer Energy integration."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import PrinterEnergyCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the printer energy button."""
    coordinator: PrinterEnergyCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities([ResetDataButton(coordinator, config_entry)])


class ResetDataButton(CoordinatorEntity, ButtonEntity):
    """Button to reset all data."""

    _attr_has_entity_name = True
    _attr_name = "Reset Data"
    _attr_icon = "mdi:restore"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        coordinator: PrinterEnergyCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the reset button."""
        super().__init__(coordinator)
        self.config_entry = config_entry
        device_name = config_entry.data.get(CONF_NAME, config_entry.title or "3D Printer Energy Tracker")
        self._attr_unique_id = f"{config_entry.entry_id}_reset_data"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": device_name,
            "manufacturer": "Custom",
            "model": "3D Printer Energy Tracker",
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return True

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.async_reset_data()
