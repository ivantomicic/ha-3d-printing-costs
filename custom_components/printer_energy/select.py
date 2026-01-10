"""Select platform for Printer Energy configuration."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_CURRENCY, DEFAULT_CURRENCY, DOMAIN
from .coordinator import PrinterEnergyCoordinator
from .helpers import slugify_device_name


# Common currency codes
CURRENCY_OPTIONS = [
    "USD",
    "EUR",
    "GBP",
    "RSD",
    "JPY",
    "CAD",
    "AUD",
    "CHF",
    "CNY",
    "INR",
]


SELECT_ENTITIES = (
    SelectEntityDescription(
        key=CONF_CURRENCY,
        name="Currency",
        icon="mdi:currency-usd",
        options=CURRENCY_OPTIONS,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the printer energy select entities."""
    coordinator: PrinterEnergyCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        PrinterEnergySelect(coordinator, config_entry, desc)
        for desc in SELECT_ENTITIES
    ]

    async_add_entities(entities)


class PrinterEnergySelect(CoordinatorEntity, SelectEntity):
    """Select entity for printer energy configuration."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: PrinterEnergyCoordinator,
        config_entry: ConfigEntry,
        description: SelectEntityDescription,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self.config_entry = config_entry
        # Get device name and slugify it for entity ID
        device_name = config_entry.data.get(CONF_NAME, config_entry.title or "3D Printer Energy Tracker")
        device_slug = slugify_device_name(device_name)
        self._attr_unique_id = f"{device_slug}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": device_name,
            "manufacturer": "Custom",
            "model": "3D Printer Energy Tracker",
        }

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        config = {**self.config_entry.data}
        if self.config_entry.options:
            config.update(self.config_entry.options)

        if self.entity_description.key == CONF_CURRENCY:
            return config.get(CONF_CURRENCY, DEFAULT_CURRENCY)
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        # Update config entry options
        new_options = {**self.config_entry.options}
        new_options[self.entity_description.key] = option

        # Update coordinator config
        coordinator_config = {**self.config_entry.data, **new_options}
        self.coordinator._update_cost_config(coordinator_config)

        # Update config entry
        self.hass.config_entries.async_update_entry(
            self.config_entry, options=new_options
        )

        # Refresh coordinator to apply changes
        await self.coordinator.async_request_refresh()
