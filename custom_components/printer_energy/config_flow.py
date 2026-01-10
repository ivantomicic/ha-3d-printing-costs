"""Config flow for Printer Energy integration."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import CONF_NAME
from homeassistant.helpers import selector

from .const import (
    CONF_ENERGY_ATTRIBUTE,
    CONF_ENERGY_COST_SENSOR,
    CONF_ENERGY_SENSOR,
    CONF_MATERIAL_COST_PER_SPOOL,
    CONF_MATERIAL_SENSOR,
    CONF_MATERIAL_SPOOL_LENGTH,
    CONF_PRINTING_SENSOR,
    CONF_PRINTING_STATE,
    DEFAULT_ENERGY_ATTRIBUTE,
    DEFAULT_PRINTING_STATE,
    DEFAULT_SPOOL_LENGTH,
    DOMAIN,
)


class PrinterEnergyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Printer Energy."""

    VERSION = 4

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate the sensors exist
            energy_sensor = user_input[CONF_ENERGY_SENSOR]
            printing_sensor = user_input[CONF_PRINTING_SENSOR]
            material_sensor = user_input.get(CONF_MATERIAL_SENSOR)

            energy_cost_sensor = user_input.get(CONF_ENERGY_COST_SENSOR)

            if self.hass.states.get(energy_sensor) is None:
                errors[CONF_ENERGY_SENSOR] = "entity_not_found"
            elif self.hass.states.get(printing_sensor) is None:
                errors[CONF_PRINTING_SENSOR] = "entity_not_found"
            elif material_sensor and material_sensor.strip() and self.hass.states.get(material_sensor) is None:
                errors[CONF_MATERIAL_SENSOR] = "entity_not_found"
            elif energy_cost_sensor and energy_cost_sensor.strip() and self.hass.states.get(energy_cost_sensor) is None:
                errors[CONF_ENERGY_COST_SENSOR] = "entity_not_found"
            else:
                # Clean up sensor values - remove if empty
                if material_sensor and not material_sensor.strip():
                    user_input[CONF_MATERIAL_SENSOR] = None
                elif material_sensor:
                    user_input[CONF_MATERIAL_SENSOR] = material_sensor.strip()
                
                if energy_cost_sensor and not energy_cost_sensor.strip():
                    user_input[CONF_ENERGY_COST_SENSOR] = None
                elif energy_cost_sensor:
                    user_input[CONF_ENERGY_COST_SENSOR] = energy_cost_sensor.strip()
                
                # Check for duplicate entries
                unique_id_parts = [energy_sensor, printing_sensor]
                if user_input.get(CONF_MATERIAL_SENSOR):
                    unique_id_parts.append(user_input[CONF_MATERIAL_SENSOR])
                await self.async_set_unique_id("_".join(unique_id_parts))
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=user_input.get(CONF_NAME, "3D Printer Cost Tracker"),
                    data=user_input,
                )

        schema = vol.Schema(
            {
                vol.Optional(CONF_NAME, default="3D Printer Cost Tracker"): str,
                vol.Required(CONF_ENERGY_SENSOR): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor",
                        multiple=False,
                    )
                ),
                vol.Optional(
                    CONF_ENERGY_ATTRIBUTE, default=DEFAULT_ENERGY_ATTRIBUTE
                ): str,
                vol.Required(CONF_PRINTING_SENSOR): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain=["binary_sensor", "sensor"],
                        multiple=False,
                    )
                ),
                vol.Optional(
                    CONF_PRINTING_STATE, default=DEFAULT_PRINTING_STATE
                ): str,
                vol.Optional(CONF_MATERIAL_SENSOR): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor",
                        multiple=False,
                    )
                ),
                vol.Optional(CONF_ENERGY_COST_SENSOR): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain=["sensor", "number"],
                        multiple=False,
                    )
                ),
                vol.Optional(
                    CONF_MATERIAL_COST_PER_SPOOL,
                    default=0.0,
                ): vol.Coerce(float),
                vol.Optional(
                    CONF_MATERIAL_SPOOL_LENGTH,
                    default=DEFAULT_SPOOL_LENGTH,
                ): vol.Coerce(float),
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return PrinterEnergyOptionsFlowHandler(config_entry)


class PrinterEnergyOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Printer Energy."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_ENERGY_ATTRIBUTE,
                    default=self.config_entry.options.get(
                        CONF_ENERGY_ATTRIBUTE,
                        self.config_entry.data.get(
                            CONF_ENERGY_ATTRIBUTE, DEFAULT_ENERGY_ATTRIBUTE
                        ),
                    ),
                ): str,
                vol.Optional(
                    CONF_PRINTING_STATE,
                    default=self.config_entry.options.get(
                        CONF_PRINTING_STATE,
                        self.config_entry.data.get(
                            CONF_PRINTING_STATE, DEFAULT_PRINTING_STATE
                        ),
                    ),
                ): str,
                vol.Optional(
                    CONF_MATERIAL_SENSOR,
                    default=self.config_entry.options.get(
                        CONF_MATERIAL_SENSOR,
                        self.config_entry.data.get(CONF_MATERIAL_SENSOR, ""),
                    ),
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor",
                        multiple=False,
                    )
                ),
                vol.Optional(
                    CONF_ENERGY_COST_SENSOR,
                    default=self.config_entry.options.get(
                        CONF_ENERGY_COST_SENSOR,
                        self.config_entry.data.get(CONF_ENERGY_COST_SENSOR, ""),
                    ),
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain=["sensor", "number"],
                        multiple=False,
                    )
                ),
                vol.Optional(
                    CONF_MATERIAL_COST_PER_SPOOL,
                    default=self.config_entry.options.get(
                        CONF_MATERIAL_COST_PER_SPOOL,
                        self.config_entry.data.get(CONF_MATERIAL_COST_PER_SPOOL, 0.0),
                    ),
                ): vol.Coerce(float),
                vol.Optional(
                    CONF_MATERIAL_SPOOL_LENGTH,
                    default=self.config_entry.options.get(
                        CONF_MATERIAL_SPOOL_LENGTH,
                        self.config_entry.data.get(
                            CONF_MATERIAL_SPOOL_LENGTH, DEFAULT_SPOOL_LENGTH
                        ),
                    ),
                ): vol.Coerce(float),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
