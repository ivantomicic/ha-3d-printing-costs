# Troubleshooting: Integration Not Appearing in Add Integration

If the "Printer Energy Tracker" integration is not appearing when you search in Settings → Devices & Services → Add Integration, try these steps:

## 1. Verify Installation Location

Ensure the integration is installed at:
```
<config>/custom_components/printer_energy/
```

Where `<config>` is your Home Assistant configuration directory.

## 2. Check Required Files

Verify these files exist:
- `custom_components/printer_energy/manifest.json`
- `custom_components/printer_energy/__init__.py`
- `custom_components/printer_energy/config_flow.py`
- `custom_components/printer_energy/const.py`

## 3. Full Home Assistant Restart

**Critical**: After installing via HACS, you MUST perform a **full restart** of Home Assistant (not just reload):
- Go to Settings → System → Hardware → Restart
- Or restart from Supervisor/HA OS if applicable

## 4. Clear Browser Cache

- Hard refresh: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
- Or clear browser cache completely

## 5. Check Home Assistant Logs

1. Go to Settings → System → Logs
2. Look for errors containing "printer_energy" or "Printer Energy Tracker"
3. Common errors:
   - Import errors
   - Missing dependencies
   - Syntax errors

## 6. Verify Search Terms

Try searching for:
- "printer energy" (partial match)
- "printer_energy" (domain name)
- Just "energy" (broader search)

## 7. Manual Verification

Check if the integration loaded:
1. Go to Developer Tools → YAML
2. Check if you see any errors related to printer_energy

## 8. Reinstall via HACS

1. Remove the integration from HACS
2. Restart Home Assistant
3. Reinstall via HACS
4. Restart Home Assistant again

## 9. Manual Installation Test

If HACS installation fails, try manual installation:
1. Copy the entire `printer_energy` folder to `custom_components/`
2. Ensure file permissions are correct
3. Restart Home Assistant

## Common Issues

### Integration appears but shows error
- Check logs for specific error messages
- Verify all dependencies are met
- Check Python version compatibility

### Integration doesn't appear at all
- Most likely: Home Assistant wasn't fully restarted
- Check manifest.json is valid JSON
- Verify config_flow.py has no syntax errors
- Ensure domain name matches folder name exactly
