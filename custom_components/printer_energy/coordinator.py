"""Data update coordinator for Printer Energy Tracker."""

from typing import Any

from homeassistant.core import HomeAssistant, State, callback
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.util import dt as dt_util

from .const import (
    CONF_ENERGY_SENSOR,
    CONF_PRINTER_STATE_SENSOR,
    CONF_PRINTING_STATE_VALUE,
    DOMAIN,
)
from .storage import ActivePrint, PrintRecord, PrintStorage


class PrinterEnergyCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate data updates for Printer Energy Tracker."""

    def __init__(
        self,
        hass: HomeAssistant,
        config: dict[str, Any],
        storage: PrintStorage,
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            logger=__name__,
            name=DOMAIN,
            update_interval=None,  # We use state change listeners instead
        )
        self._config = config
        self._storage = storage
        self._energy_entity = config[CONF_ENERGY_SENSOR]
        self._printer_state_entity = config[CONF_PRINTER_STATE_SENSOR]
        self._printing_state_value = config.get(
            CONF_PRINTING_STATE_VALUE, "printing"
        ).lower()
        self._previous_printer_state: str | None = None

    async def async_start(self) -> None:
        """Start the coordinator and set up listeners."""
        # Load existing data
        await self._storage.async_load()

        # Handle active print from previous session
        active_print = self._storage.get_active_print()
        if active_print:
            # Check current printer state
            current_state = self._get_printer_state()
            if current_state and current_state.lower() == self._printing_state_value:
                # Print is still active, continue tracking
                self.logger.info(
                    "Resuming active print from %s", active_print.start_time
                )
            else:
                # Print ended while HA was down, try to calculate energy if possible
                await self._handle_print_end(active_print)

        # Set up state change listener for printer state
        self.async_on_remove(
            async_track_state_change_event(
                self.hass,
                [self._printer_state_entity],
                self._async_printer_state_changed,
            )
        )

        # Initialize data
        await self.async_request_refresh()

    async def _async_update_data(self) -> dict[str, Any]:
        """Update coordinator data."""
        # This is called periodically, but we mainly use state change events
        return {
            "active_print": self._storage.get_active_print(),
            "total_energy": self._storage.get_total_energy(),
            "print_count": self._storage.get_print_count(),
            "last_print": self._storage.get_last_print(),
        }

    @callback
    def _async_printer_state_changed(self, event: Any) -> None:
        """Handle printer state changes."""
        new_state_obj = event.data.get("new_state")
        old_state_obj = event.data.get("old_state")

        if not new_state_obj or not old_state_obj:
            return

        new_state = new_state_obj.state
        old_state = old_state_obj.state

        # Ignore unavailable/unknown states
        if new_state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return
        if old_state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            old_state = None

        new_state_lower = new_state.lower()
        old_state_lower = old_state.lower() if old_state else None

        # Check for print start
        if (
            old_state_lower != self._printing_state_value
            and new_state_lower == self._printing_state_value
        ):
            self.hass.async_create_task(self._handle_print_start())

        # Check for print end
        elif (
            old_state_lower == self._printing_state_value
            and new_state_lower != self._printing_state_value
        ):
            active_print = self._storage.get_active_print()
            if active_print:
                self.hass.async_create_task(self._handle_print_end(active_print))

        self._previous_printer_state = new_state

    async def _handle_print_start(self) -> None:
        """Handle print start event."""
        energy_value = self._get_energy_value()
        if energy_value is None:
            self.logger.warning(
                "Cannot start print tracking: energy sensor unavailable"
            )
            return

        active_print = ActivePrint(
            start_time=dt_util.now(),
            start_energy=energy_value,
        )

        self._storage.set_active_print(active_print)
        await self._storage.async_save()

        self.logger.info(
            "Print started at %s (start energy: %.3f kWh)",
            active_print.start_time,
            active_print.start_energy,
        )

        # Notify listeners
        await self.async_request_refresh()

    async def _handle_print_end(self, active_print: ActivePrint) -> None:
        """Handle print end event."""
        energy_value = self._get_energy_value()
        if energy_value is None:
            self.logger.warning(
                "Cannot end print tracking: energy sensor unavailable. "
                "Print will be discarded."
            )
            self._storage.set_active_print(None)
            await self._storage.async_save()
            await self.async_request_refresh()
            return

        # Calculate energy used
        energy_used = energy_value - active_print.start_energy

        # Handle energy sensor reset or negative delta
        if energy_used < 0:
            self.logger.warning(
                "Negative energy delta detected (%.3f kWh). "
                "Energy sensor may have been reset. Discarding print.",
                energy_used,
            )
            self._storage.set_active_print(None)
            await self._storage.async_save()
            await self.async_request_refresh()
            return

        # Create print record
        end_time = dt_util.now()
        print_record = PrintRecord(
            start_time=active_print.start_time,
            end_time=end_time,
            energy_kwh=energy_used,
        )

        self._storage.add_print(print_record)
        self._storage.set_active_print(None)
        await self._storage.async_save()

        self.logger.info(
            "Print ended at %s (energy used: %.3f kWh, duration: %s)",
            end_time,
            energy_used,
            end_time - active_print.start_time,
        )

        # Notify listeners
        await self.async_request_refresh()

    def _get_energy_value(self) -> float | None:
        """Get current energy sensor value."""
        state = self.hass.states.get(self._energy_entity)
        if not state or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return None

        try:
            return float(state.state)
        except (ValueError, TypeError):
            self.logger.warning(
                "Energy sensor '%s' has invalid state: %s", self._energy_entity, state.state
            )
            return None

    def _get_printer_state(self) -> str | None:
        """Get current printer state."""
        state = self.hass.states.get(self._printer_state_entity)
        if not state or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return None
        return state.state
