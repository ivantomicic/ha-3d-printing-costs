"""Sensor platform for Printer Energy integration."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .helpers import slugify_device_name

from .const import (
    ATTR_LAST_PRINT_ENERGY,
    ATTR_LAST_PRINT_ENERGY_COST,
    ATTR_LAST_PRINT_END,
    ATTR_LAST_PRINT_MATERIAL,
    ATTR_LAST_PRINT_MATERIAL_COST,
    ATTR_LAST_PRINT_START,
    ATTR_LAST_PRINT_TOTAL_COST,
    ATTR_PRINT_COUNT,
    ATTR_TOTAL_COST,
    ATTR_TOTAL_ENERGY,
    ATTR_TOTAL_ENERGY_COST,
    ATTR_TOTAL_MATERIAL,
    ATTR_TOTAL_MATERIAL_COST,
    DOMAIN,
)
from .coordinator import PrinterEnergyCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the printer energy sensors."""
    coordinator: PrinterEnergyCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        TotalEnergySensor(coordinator, config_entry),
        PrintCountSensor(coordinator, config_entry),
        LastPrintEnergySensor(coordinator, config_entry),
        LastPrintCostSensor(coordinator, config_entry),
        TotalCostSensor(coordinator, config_entry),
    ]
    
    # Add material sensor only if material tracking is configured
    coordinator_instance: PrinterEnergyCoordinator = coordinator
    if coordinator_instance.material_sensor:
        entities.append(LastPrintMaterialSensor(coordinator, config_entry))

    async_add_entities(entities)


class PrinterEnergySensor(CoordinatorEntity, SensorEntity):
    """Base class for printer energy sensors."""

    def __init__(
        self,
        coordinator: PrinterEnergyCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.config_entry = config_entry
        # Get device name and slugify it for entity ID
        device_name = config_entry.data.get(CONF_NAME, config_entry.title or "3D Printer Energy Tracker")
        device_slug = slugify_device_name(device_name)
        self._attr_unique_id = f"{device_slug}_{self.entity_key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": device_name,
            "manufacturer": "Custom",
            "model": "3D Printer Energy Tracker",
        }

    @property
    def entity_key(self) -> str:
        """Return the entity key for unique_id."""
        raise NotImplementedError

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success


class TotalEnergySensor(PrinterEnergySensor):
    """Sensor for total energy consumed during prints."""

    _attr_name = "Total Energy"
    _attr_native_unit_of_measurement = "kWh"
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_icon = "mdi:flash"

    @property
    def entity_key(self) -> str:
        """Return the entity key."""
        return "total_energy"

    @property
    def native_value(self) -> float:
        """Return the total energy consumed."""
        if self.coordinator.data:
            return round(self.coordinator.data.get("total_energy", 0.0), 3)
        return 0.0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attrs = {}
        if self.coordinator.data:
            attrs[ATTR_PRINT_COUNT] = self.coordinator.data.get("print_count", 0)
            attrs[ATTR_LAST_PRINT_ENERGY] = self.coordinator.data.get(
                "last_print_energy", 0.0
            )
            if self.coordinator.data.get("last_print_start"):
                attrs[ATTR_LAST_PRINT_START] = self.coordinator.data["last_print_start"]
            if self.coordinator.data.get("last_print_end"):
                attrs[ATTR_LAST_PRINT_END] = self.coordinator.data["last_print_end"]
            if self.coordinator.data.get("last_print_material", 0.0) > 0:
                attrs[ATTR_LAST_PRINT_MATERIAL] = self.coordinator.data.get(
                    "last_print_material", 0.0
                )
            if self.coordinator.data.get("total_material", 0.0) > 0:
                attrs[ATTR_TOTAL_MATERIAL] = self.coordinator.data.get(
                    "total_material", 0.0
                )
            # Add cost information
            attrs[ATTR_TOTAL_ENERGY_COST] = self.coordinator.data.get(
                "total_energy_cost", 0.0
            )
            attrs[ATTR_TOTAL_COST] = self.coordinator.data.get("total_cost", 0.0)
            if self.coordinator.data.get("last_print_total_cost", 0.0) > 0:
                attrs[ATTR_LAST_PRINT_TOTAL_COST] = self.coordinator.data.get(
                    "last_print_total_cost", 0.0
                )
            if self.coordinator.data.get("total_material_cost", 0.0) > 0:
                attrs[ATTR_TOTAL_MATERIAL_COST] = self.coordinator.data.get(
                    "total_material_cost", 0.0
                )
        return attrs


