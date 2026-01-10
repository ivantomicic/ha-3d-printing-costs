"""Text platform for Printer Energy configuration."""

from __future__ import annotations

from homeassistant.components.text import TextEntity, TextEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_CURRENCY_SENSOR, CONF_ENERGY_COST_SENSOR, DOMAIN
from .coordinator import PrinterEnergyCoordinator


TEXT_ENTITIES = (
    TextEntityDescription(
        key=CONF_ENERGY_COST_SENSOR,
        name="Energy Cost Sensor",
        icon="mdi:currency-usd",
        native_min=0,
        native_max=255,  # Max length for entity ID
    ),
    TextEntityDescription(
        key=CONF_CURRENCY_SENSOR,
        name="Currency Sensor",
        icon="mdi:currency-usd",
        native_min=0,
        native_max=255,  # Max length for entity ID
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the printer energy text entities."""
    coordinator: PrinterEnergyCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        PrinterEnergyText(coordinator, config_entry, desc)
        for desc in TEXT_ENTITIES
    ]

    async_add_entities(entities)


class PrinterEnergyText(CoordinatorEntity, TextEntity):
    """Text entity for printer energy configuration."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: PrinterEnergyCoordinator,
        config_entry: ConfigEntry,
        description: TextEntityDescription,
    ) -> None:
        """Initialize the text entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self.config_entry = config_entry
        device_name = config_entry.data.get(CONF_NAME, config_entry.title or "3D Printer Cost Tracker")
        self._attr_unique_id = f"{config_entry.entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": device_name,
            "manufacturer": "Custom",
            "model": "3D Printer Cost Tracker",
        }

    @property
    def native_value(self) -> str:
        """Return the current entity ID."""
        config = {**self.config_entry.data}
        if self.config_entry.options:
            config.update(self.config_entry.options)
        return config.get(self.entity_description.key, "") or ""

    async def async_set_value(self, value: str) -> None:
        """Update the entity ID."""
        # Clean up empty values
        if not value or not value.strip():
            value = None
        else:
            value = value.strip()

        # Update config entry options
        new_options = {**self.config_entry.options}
        new_options[self.entity_description.key] = value

        # Update coordinator config
        coordinator_config = {**self.config_entry.data, **new_options}
        self.coordinator._update_cost_config(coordinator_config)

        # Update config entry
        self.hass.config_entries.async_update_entry(
            self.config_entry, options=new_options
        )

        # Refresh coordinator to apply changes
        await self.coordinator.async_request_refresh()
