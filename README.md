# 3D Printer Cost Tracker

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/ivans-ha-stuff/ha-3d-printing-costs.svg)](https://github.com/ivans-ha-stuff/ha-3d-printing-costs/releases)

A comprehensive Home Assistant integration for tracking energy consumption, material usage, and costs for your 3D printer. This integration monitors your printer's energy usage and material consumption during printing sessions and calculates the associated costs.

**By Ivan's HA Stuff**

## Features

-   **⚡ Energy Tracking**: Tracks energy consumption from any energy sensor (Shelly Plug, smart plugs, etc.)
-   **📊 Material Tracking**: Optional tracking of filament usage during prints
-   **💰 Cost Calculation**: Automatic cost calculation for both energy and material
-   **🎯 Smart Print Detection**: Supports multiple printing states (self-check, printing, etc.)
-   **💾 Persistent Storage**: All data persists across Home Assistant restarts
-   **📈 Comprehensive Sensors**: 8+ sensors tracking energy, material, costs, and statistics
-   **🔧 Easy Configuration**: Simple setup wizard with options for customization

## Installation

### HACS (Recommended)

1. Make sure [HACS](https://hacs.xyz/) is installed in your Home Assistant instance
2. In HACS, go to **Integrations**
3. Click the **⋮** (three dots) in the top right corner
4. Select **Custom repositories**
5. Add this repository URL: `https://github.com/ivans-ha-stuff/ha-3d-printing-costs`
6. Select category: **Integration**
7. Click **Add**
8. Search for **"3D Printer Cost Tracker"** in HACS
9. Click **Download**
10. Restart Home Assistant

### Manual Installation

1. Download the latest release from the [Releases](https://github.com/ivans-ha-stuff/ha-3d-printing-costs/releases) page
2. Extract the `printer_energy` folder from the `custom_components` directory
3. Copy the `printer_energy` folder to your Home Assistant `custom_components` directory:
    ```
    config/custom_components/printer_energy/
    ```
4. Restart Home Assistant
5. Go to **Settings** → **Devices & Services** → **Add Integration**
6. Search for **"3D Printer Cost Tracker"**

## Configuration

### Initial Setup

1. Go to **Settings** → **Devices & Services** → **Add Integration**
2. Search for **"3D Printer Cost Tracker"**
3. Fill in the configuration:
    - **Name**: Friendly name for this tracker (default: "3D Printer Cost Tracker")
    - **Energy Sensor**: Select your energy sensor (e.g., `sensor.shelly_plug_s_energy`)
    - **Energy Attribute**: Attribute containing energy value (default: `total_increased` for Shelly)
    - **Printing Sensor**: Select sensor that indicates printing status (e.g., `binary_sensor.octoprint_printing`)
    - **Printing State**: Comma-separated states indicating printing (default: `on,printing,self-check`)
    - **Material Sensor** (optional): Select sensor tracking filament usage (e.g., `sensor.creality_k1c_used_material_length`)
    - **Energy Cost per kWh**: Your electricity rate (default: `9`)
    - **Material Cost per Spool**: Cost of one spool (e.g., `25.00`)
    - **Spool Length (meters)**: Length of filament per spool (default: `330`)
4. Click **Submit**

### Finding Your Sensors

#### Energy Sensor

-   **Shelly Plug S**: `sensor.shelly_plug_s_<device_id>_energy` with attribute `total_increased`
-   **Other devices**: Look for sensors with device class `energy` or cumulative energy consumption

#### Printing Sensor

-   **OctoPrint**: `binary_sensor.octoprint_printing`
-   **Custom template**: Any binary sensor that turns ON when printing
-   **Multiple states**: Use comma-separated values like `self-check,printing` to track from self-check through printing

#### Material Sensor (Optional)

-   **OctoPrint**: Material usage sensors
-   **Creality K1C**: `sensor.creality_k1c_used_material_length`
-   Any sensor tracking cumulative material/filament length in millimeters

### Options Configuration

You can reconfigure settings after installation:

1. Go to **Settings** → **Devices & Services**
2. Find your **3D Printer Cost Tracker** integration
3. Click on it → **Options**
4. Modify:
    - **Energy Attribute**: Attribute name for energy readings
    - **Printing State**: States that indicate printing (comma-separated)
    - **Material Sensor**: Change material tracking sensor
    - **Energy Cost per kWh**: Update electricity rate
    - **Material Cost per Spool**: Update spool cost
    - **Spool Length**: Update spool length if using different filament

## Sensors

The integration creates the following sensors:

### Energy Sensors

-   **`sensor.<name>_total_energy`**: Total energy consumed across all prints (kWh)
-   **`sensor.<name>_current_session_energy`**: Current print session energy (kWh)
-   **`sensor.<name>_last_print_energy`**: Energy consumed in last print (kWh)

### Material Sensors (if material sensor configured)

-   **`sensor.<name>_last_print_material`**: Material used in last print (mm)

### Cost Sensors

-   **`sensor.<name>_last_print_cost`**: Total cost of last print ($)
-   **`sensor.<name>_total_cost`**: Cumulative cost across all prints ($)

### Statistics Sensors

-   **`sensor.<name>_print_count`**: Total number of completed prints

### Sensor Attributes

All sensors include comprehensive attributes with:

-   Print timestamps (start/end)
-   Energy and material breakdowns
-   Cost breakdowns (energy cost, material cost, total cost)
-   Current session information (if printing)
-   Total statistics

## How It Works

1. **Print Start**: When the printing sensor enters any configured printing state (e.g., "self-check"), the integration:

    - Records current energy reading
    - Records current material reading (if configured)
    - Starts tracking

2. **During Print**: Continuously monitors:

    - Energy consumption changes
    - Material usage changes
    - Calculates real-time costs

3. **Print End**: When printing state changes to non-printing:

    - Calculates energy difference
    - Calculates material difference
    - Calculates costs (energy + material)
    - Saves all data to persistent storage
    - Updates total statistics

4. **Persistence**: All data is saved to Home Assistant storage and survives restarts

## Cost Calculation

### Energy Cost

```
Energy Cost = Energy (kWh) × Cost per kWh
```

### Material Cost

```
Material Cost = (Material (mm) / 1000) × Cost per Meter
Cost per Meter = Cost per Spool / Spool Length (meters)
```

### Total Cost

```
Total Cost = Energy Cost + Material Cost
```

**Example:**

-   Spool Cost: $25.00
-   Spool Length: 330 meters
-   Cost per Meter: $25.00 / 330 = $0.0758/meter
-   Print uses: 5000mm (5 meters) = $0.38
-   Energy: 0.5 kWh at $9/kWh = $0.06
-   **Total Print Cost: $0.44**

## Example Automations

### Notify When Print Completes with Costs

```yaml
automation:
    - alias: "Notify Print Complete with Costs"
      trigger:
          - platform: state
            entity_id: binary_sensor.printer_printing
            to: "off"
      action:
          - service: notify.mobile_app
            data:
                title: "Print Complete!"
                message: >
                    Energy: {{ states('sensor.printer_energy_tracker_last_print_energy') }} kWh
                    Material: {{ states('sensor.printer_energy_tracker_last_print_material') }} mm
                    Cost: ${{ states('sensor.printer_energy_tracker_last_print_cost') }}
```

### Track Monthly Costs

```yaml
template:
    - sensor:
          - name: "3D Printer Monthly Cost"
            unit_of_measurement: "$"
            state: >
                {% set total = states('sensor.printer_energy_tracker_total_cost') | float(0) %}
                {% set current_month = now().month %}
                {% set last_reset = state_attr('sensor.printer_energy_tracker_total_cost', 'last_reset') %}
                {% if last_reset %}
                  {% set reset_month = last_reset | as_timestamp | timestamp_custom('%m', True) | int(0) %}
                  {% if reset_month == current_month %}
                    {{ total }}
                  {% else %}
                    0.0
                  {% endif %}
                {% else %}
                  {{ total }}
                {% endif %}
```

## Troubleshooting

### Energy readings are always 0

-   ✅ Verify energy sensor provides cumulative values (not instantaneous power)
-   ✅ Check "Energy Attribute" matches your device (try `total_increased` for Shelly)
-   ✅ Some devices use state value directly (leave attribute blank or use device state)

### Print count not incrementing

-   ✅ Verify printing sensor changes state correctly
-   ✅ Check "Printing State" includes all states (e.g., `self-check,printing`)
-   ✅ Ensure sensor transitions properly (use Developer Tools → States to verify)

### Material tracking not working

-   ✅ Verify material sensor is configured
-   ✅ Check material sensor reports cumulative values (not resetting)
-   ✅ Material sensor should report in millimeters (mm)

### Costs showing as 0

-   ✅ Verify cost per kWh is configured (default: 9)
-   ✅ Verify material cost per spool is configured if tracking material
-   ✅ Check spool length matches your filament type

### Data not persisting

-   ✅ Check Home Assistant logs for storage errors
-   ✅ Verify write permissions in config directory
-   ✅ Ensure integration is properly installed (check `custom_components/printer_energy/` exists)

## Updating

### Via HACS

1. Go to HACS → Integrations
2. Find "3D Printer Cost Tracker"
3. Click **Update** if available
4. Restart Home Assistant

### Manual Update

1. Download latest release
2. Replace `custom_components/printer_energy` folder
3. Restart Home Assistant
4. Your data will be preserved

## Breaking Changes

### Version 1.0.0

-   Initial release with energy, material, and cost tracking

## Support

-   🐛 **Bug Reports**: [GitHub Issues](https://github.com/ivans-ha-stuff/ha-3d-printing-costs/issues)
-   💡 **Feature Requests**: [GitHub Issues](https://github.com/ivans-ha-stuff/ha-3d-printing-costs/issues)
-   📧 **Questions**: Open a discussion on GitHub

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Credits

**Ivan's HA Stuff** - Custom Home Assistant Integrations

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Made with ❤️ for the Home Assistant community**
