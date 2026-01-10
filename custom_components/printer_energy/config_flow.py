"""Config flow for Printer Energy Tracker integration."""

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.const import CONF_NAME, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    CONF_ENERGY_SENSOR,
    CONF_PRINTER_STATE_SENSOR,
    CONF_PRINTING_STATE_VALUE,
    DEFAULT_PRINTING_STATE,
    DOMAIN,
    NAME,
)

_LOGGER = logging.getLogger(__name__)


def validate_energy_sensor(hass: HomeAssistant, entity_id: str) -> str | None:
    """Validate that the entity is an energy sensor."""
    state = hass.states.get(entity_id)
    if state is None:
        return "entity_not_found"

    if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
        return "entity_unavailable"

    # Check if it's an energy sensor
    device_class = state.attributes.get("device_class")
    if device_class != "energy":
        return "not_energy_sensor"

    unit = state.attributes.get("unit_of_measurement", "").lower()
    if "kwh" not in unit:
        return "not_kwh_unit"

    return None


def validate_printer_sensor(hass: HomeAssistant, entity_id: str) -> str | None:
    """Validate that the entity exists and is a valid sensor."""
    state = hass.states.get(entity_id)
    if state is None:
        return "entity_not_found"

    if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
        return "entity_unavailable"

    return None


class PrinterEnergyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Printer Energy Tracker."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        _LOGGER.debug("Config flow user step called")
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate energy sensor
            energy_error = await self.hass.async_add_executor_job(
                validate_energy_sensor, self.hass, user_input[CONF_ENERGY_SENSOR]
            )
            if energy_error:
                errors[CONF_ENERGY_SENSOR] = energy_error

            # Validate printer state sensor
            printer_error = await self.hass.async_add_executor_job(
                validate_printer_sensor, self.hass, user_input[CONF_PRINTER_STATE_SENSOR]
            )
            if printer_error:
                errors[CONF_PRINTER_STATE_SENSOR] = printer_error

            # Ensure sensors are different
            if (
                user_input[CONF_ENERGY_SENSOR] == user_input[CONF_PRINTER_STATE_SENSOR]
                and not errors
            ):
                errors["base"] = "same_sensors"

            if not errors:
                # Create the config entry
                return self.async_create_entry(
                    title=user_input.get(CONF_NAME, NAME),
                    data=user_input,
                )

        # Build entity selector filters
        energy_entity_selector = selector.EntitySelector(
            selector.EntitySelectorConfig(
                domain=SENSOR_DOMAIN,
                device_class="energy",
                unit_of_measurement="kWh",
            )
        )

        printer_entity_selector = selector.EntitySelector(
            selector.EntitySelectorConfig(domain=SENSOR_DOMAIN)
        )

        schema = vol.Schema(
            {
                vol.Optional(CONF_NAME, default=NAME): str,
                vol.Required(CONF_ENERGY_SENSOR): energy_entity_selector,
                vol.Required(CONF_PRINTER_STATE_SENSOR): printer_entity_selector,
                vol.Optional(
                    CONF_PRINTING_STATE_VALUE, default=DEFAULT_PRINTING_STATE
                ): str,
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return PrinterEnergyOptionsFlow(config_entry)


class PrinterEnergyOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Printer Energy Tracker."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate energy sensor if changed
            if user_input[CONF_ENERGY_SENSOR] != self.config_entry.data[CONF_ENERGY_SENSOR]:
                energy_error = await self.hass.async_add_executor_job(
                    validate_energy_sensor, self.hass, user_input[CONF_ENERGY_SENSOR]
                )
                if energy_error:
                    errors[CONF_ENERGY_SENSOR] = energy_error

            # Validate printer state sensor if changed
            if (
                user_input[CONF_PRINTER_STATE_SENSOR]
                != self.config_entry.data[CONF_PRINTER_STATE_SENSOR]
            ):
                printer_error = await self.hass.async_add_executor_job(
                    validate_printer_sensor,
                    self.hass,
                    user_input[CONF_PRINTER_STATE_SENSOR],
                )
                if printer_error:
                    errors[CONF_PRINTER_STATE_SENSOR] = printer_error

            # Ensure sensors are different
            if (
                user_input[CONF_ENERGY_SENSOR] == user_input[CONF_PRINTER_STATE_SENSOR]
                and not errors
            ):
                errors["base"] = "same_sensors"

            if not errors:
                # Update config entry
                self.hass.config_entries.async_update_entry(
                    self.config_entry, data=user_input
                )
                return self.async_create_entry(title="", data={})

        energy_entity_selector = selector.EntitySelector(
            selector.EntitySelectorConfig(
                domain=SENSOR_DOMAIN,
                device_class="energy",
                unit_of_measurement="kWh",
            )
        )

        printer_entity_selector = selector.EntitySelector(
            selector.EntitySelectorConfig(domain=SENSOR_DOMAIN)
        )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_ENERGY_SENSOR,
                    default=self.config_entry.data.get(CONF_ENERGY_SENSOR),
                ): energy_entity_selector,
                vol.Required(
                    CONF_PRINTER_STATE_SENSOR,
                    default=self.config_entry.data.get(CONF_PRINTER_STATE_SENSOR),
                ): printer_entity_selector,
                vol.Optional(
                    CONF_PRINTING_STATE_VALUE,
                    default=self.config_entry.data.get(
                        CONF_PRINTING_STATE_VALUE, DEFAULT_PRINTING_STATE
                    ),
                ): str,
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)