class PrintCountSensor(PrinterEnergySensor):
    """Sensor for print count."""

    _attr_name = "Print Count"
    _attr_native_unit_of_measurement = "prints"
    _attr_icon = "mdi:counter"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def entity_key(self) -> str:
        """Return the entity key."""
        return "print_count"

    @property
    def native_value(self) -> int:
        """Return the print count."""
        if self.coordinator.data:
            return self.coordinator.data.get("print_count", 0)
        return 0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attrs = {}
        if self.coordinator.data:
            attrs[ATTR_TOTAL_ENERGY] = self.coordinator.data.get("total_energy", 0.0)
            attrs[ATTR_LAST_PRINT_ENERGY] = self.coordinator.data.get(
                "last_print_energy", 0.0
            )
            if self.coordinator.data.get("last_print_material", 0.0) > 0:
                attrs[ATTR_LAST_PRINT_MATERIAL] = self.coordinator.data.get(
                    "last_print_material", 0.0
                )
            if self.coordinator.data.get("total_material", 0.0) > 0:
                attrs[ATTR_TOTAL_MATERIAL] = self.coordinator.data.get(
                    "total_material", 0.0
                )
        return attrs


class LastPrintEnergySensor(PrinterEnergySensor):
    """Sensor for last print energy consumption."""

    _attr_name = "Last Print Energy"
    _attr_native_unit_of_measurement = "kWh"
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:flash-outline"

    @property
    def entity_key(self) -> str:
        """Return the entity key."""
        return "last_print_energy"

    @property
    def native_value(self) -> float:
        """Return the last print energy."""
        if self.coordinator.data:
            return round(self.coordinator.data.get("last_print_energy", 0.0), 3)
        return 0.0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attrs = {}
        if self.coordinator.data:
            if self.coordinator.data.get("last_print_start"):
                attrs[ATTR_LAST_PRINT_START] = self.coordinator.data["last_print_start"]
            if self.coordinator.data.get("last_print_end"):
                attrs[ATTR_LAST_PRINT_END] = self.coordinator.data["last_print_end"]
            attrs[ATTR_TOTAL_ENERGY] = self.coordinator.data.get("total_energy", 0.0)
            attrs[ATTR_PRINT_COUNT] = self.coordinator.data.get("print_count", 0)
            if self.coordinator.data.get("last_print_material", 0.0) > 0:
                attrs[ATTR_LAST_PRINT_MATERIAL] = self.coordinator.data.get(
                    "last_print_material", 0.0
                )
            if self.coordinator.data.get("total_material", 0.0) > 0:
                attrs[ATTR_TOTAL_MATERIAL] = self.coordinator.data.get(
                    "total_material", 0.0
                )
            # Add cost information
            if self.coordinator.data.get("last_print_total_cost", 0.0) > 0:
                attrs[ATTR_LAST_PRINT_TOTAL_COST] = self.coordinator.data.get(
                    "last_print_total_cost", 0.0
                )
                attrs[ATTR_LAST_PRINT_ENERGY_COST] = self.coordinator.data.get(
                    "last_print_energy_cost", 0.0
                )
                if self.coordinator.data.get("last_print_material_cost", 0.0) > 0:
                    attrs[ATTR_LAST_PRINT_MATERIAL_COST] = self.coordinator.data.get(
                        "last_print_material_cost", 0.0
                    )
        return attrs


class LastPrintMaterialSensor(PrinterEnergySensor):
    """Sensor for last print material consumption."""

    _attr_name = "Last Print Material"
    _attr_native_unit_of_measurement = "mm"
    _attr_icon = "mdi:counter"
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def entity_key(self) -> str:
        """Return the entity key."""
        return "last_print_material"

    @property
    def native_value(self) -> float:
        """Return the last print material usage."""
        if self.coordinator.data:
            return round(self.coordinator.data.get("last_print_material", 0.0), 2)
        return 0.0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attrs = {}
        if self.coordinator.data:
            if self.coordinator.data.get("last_print_start"):
                attrs[ATTR_LAST_PRINT_START] = self.coordinator.data["last_print_start"]
            if self.coordinator.data.get("last_print_end"):
                attrs[ATTR_LAST_PRINT_END] = self.coordinator.data["last_print_end"]
            attrs[ATTR_TOTAL_MATERIAL] = self.coordinator.data.get("total_material", 0.0)
            attrs[ATTR_LAST_PRINT_ENERGY] = self.coordinator.data.get(
                "last_print_energy", 0.0
            )
            attrs[ATTR_TOTAL_ENERGY] = self.coordinator.data.get("total_energy", 0.0)
            attrs[ATTR_PRINT_COUNT] = self.coordinator.data.get("print_count", 0)
            # Add cost information
            if self.coordinator.data.get("last_print_total_cost", 0.0) > 0:
                attrs[ATTR_LAST_PRINT_TOTAL_COST] = self.coordinator.data.get(
                    "last_print_total_cost", 0.0
                )
                attrs[ATTR_LAST_PRINT_ENERGY_COST] = self.coordinator.data.get(
                    "last_print_energy_cost", 0.0
                )
                if self.coordinator.data.get("last_print_material_cost", 0.0) > 0:
                    attrs[ATTR_LAST_PRINT_MATERIAL_COST] = self.coordinator.data.get(
                        "last_print_material_cost", 0.0
                    )
        return attrs


