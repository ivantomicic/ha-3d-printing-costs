"""Constants for Printer Energy Tracker integration."""

from typing import Final

DOMAIN: Final = "printer_energy"
NAME: Final = "Printer Energy Tracker"

# Config flow
CONF_ENERGY_SENSOR: Final = "energy_sensor"
CONF_PRINTER_STATE_SENSOR: Final = "printer_state_sensor"
CONF_PRINTING_STATE_VALUE: Final = "printing_state_value"

# Default values
DEFAULT_PRINTING_STATE: Final = "printing"

# Storage
STORAGE_KEY: Final = f"{DOMAIN}_prints"
STORAGE_VERSION: Final = 1

# Sensor attributes
ATTR_START_TIME: Final = "start_time"
ATTR_END_TIME: Final = "end_time"
ATTR_ENERGY_KWH: Final = "energy_kwh"
ATTR_PRINT_COUNT: Final = "print_count"
ATTR_ACTIVE_PRINT: Final = "active_print"
ATTR_START_ENERGY: Final = "start_energy"
