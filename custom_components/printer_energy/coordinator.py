"""Data coordinator for Printer Energy integration."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Callable

from homeassistant.core import HomeAssistant, State, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.util import dt as dt_util

from .const import (
    CONF_ENERGY_COST_SENSOR,
    CONF_ENERGY_SENSOR,
    CONF_MATERIAL_COST_PER_SPOOL,
    CONF_MATERIAL_SENSOR,
    CONF_MATERIAL_SPOOL_LENGTH,
    CONF_PRINTING_SENSOR,
    CONF_PRINTING_STATE,
    DEFAULT_MATERIAL_COST_PER_SPOOL,
    DEFAULT_SPOOL_LENGTH,
    DOMAIN,
    ENERGY_ATTRIBUTE,
    STORAGE_KEY,
    STORAGE_VERSION,
)
from .storage import PrinterEnergyStorage


class PrinterEnergyCoordinator(DataUpdateCoordinator):
    """Coordinate data updates for printer energy tracking."""

    def __init__(
        self,
        hass: HomeAssistant,
        config: dict[str, Any],
        entry_id: str,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            logger=__import__("logging").getLogger(__name__),
            name=DOMAIN,
            update_interval=None,  # We update on state changes, not on interval
        )
        self.hass = hass
        self.entry_id = entry_id
        self.energy_sensor = config[CONF_ENERGY_SENSOR]
        self.printing_sensor = config[CONF_PRINTING_SENSOR]
        printing_state_config = config.get(CONF_PRINTING_STATE, "on")
        # Support comma-separated states or single state
        if isinstance(printing_state_config, str):
            self.printing_states = [
                state.strip().lower()
                for state in printing_state_config.split(",")
                if state.strip()
            ]
        else:
            self.printing_states = [str(printing_state_config).lower()]
        if not self.printing_states:
            self.printing_states = ["on"]
        # Energy attribute is always "total_increased" (hardcoded, not stored as instance variable)
        material_sensor_config = config.get(CONF_MATERIAL_SENSOR)
        self.material_sensor = material_sensor_config.strip() if material_sensor_config and isinstance(material_sensor_config, str) else (material_sensor_config if material_sensor_config else None)
        
        # Energy cost sensor
        energy_cost_sensor_config = config.get(CONF_ENERGY_COST_SENSOR)
        self.energy_cost_sensor = energy_cost_sensor_config.strip() if energy_cost_sensor_config and isinstance(energy_cost_sensor_config, str) else (energy_cost_sensor_config if energy_cost_sensor_config else None)
        
        # Create entry-specific storage to prevent data sharing between instances
        self.storage = PrinterEnergyStorage(hass, entry_id)
        
        # Update cost configuration
        self._update_cost_config(config)

        self.is_printing = False
        self.session_start_energy = None
        self.current_session_energy = 0.0
        self.total_energy = 0.0
        self.print_count = 0
        self.last_print_energy = 0.0
        self.last_print_start = None
        self.last_print_end = None

        # Material tracking
        self.session_start_material = None
        self.current_session_material = 0.0
        self.total_material = 0.0
        self.last_print_material = 0.0

        # Cost tracking
        self.last_print_energy_cost = 0.0
        self.last_print_material_cost = 0.0
        self.last_print_total_cost = 0.0
        self.current_session_energy_cost = 0.0
        self.current_session_material_cost = 0.0
        self.current_session_total_cost = 0.0
        self.total_energy_cost = 0.0
        self.total_material_cost = 0.0
        self.total_cost = 0.0

        self._event_listeners = []

    def _update_cost_config(self, config: dict[str, Any]) -> None:
        """Update cost configuration from config."""
        # Update sensor references
        energy_cost_sensor_config = config.get(CONF_ENERGY_COST_SENSOR)
        self.energy_cost_sensor = energy_cost_sensor_config.strip() if energy_cost_sensor_config and isinstance(energy_cost_sensor_config, str) else (energy_cost_sensor_config if energy_cost_sensor_config else None)
        
        # Material cost configuration - cost per spool and spool length
        raw_spool_cost = config.get(CONF_MATERIAL_COST_PER_SPOOL, DEFAULT_MATERIAL_COST_PER_SPOOL)
        self.material_cost_per_spool = float(raw_spool_cost)
        # Spool length must be integer (no decimals)
        spool_length_raw = config.get(CONF_MATERIAL_SPOOL_LENGTH, DEFAULT_SPOOL_LENGTH)
        self.material_spool_length = float(int(spool_length_raw))
        # Calculate cost per meter from spool cost and length
        if self.material_spool_length > 0:
            self.material_cost_per_meter = self.material_cost_per_spool / self.material_spool_length
        else:
            self.material_cost_per_meter = 0.0
        self.logger.info(
            f"Material cost config: raw={raw_spool_cost}, spool_cost={self.material_cost_per_spool}, "
            f"spool_length={self.material_spool_length}, cost_per_meter={self.material_cost_per_meter}"
        )

    def _get_energy_cost_per_kwh(self) -> float:
        """Get energy cost per kWh from selected sensor/number entity."""
        if not self.energy_cost_sensor:
            return 0.0
        
        state = self.hass.states.get(self.energy_cost_sensor)
        if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN, None):
            return 0.0
        
        try:
            return float(state.state)
        except (ValueError, TypeError):
            self.logger.warning(f"Could not parse energy cost from {self.energy_cost_sensor}: {state.state}")
            return 0.0

    def _get_currency(self) -> str:
        """Get currency from energy cost sensor's unit_of_measurement (e.g., 'RSD/kWh' -> 'RSD')."""
        if not self.energy_cost_sensor:
            return "RSD"  # Default currency
        
        state = self.hass.states.get(self.energy_cost_sensor)
        if state is None:
            return "RSD"
        
        # Try to extract currency from unit_of_measurement attribute
        unit_of_measurement = state.attributes.get("unit_of_measurement")
        if unit_of_measurement and isinstance(unit_of_measurement, str):
            # If unit is like "RSD/kWh", extract "RSD"
            if "/" in unit_of_measurement:
                currency = unit_of_measurement.split("/")[0].strip().upper()
                if currency:
                    return currency
            # If unit is just "RSD", use it directly
            elif len(unit_of_measurement) <= 10:  # Reasonable currency code length
                currency = unit_of_measurement.strip().upper()
                if currency:
                    return currency
        
        # Default fallback
        return "RSD"

    async def async_config_entry_first_refresh(self) -> None:
        """Load persisted data on first refresh."""
        await self._load_persisted_data()
        await self._update_printing_state()
        await self.async_refresh()

    async def _load_persisted_data(self) -> None:
        """Load persisted data from storage."""
        data = await self.storage.load()
        
        # Check if entry-specific storage is empty (new entry or first load after migration)
        # If empty, try to migrate from old shared storage (one-time migration)
        has_data = data and (
            data.get("total_energy", 0.0) > 0 
            or data.get("print_count", 0) > 0
            or data.get("total_cost", 0.0) > 0
        )
        
        if not has_data:
            # Try to migrate from old shared storage key (for entries migrated from version 2)
            from homeassistant.helpers.storage import Store
            
            old_store = Store(self.hass, STORAGE_VERSION, STORAGE_KEY)
            old_data = await old_store.async_load()
            
            if old_data and (old_data.get("total_energy", 0.0) > 0 or old_data.get("print_count", 0) > 0):
                # Found old shared data, migrate it to this entry's storage
                # Note: Each entry will get its own copy of the old data, then diverge independently
                self.logger.info(
                    f"Migrating old shared storage data to entry-specific storage "
                    f"for entry {self.entry_id}. This is a one-time migration."
                )
                data = old_data.copy()  # Copy to avoid reference issues
                # Save migrated data to entry-specific storage
                await self.storage.save(data)
        
        self.total_energy = data.get("total_energy", 0.0)
        self.print_count = data.get("print_count", 0)
        self.last_print_energy = data.get("last_print_energy", 0.0)
        self.total_material = data.get("total_material", 0.0)
        self.last_print_material = data.get("last_print_material", 0.0)
        
        # Cost data
        self.total_energy_cost = data.get("total_energy_cost", 0.0)
        self.total_material_cost = data.get("total_material_cost", 0.0)
        self.total_cost = data.get("total_cost", 0.0)
        self.last_print_energy_cost = data.get("last_print_energy_cost", 0.0)
        self.last_print_material_cost = data.get("last_print_material_cost", 0.0)
        self.last_print_total_cost = data.get("last_print_total_cost", 0.0)
        
        if data.get("last_print_start"):
            try:
                self.last_print_start = dt_util.parse_datetime(data["last_print_start"])
            except (ValueError, TypeError):
                self.last_print_start = None
        
        if data.get("last_print_end"):
            try:
                self.last_print_end = dt_util.parse_datetime(data["last_print_end"])
            except (ValueError, TypeError):
                self.last_print_end = None

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data from sensors."""
        try:
            energy_state = self.hass.states.get(self.energy_sensor)
            printing_state = self.hass.states.get(self.printing_sensor)

            # Handle unavailable sensors gracefully - use last known values
            # Don't raise UpdateFailed, just skip updates for unavailable sensors
            current_energy = None
            if energy_state and energy_state.state not in (STATE_UNAVAILABLE, STATE_UNKNOWN):
                current_energy = self._get_energy_value(energy_state)
            else:
                # Energy sensor unavailable - use last known energy if we have it
                # This allows sensors to continue showing last known values
                self.logger.debug(f"Energy sensor {self.energy_sensor} is unavailable, using last known values")

            # Check printing state - handle unavailable printing sensor
            printing = False
            if printing_state and printing_state.state not in (STATE_UNAVAILABLE, STATE_UNKNOWN):
                printing_state_value = printing_state.state.lower()
                printing = printing_state_value in self.printing_states
            else:
                # Printing sensor unavailable - assume not printing to avoid false triggers
                # Keep last known state if already tracked
                self.logger.debug(f"Printing sensor {self.printing_sensor} is unavailable, assuming not printing")
                printing = False

            # Get current material value if material sensor is configured
            current_material = None
            if self.material_sensor:
                material_state = self.hass.states.get(self.material_sensor)
                if material_state and material_state.state not in (
                    STATE_UNAVAILABLE,
                    STATE_UNKNOWN,
                ):
                    current_material = self._get_material_value(material_state)

            # Handle state transitions - only if we have valid sensor data
            # If sensors are unavailable, we skip updates but keep last known values
            if current_energy is not None:
                if printing and not self.is_printing:
                    # Started printing
                    await self._handle_print_start(current_energy, current_material)
                elif not printing and self.is_printing:
                    # Stopped printing
                    await self._handle_print_stop(current_energy, current_material)
                elif printing and self.is_printing:
                    # Still printing - update current session energy and material
                    if self.session_start_energy is not None:
                        self.current_session_energy = current_energy - self.session_start_energy
                        # Calculate cost for current session energy (convert mm to meters for material)
                        energy_cost_per_kwh = self._get_energy_cost_per_kwh()
                        self.current_session_energy_cost = self.current_session_energy * energy_cost_per_kwh
                    else:
                        self.current_session_energy = 0.0
                        self.current_session_energy_cost = 0.0
                    
                    if self.material_sensor and current_material is not None:
                        if self.session_start_material is not None:
                            self.current_session_material = current_material - self.session_start_material
                            # Material is in mm, convert to meters for cost calculation
                            material_meters = self.current_session_material / 1000.0
                            self.current_session_material_cost = material_meters * self.material_cost_per_meter
                        else:
                            self.current_session_material = 0.0
                            self.current_session_material_cost = 0.0
                    else:
                        self.current_session_material_cost = 0.0
                    
                    # Calculate total current session cost
                    self.current_session_total_cost = self.current_session_energy_cost + self.current_session_material_cost
            else:
                # Energy sensor unavailable - keep last known values, don't update current session
                self.logger.debug("Skipping state transitions due to unavailable energy sensor")

            # Return data - use current_energy if available, otherwise keep last known values
            # This ensures sensors continue to show data even when source sensors are unavailable
            return {
                "is_printing": self.is_printing,
                "current_energy": current_energy if current_energy is not None else (self.total_energy if hasattr(self, 'total_energy') else 0.0),
                "current_session_energy": self.current_session_energy,
                "total_energy": self.total_energy,
                "print_count": self.print_count,
                "last_print_energy": self.last_print_energy,
                "last_print_start": self.last_print_start,
                "last_print_end": self.last_print_end,
                "current_session_material": self.current_session_material,
                "total_material": self.total_material,
                "last_print_material": self.last_print_material,
                "current_session_energy_cost": self.current_session_energy_cost,
                "current_session_material_cost": self.current_session_material_cost,
                "current_session_total_cost": self.current_session_total_cost,
                "last_print_energy_cost": self.last_print_energy_cost,
                "last_print_material_cost": self.last_print_material_cost,
                "last_print_total_cost": self.last_print_total_cost,
                "total_energy_cost": self.total_energy_cost,
                "total_material_cost": self.total_material_cost,
                "total_cost": self.total_cost,
            }

        except Exception as err:
            # Log error but don't raise UpdateFailed - return last known values instead
            # This keeps sensors available showing last known data even when errors occur
            self.logger.warning(f"Error updating printer energy data: {err}, using last known values")
            # Return last known data - all attributes are initialized in __init__ so safe to access
            return {
                "is_printing": self.is_printing,
                "current_energy": self.total_energy,
                "current_session_energy": self.current_session_energy,
                "total_energy": self.total_energy,
                "print_count": self.print_count,
                "last_print_energy": self.last_print_energy,
                "last_print_start": self.last_print_start,
                "last_print_end": self.last_print_end,
                "current_session_material": self.current_session_material,
                "total_material": self.total_material,
                "last_print_material": self.last_print_material,
                "current_session_energy_cost": self.current_session_energy_cost,
                "current_session_material_cost": self.current_session_material_cost,
                "current_session_total_cost": self.current_session_total_cost,
                "last_print_energy_cost": self.last_print_energy_cost,
                "last_print_material_cost": self.last_print_material_cost,
                "last_print_total_cost": self.last_print_total_cost,
                "total_energy_cost": self.total_energy_cost,
                "total_material_cost": self.total_material_cost,
                "total_cost": self.total_cost,
            }

    def _get_energy_value(self, state: State) -> float:
        """Extract energy value from state."""
        # Always use "total_increased" attribute (hardcoded)
        if ENERGY_ATTRIBUTE in state.attributes:
            try:
                return float(state.attributes[ENERGY_ATTRIBUTE])
            except (ValueError, TypeError):
                pass

        # Fallback to state value
        try:
            return float(state.state)
        except (ValueError, TypeError):
            return 0.0

    def _get_material_value(self, state: State) -> float:
        """Extract material value from state."""
        try:
            return float(state.state)
        except (ValueError, TypeError):
            return 0.0

    async def _handle_print_start(self, current_energy: float, current_material: float | None = None) -> None:
        """Handle when printing starts."""
        self.is_printing = True
        self.session_start_energy = current_energy
        self.current_session_energy = 0.0
        self.current_session_energy_cost = 0.0
        self.last_print_start = dt_util.utcnow()
        
        if current_material is not None:
            self.session_start_material = current_material
            self.current_session_material = 0.0
            self.current_session_material_cost = 0.0
        else:
            self.session_start_material = None
            self.current_session_material = 0.0
            self.current_session_material_cost = 0.0
        
        self.current_session_total_cost = 0.0
        
        material_info = f", Material: {current_material:.2f}" if current_material is not None else ""
        self.logger.info(f"Printing started. Energy: {current_energy:.2f}{material_info}")

    async def _handle_print_stop(self, current_energy: float, current_material: float | None = None) -> None:
        """Handle when printing stops."""
        if self.session_start_energy is not None:
            session_energy = current_energy - self.session_start_energy
            if session_energy > 0:
                self.current_session_energy = session_energy
                self.total_energy += session_energy
                self.last_print_energy = session_energy
                self.print_count += 1
                self.last_print_end = dt_util.utcnow()

                # Calculate energy cost
                energy_cost_per_kwh = self._get_energy_cost_per_kwh()
                self.last_print_energy_cost = session_energy * energy_cost_per_kwh
                self.total_energy_cost += self.last_print_energy_cost
                self.current_session_energy_cost = self.last_print_energy_cost

                # Handle material tracking and cost
                if current_material is not None and self.session_start_material is not None:
                    session_material = current_material - self.session_start_material
                    if session_material > 0:
                        self.current_session_material = session_material
                        self.total_material += session_material
                        self.last_print_material = session_material
                        
                        # Calculate material cost (convert mm to meters)
                        material_meters = session_material / 1000.0
                        self.last_print_material_cost = material_meters * self.material_cost_per_meter
                        self.total_material_cost += self.last_print_material_cost
                        self.current_session_material_cost = self.last_print_material_cost
                        self.logger.info(
                            f"Material cost calc: material_mm={session_material}, material_meters={material_meters}, "
                            f"cost_per_meter={self.material_cost_per_meter}, cost={self.last_print_material_cost}"
                        )
                    else:
                        self.current_session_material = 0.0
                        self.last_print_material_cost = 0.0
                        self.current_session_material_cost = 0.0
                else:
                    self.current_session_material = 0.0
                    self.last_print_material_cost = 0.0
                    self.current_session_material_cost = 0.0

                # Calculate total costs
                self.last_print_total_cost = self.last_print_energy_cost + self.last_print_material_cost
                self.total_cost += self.last_print_total_cost
                self.current_session_total_cost = self.last_print_total_cost

                # Save to storage
                await self._save_data()

                material_info = (
                    f", Material: {self.last_print_material:.2f} mm"
                    if self.last_print_material > 0
                    else ""
                )
                cost_info = f", Cost: ${self.last_print_total_cost:.2f}" if self.last_print_total_cost > 0 else ""
                self.logger.info(
                    f"Printing stopped. Session energy: {session_energy:.2f} kWh, "
                    f"Total: {self.total_energy:.2f} kWh{material_info}{cost_info}"
                )

        self.is_printing = False
        self.session_start_energy = None
        self.session_start_material = None

    async def _save_data(self) -> None:
        """Save data to persistent storage."""
        data = {
            "total_energy": self.total_energy,
            "print_count": self.print_count,
            "last_print_energy": self.last_print_energy,
            "last_print_start": (
                self.last_print_start.isoformat() if self.last_print_start else None
            ),
            "last_print_end": (
                self.last_print_end.isoformat() if self.last_print_end else None
            ),
            "total_material": self.total_material,
            "last_print_material": self.last_print_material,
            "total_energy_cost": self.total_energy_cost,
            "total_material_cost": self.total_material_cost,
            "total_cost": self.total_cost,
            "last_print_energy_cost": self.last_print_energy_cost,
            "last_print_material_cost": self.last_print_material_cost,
            "last_print_total_cost": self.last_print_total_cost,
        }
        await self.storage.save(data)

    async def _update_printing_state(self) -> None:
        """Update printing state based on current sensor state.
        
        Handles unavailable sensors gracefully - only updates if sensors are available.
        """
        printing_state = self.hass.states.get(self.printing_sensor)
        if printing_state and printing_state.state not in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            printing_state_value = printing_state.state.lower()
            printing = printing_state_value in self.printing_states
            if printing != self.is_printing:
                energy_state = self.hass.states.get(self.energy_sensor)
                if energy_state and energy_state.state not in (STATE_UNAVAILABLE, STATE_UNKNOWN):
                    current_energy = self._get_energy_value(energy_state)
                    
                    # Get material value if configured
                    current_material = None
                    if self.material_sensor:
                        material_state = self.hass.states.get(self.material_sensor)
                        if material_state and material_state.state not in (
                            STATE_UNAVAILABLE,
                            STATE_UNKNOWN,
                        ):
                            current_material = self._get_material_value(material_state)
                    
                    if printing:
                        await self._handle_print_start(current_energy, current_material)
                    else:
                        await self._handle_print_stop(current_energy, current_material)
                else:
                    # Energy sensor unavailable - skip update but log it
                    self.logger.debug(f"Energy sensor {self.energy_sensor} unavailable, skipping print state transition")
        else:
            # Printing sensor unavailable - skip update but log it
            self.logger.debug(f"Printing sensor {self.printing_sensor} unavailable, skipping print state check")

    @callback
    def _state_listener(self, event: dict) -> None:
        """Handle state change events."""
        entity_id = event.data.get("entity_id")
        tracked_entities = [self.energy_sensor, self.printing_sensor]
        if self.material_sensor:
            tracked_entities.append(self.material_sensor)
        if entity_id in tracked_entities:
            self.hass.async_create_task(self.async_refresh())

    @callback
    def async_setup_listeners(self) -> Callable[[], None]:
        """Set up state change listeners and return cleanup function."""
        remove_listener = self.hass.bus.async_listen("state_changed", self._state_listener)
        self._event_listeners.append(remove_listener)
        return remove_listener

    async def async_reset_data(self) -> None:
        """Reset all accumulated data."""
        self.total_energy = 0.0
        self.total_material = 0.0
        self.print_count = 0
        self.last_print_energy = 0.0
        self.last_print_material = 0.0
        self.last_print_start = None
        self.last_print_end = None
        self.total_energy_cost = 0.0
        self.total_material_cost = 0.0
        self.total_cost = 0.0
        self.last_print_energy_cost = 0.0
        self.last_print_material_cost = 0.0
        self.last_print_total_cost = 0.0
        self.current_session_energy = 0.0
        self.current_session_material = 0.0
        self.current_session_energy_cost = 0.0
        self.current_session_material_cost = 0.0
        self.current_session_total_cost = 0.0
        
        # Save reset state to storage
        await self._save_data()
        
        # Refresh to update sensors
        await self.async_refresh()
        
        self.logger.info("All data has been reset")

    async def async_shutdown(self) -> None:
        """Shutdown coordinator."""
        # Cancel all event listeners
        for remove_listener in self._event_listeners:
            remove_listener()
        self._event_listeners.clear()