class LastPrintCostSensor(PrinterEnergySensor):
    """Sensor for last print total cost."""

    _attr_name = "Last Print Cost"
    _attr_icon = "mdi:currency-usd"
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def entity_key(self) -> str:
        """Return the entity key."""
        return "last_print_cost"

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the currency unit."""
        if self.coordinator.data and self.coordinator.data.get("currency"):
            return self.coordinator.data.get("currency")
        return self.coordinator.currency if hasattr(self.coordinator, "currency") else "RSD"

    @property
    def native_value(self) -> float:
        """Return the last print total cost."""
        if self.coordinator.data:
            return round(self.coordinator.data.get("last_print_total_cost", 0.0), 2)
        return 0.0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attrs = {}
        if self.coordinator.data:
            if self.coordinator.data.get("last_print_start"):
                attrs[ATTR_LAST_PRINT_START] = self.coordinator.data["last_print_start"]
            if self.coordinator.data.get("last_print_end"):
                attrs[ATTR_LAST_PRINT_END] = self.coordinator.data["last_print_end"]
            attrs[ATTR_LAST_PRINT_ENERGY_COST] = self.coordinator.data.get(
                "last_print_energy_cost", 0.0
            )
            attrs[ATTR_LAST_PRINT_ENERGY] = self.coordinator.data.get(
                "last_print_energy", 0.0
            )
            if self.coordinator.data.get("last_print_material_cost", 0.0) > 0:
                attrs[ATTR_LAST_PRINT_MATERIAL_COST] = self.coordinator.data.get(
                    "last_print_material_cost", 0.0
                )
                attrs[ATTR_LAST_PRINT_MATERIAL] = self.coordinator.data.get(
                    "last_print_material", 0.0
                )
            attrs[ATTR_TOTAL_COST] = self.coordinator.data.get("total_cost", 0.0)
            attrs[ATTR_PRINT_COUNT] = self.coordinator.data.get("print_count", 0)
        return attrs


class TotalCostSensor(PrinterEnergySensor):
    """Sensor for total cost across all prints."""

    _attr_name = "Total Cost"
    _attr_icon = "mdi:cash"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def entity_key(self) -> str:
        """Return the entity key."""
        return "total_cost"

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the currency unit."""
        if self.coordinator.data and self.coordinator.data.get("currency"):
            return self.coordinator.data.get("currency")
        return self.coordinator.currency if hasattr(self.coordinator, "currency") else "RSD"

    @property
    def native_value(self) -> float:
        """Return the total cost."""
        if self.coordinator.data:
            return round(self.coordinator.data.get("total_cost", 0.0), 2)
        return 0.0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attrs = {}
        if self.coordinator.data:
            attrs[ATTR_PRINT_COUNT] = self.coordinator.data.get("print_count", 0)
            attrs[ATTR_TOTAL_ENERGY_COST] = self.coordinator.data.get(
                "total_energy_cost", 0.0
            )
            attrs[ATTR_TOTAL_ENERGY] = self.coordinator.data.get("total_energy", 0.0)
            if self.coordinator.data.get("total_material_cost", 0.0) > 0:
                attrs[ATTR_TOTAL_MATERIAL_COST] = self.coordinator.data.get(
                    "total_material_cost", 0.0
                )
                attrs[ATTR_TOTAL_MATERIAL] = self.coordinator.data.get(
                    "total_material", 0.0
                )
            attrs[ATTR_LAST_PRINT_TOTAL_COST] = self.coordinator.data.get(
                "last_print_total_cost", 0.0
            )
        return attrs
