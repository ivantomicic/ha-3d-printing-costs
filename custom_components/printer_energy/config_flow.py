"""Config flow for Printer Energy integration."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import CONF_NAME
from homeassistant.helpers import selector

from .const import (
    CONF_CURRENCY,
    CONF_ENERGY_ATTRIBUTE,
    CONF_ENERGY_COST_PER_KWH,
    CONF_ENERGY_SENSOR,
    CONF_MATERIAL_COST_PER_SPOOL,
    CONF_MATERIAL_SENSOR,
    CONF_MATERIAL_SPOOL_LENGTH,
    CONF_PRINTING_SENSOR,
    CONF_PRINTING_STATE,
    DEFAULT_CURRENCY,
    DEFAULT_ENERGY_ATTRIBUTE,
    DEFAULT_ENERGY_COST,
    DEFAULT_PRINTING_STATE,
    DEFAULT_SPOOL_LENGTH,
    DOMAIN,
)


class PrinterEnergyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Printer Energy."""

    VERSION = 2

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate the sensors exist
            energy_sensor = user_input[CONF_ENERGY_SENSOR]
            printing_sensor = user_input[CONF_PRINTING_SENSOR]
            material_sensor = user_input.get(CONF_MATERIAL_SENSOR)

            if self.hass.states.get(energy_sensor) is None:
                errors[CONF_ENERGY_SENSOR] = "entity_not_found"
            elif self.hass.states.get(printing_sensor) is None:
                errors[CONF_PRINTING_SENSOR] = "entity_not_found"
            elif material_sensor and material_sensor.strip() and self.hass.states.get(material_sensor) is None:
                errors[CONF_MATERIAL_SENSOR] = "entity_not_found"
            else:
                # Clean up material sensor - remove if empty
                if material_sensor and not material_sensor.strip():
                    user_input[CONF_MATERIAL_SENSOR] = None
                elif material_sensor:
                    user_input[CONF_MATERIAL_SENSOR] = material_sensor.strip()
                
                # Check for duplicate entries
                unique_id_parts = [energy_sensor, printing_sensor]
                if user_input.get(CONF_MATERIAL_SENSOR):
                    unique_id_parts.append(user_input[CONF_MATERIAL_SENSOR])
                await self.async_set_unique_id("_".join(unique_id_parts))
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=user_input.get(CONF_NAME, "3D Printer Energy Tracker"),
                    data=user_input,
                )

        schema = vol.Schema(
            {
                vol.Optional(CONF_NAME, default="3D Printer Energy Tracker"): str,
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
                vol.Optional(
                    CONF_ENERGY_COST_PER_KWH,
                    default=DEFAULT_ENERGY_COST,
                ): vol.Coerce(float),
                vol.Optional(
                    CONF_MATERIAL_COST_PER_SPOOL,
                    default=0.0,
                ): vol.Coerce(float),
                vol.Optional(
                    CONF_MATERIAL_SPOOL_LENGTH,
                    default=DEFAULT_SPOOL_LENGTH,
                ): vol.Coerce(float),
                vol.Optional(
                    CONF_CURRENCY,
                    default=DEFAULT_CURRENCY,
                ): str,
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
        """Manage the options menu."""
        errors = {}
        if user_input is not None:
            if user_input["next_step"] == "options":
                return await self.async_step_options()
            elif user_input["next_step"] == "reset":
                return await self.async_step_reset_confirm()

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required("next_step", default="options"): vol.In(
                        {
                            "options": "⚙️ Configure Settings",
                            "reset": "⚠️ Reset All Data",
                        }
                    ),
                }
            ),
            description_placeholders={
                "name": self.config_entry.title,
            },
            errors=errors,
        )

    async def async_step_options(self, user_input=None):
        """Handle options configuration."""
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
                    CONF_ENERGY_COST_PER_KWH,
                    default=self.config_entry.options.get(
                        CONF_ENERGY_COST_PER_KWH,
                        self.config_entry.data.get(
                            CONF_ENERGY_COST_PER_KWH, DEFAULT_ENERGY_COST
                        ),
                    ),
                ): vol.Coerce(float),
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
                vol.Optional(
                    CONF_CURRENCY,
                    default=self.config_entry.options.get(
                        CONF_CURRENCY,
                        self.config_entry.data.get(CONF_CURRENCY, DEFAULT_CURRENCY),
                    ),
                ): str,
            }
        )

        return self.async_show_form(step_id="options", data_schema=schema)

    async def async_step_reset_confirm(self, user_input=None):
        """Confirm reset data."""
        errors = {}
        if user_input is not None:
            if user_input.get("confirm") is True:
                # Reset data
                hass = self.hass
                coordinator = hass.data.get(DOMAIN, {}).get(self.config_entry.entry_id)
                
                if coordinator:
                    from .coordinator import PrinterEnergyCoordinator
                    if isinstance(coordinator, PrinterEnergyCoordinator):
                        await coordinator.async_reset_data()
                        # Reload entry to refresh all sensors
                        await hass.config_entries.async_reload(self.config_entry.entry_id)
                        return self.async_create_entry(title="", data={})
                    else:
                        errors["base"] = "invalid_coordinator"
                else:
                    errors["base"] = "coordinator_not_found"
            else:
                # User cancelled, go back to menu
                return await self.async_step_init()

        return self.async_show_form(
            step_id="reset_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required("confirm", default=False): bool,
                }
            ),
            description_placeholders={
                "name": self.config_entry.title,
                "warning": "⚠️ This will reset ALL statistics including:\n- Total energy\n- Total material\n- Total costs\n- Print count\n- Last print data\n\nThis action CANNOT be undone!"
            },
            errors=errors,
        )
