"""Constants for the Printer Energy integration."""

DOMAIN = "printer_energy"
STORAGE_KEY = f"{DOMAIN}.storage"
STORAGE_VERSION = 1

CONF_ENERGY_SENSOR = "energy_sensor"
CONF_PRINTING_SENSOR = "printing_sensor"
CONF_PRINTING_STATE = "printing_state"
CONF_ENERGY_ATTRIBUTE = "energy_attribute"
CONF_MATERIAL_SENSOR = "material_sensor"
CONF_ENERGY_COST_PER_KWH = "energy_cost_per_kwh"
CONF_MATERIAL_COST_PER_SPOOL = "material_cost_per_spool"
CONF_MATERIAL_SPOOL_LENGTH = "material_spool_length"

DEFAULT_PRINTING_STATE = "on,printing,self-check"
DEFAULT_ENERGY_ATTRIBUTE = "total_increased"
DEFAULT_ENERGY_COST = 0.12  # $0.12 per kWh (common default)
DEFAULT_MATERIAL_COST_PER_SPOOL = 0.0  # No default, user must configure
DEFAULT_SPOOL_LENGTH = 330.0  # 330 meters per spool (common default)

ATTR_CURRENT_SESSION_ENERGY = "current_session_energy"
ATTR_TOTAL_ENERGY = "total_energy"
ATTR_PRINT_COUNT = "print_count"
ATTR_LAST_PRINT_ENERGY = "last_print_energy"
ATTR_LAST_PRINT_START = "last_print_start"
ATTR_LAST_PRINT_END = "last_print_end"
ATTR_CURRENT_SESSION_MATERIAL = "current_session_material"
ATTR_LAST_PRINT_MATERIAL = "last_print_material"
ATTR_TOTAL_MATERIAL = "total_material"
ATTR_LAST_PRINT_ENERGY_COST = "last_print_energy_cost"
ATTR_LAST_PRINT_MATERIAL_COST = "last_print_material_cost"
ATTR_LAST_PRINT_TOTAL_COST = "last_print_total_cost"
ATTR_CURRENT_SESSION_ENERGY_COST = "current_session_energy_cost"
ATTR_CURRENT_SESSION_MATERIAL_COST = "current_session_material_cost"
ATTR_CURRENT_SESSION_TOTAL_COST = "current_session_total_cost"
ATTR_TOTAL_ENERGY_COST = "total_energy_cost"
ATTR_TOTAL_MATERIAL_COST = "total_material_cost"
ATTR_TOTAL_COST = "total_cost"

SENSOR_TOTAL_ENERGY = "total_energy"
SENSOR_CURRENT_SESSION = "current_session"
SENSOR_PRINT_COUNT = "print_count"
SENSOR_LAST_PRINT_ENERGY = "last_print_energy"
SENSOR_LAST_PRINT_MATERIAL = "last_print_material"
SENSOR_LAST_PRINT_COST = "last_print_cost"
SENSOR_TOTAL_COST = "total_cost"
