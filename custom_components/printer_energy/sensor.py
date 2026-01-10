"""Sensor entities for Printer Energy Tracker."""

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import UnitOfEnergy

from .const import (
    ATTR_ACTIVE_PRINT,
    ATTR_ENERGY_KWH,
    ATTR_END_TIME,
    ATTR_PRINT_COUNT,
    ATTR_START_ENERGY,
    ATTR_START_TIME,
    DOMAIN,
)
from .coordinator import PrinterEnergyCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from a config entry."""
    coordinator: PrinterEnergyCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            LastPrintEnergySensor(coordinator, entry),
            TotalPrintEnergySensor(coordinator, entry),
            PrintCountSensor(coordinator, entry),
        ]
    )


class PrinterEnergySensor(CoordinatorEntity[PrinterEnergyCoordinator], SensorEntity):
    """Base class for printer energy sensors."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self,
        coordinator: PrinterEnergyCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self._entry_id = entry.entry_id
        self._attr_unique_id = f"{entry.entry_id}_{self.entity_description.key}"

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": "Printer Energy Tracker",
            "manufacturer": "Home Assistant",
            "model": "Printer Energy Tracker",
        }

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()


class LastPrintEnergySensor(PrinterEnergySensor):
    """Sensor for energy used in the last print."""

    entity_description = SensorEntityDescription(
        key="last_print_energy",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    )

    def __init__(
        self,
        coordinator: PrinterEnergyCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator, entry)
        self._attr_name = "Last Print Energy"

    @property
    def native_value(self) -> float | None:
        """Return the energy used in the last print."""
        last_print = self.coordinator.data.get("last_print")
        if last_print:
            return last_print.energy_kwh
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        last_print = self.coordinator.data.get("last_print")
        if not last_print:
            return {}

        attrs: dict[str, Any] = {
            ATTR_START_TIME: last_print.start_time.isoformat(),
            ATTR_END_TIME: last_print.end_time.isoformat(),
            ATTR_ENERGY_KWH: last_print.energy_kwh,
        }

        # Add active print info if available
        active_print = self.coordinator.data.get("active_print")
        if active_print:
            attrs[ATTR_ACTIVE_PRINT] = True
            attrs[ATTR_START_ENERGY] = active_print.start_energy
        else:
            attrs[ATTR_ACTIVE_PRINT] = False

        return attrs


class TotalPrintEnergySensor(PrinterEnergySensor):
    """Sensor for total energy used across all prints."""

    entity_description = SensorEntityDescription(
        key="total_print_energy",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    )

    def __init__(
        self,
        coordinator: PrinterEnergyCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator, entry)
        self._attr_name = "Total Print Energy"

    @property
    def native_value(self) -> float:
        """Return the total energy used across all prints."""
        return self.coordinator.data.get("total_energy", 0.0)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        return {
            ATTR_PRINT_COUNT: self.coordinator.data.get("print_count", 0),
        }


class PrintCountSensor(PrinterEnergySensor):
    """Sensor for total number of completed prints."""

    entity_description = SensorEntityDescription(
        key="print_count",
        device_class=None,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=None,
    )

    def __init__(
        self,
        coordinator: PrinterEnergyCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator, entry)
        self._attr_name = "Print Count"
        self._attr_icon = "mdi:printer-3d"

    @property
    def native_value(self) -> int:
        """Return the total number of completed prints."""
        return self.coordinator.data.get("print_count", 0)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attrs: dict[str, Any] = {
            ATTR_PRINT_COUNT: self.native_value,
        }

        # Add active print info if available
        active_print = self.coordinator.data.get("active_print")
        if active_print:
            attrs[ATTR_ACTIVE_PRINT] = True
            attrs[ATTR_START_TIME] = active_print.start_time.isoformat()
            attrs[ATTR_START_ENERGY] = active_print.start_energy
        else:
            attrs[ATTR_ACTIVE_PRINT] = False

        return attrs
