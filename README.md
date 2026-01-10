# Printer Energy Tracker

A Home Assistant custom integration to track energy consumption per 3D print job.

## Features

- **Automatic Print Detection**: Monitors your printer state sensor to detect when prints start and end
- **Energy Tracking**: Calculates energy consumption (kWh) for each print job using a total energy sensor (e.g., Shelly Plug)
- **Persistent History**: Stores print history across Home Assistant restarts using built-in storage
- **Three Sensors**:
  - `sensor.printer_last_print_energy` - Energy used in the most recent print
  - `sensor.printer_total_print_energy` - Cumulative energy across all prints
  - `sensor.printer_print_count` - Total number of completed prints

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to **Integrations**
3. Click the three dots in the top right and select **Custom repositories**
4. Add this repository URL and select **Integration** as the category
5. Click **Download** and restart Home Assistant
6. Go to **Settings** → **Devices & Services** → **Add Integration**
7. Search for "Printer Energy Tracker"

### Manual Installation

1. Copy the `printer_energy` folder to your `custom_components` directory:
   ```
   <config>/custom_components/printer_energy/
   ```
2. Restart Home Assistant
3. Go to **Settings** → **Devices & Services** → **Add Integration**
4. Search for "Printer Energy Tracker"

## Configuration

### Setup Requirements

1. **Energy Sensor**: A sensor with:
   - Device class: `energy`
   - Unit: `kWh`
   - Must be monotonically increasing (total energy, not power)
   - Examples: Shelly Plug energy sensor, smart plug with energy tracking

2. **Printer State Sensor**: A string-based sensor that indicates printer state
   - Examples: OctoPrint sensor, 3D printer integration state sensor
   - The sensor should have a state value when printing (default: `"printing"`)

### Configuration Steps

1. Add the integration through the UI
2. Select your energy sensor (must be kWh energy sensor)
3. Select your printer state sensor
4. Enter the state value that indicates printing (default: `"printing"`)
   - This is case-insensitive
   - Examples: `"printing"`, `"Printing"`, `"PRINTING"`

## How It Works

### Print Start Detection

When the printer state sensor changes to your configured printing state:
- The current energy sensor value is recorded as `start_energy`
- A timestamp is saved
- The print is marked as active

### Print End Detection

When the printer state changes from the printing state to any other state:
- The current energy sensor value is read
- Energy used is calculated: `end_energy - start_energy`
- The print record is saved with:
  - Start time
  - End time
  - Energy consumed (kWh)
- Active print state is cleared

### Error Handling

The integration handles various edge cases:

- **Unavailable/Unknown States**: Ignored, tracking continues when states become available
- **Negative Energy Deltas**: Detected and logged (e.g., if energy sensor was reset). The print is discarded to prevent invalid data
- **Home Assistant Restart**: Active prints are preserved and tracking continues after restart
- **Energy Sensor Reset**: If a negative delta is detected, the print is discarded with a warning

## Sensors

### `sensor.printer_last_print_energy`

- **Device Class**: Energy
- **Unit**: kWh
- **Attributes**:
  - `start_time`: ISO timestamp of print start
  - `end_time`: ISO timestamp of print end
  - `energy_kwh`: Energy consumed
  - `active_print`: Boolean indicating if a print is currently active
  - `start_energy`: Energy value at print start (if active)

### `sensor.printer_total_print_energy`

- **Device Class**: Energy
- **Unit**: kWh
- **Attributes**:
  - `print_count`: Total number of completed prints

### `sensor.printer_print_count`

- **Device Class**: None
- **Icon**: `mdi:printer-3d`
- **Attributes**:
  - `print_count`: Total number of completed prints
  - `active_print`: Boolean indicating if a print is currently active
  - `start_time`: Start time of active print (if active)
  - `start_energy`: Energy value at print start (if active)

## Limitations

- **Single Printer**: This integration tracks one printer per config entry
- **No Cost Calculation**: Energy tracking only, no cost calculations
- **No UI Panels**: Sensors only, no custom UI

## Troubleshooting

### Print not being detected

- Verify your printer state sensor is updating correctly
- Check that the printing state value matches exactly (case-insensitive)
- Check Home Assistant logs for any errors

### Negative energy detected

- This usually means the energy sensor was reset (counter reset to 0)
- The integration will discard that print to maintain data integrity
- Ensure your energy sensor is a total energy counter (not power)

### Active print after restart

- This is expected behavior if a print was active when HA restarted
- The integration will resume tracking the active print
- If the print has already ended, it will be properly recorded

## Support

For issues, feature requests, or questions:
- Open an issue on GitHub
- Check existing issues first

## License

See LICENSE file for details.
