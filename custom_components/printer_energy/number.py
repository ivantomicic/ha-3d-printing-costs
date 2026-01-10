"""Number platform for Printer Energy configuration."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_MATERIAL_COST_PER_SPOOL,
    CONF_MATERIAL_SPOOL_LENGTH,
    DEFAULT_MATERIAL_COST_PER_SPOOL,
    DEFAULT_SPOOL_LENGTH,
    DOMAIN,
)
from .coordinator import PrinterEnergyCoordinator


NUMBER_ENTITIES = (
    NumberEntityDescription(
        key=CONF_MATERIAL_COST_PER_SPOOL,
        name="Material Cost per Spool",
        icon="mdi:currency-usd",
        native_min_value=0.0,
        native_max_value=5000.0,
        native_step=10,
        native_unit_of_measurement="RSD",
    ),
    NumberEntityDescription(
        key=CONF_MATERIAL_SPOOL_LENGTH,
        name="Spool Length",
        icon="mdi:meter-electric-outline",
        native_min_value=1,
        native_max_value=500,
        native_step=1,
        native_unit_of_measurement="m",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the printer energy number entities."""
    coordinator: PrinterEnergyCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        PrinterEnergyNumber(coordinator, config_entry, desc)
        for desc in NUMBER_ENTITIES
    ]

    async_add_entities(entities)


class PrinterEnergyNumber(CoordinatorEntity, NumberEntity):
    """Number entity for printer energy configuration."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: PrinterEnergyCoordinator,
        config_entry: ConfigEntry,
        description: NumberEntityDescription,
    ) -> None:
        """Initialize the number entity."""
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
    def native_value(self) -> float:
        """Return the current value."""
        config = {**self.config_entry.data}
        if self.config_entry.options:
            config.update(self.config_entry.options)

        key = self.entity_description.key
        if key == CONF_MATERIAL_COST_PER_SPOOL:
            return float(config.get(CONF_MATERIAL_COST_PER_SPOOL, DEFAULT_MATERIAL_COST_PER_SPOOL))
        elif key == CONF_MATERIAL_SPOOL_LENGTH:
            # Ensure integer value (no decimals) for spool length
            raw_value = config.get(CONF_MATERIAL_SPOOL_LENGTH, DEFAULT_SPOOL_LENGTH)
            return float(int(raw_value))
        return 0.0

    async def async_set_native_value(self, value: float) -> None:
        """Update the value."""
        key = self.entity_description.key
        
        # For spool length, ensure integer value (no decimals)
        if key == CONF_MATERIAL_SPOOL_LENGTH:
            value = int(round(value))
        
        # Update config entry options
        new_options = {**self.config_entry.options}
        new_options[key] = value

        # Update config entry
        self.hass.config_entries.async_update_entry(
            self.config_entry, options=new_options
        )

        # Update coordinator config with merged data
        coordinator_config = {**self.config_entry.data, **new_options}
        self.coordinator._update_cost_config(coordinator_config)

        # Refresh coordinator to apply changes
        await self.coordinator.async_request_refresh()
