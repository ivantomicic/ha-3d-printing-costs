# Debugging Steps for Integration Not Appearing

## 1. Check Home Assistant Logs

Go to **Settings → System → Logs** and look for:

**GOOD signs (integration is loading):**
```
Printer Energy Tracker integration loaded
```

**BAD signs (integration has errors):**
```
Error loading integration printer_energy
ModuleNotFoundError
ImportError
SyntaxError
```

## 2. Verify Installation Location

The integration MUST be at:
```
<config>/custom_components/printer_energy/
```

Common locations:
- **Home Assistant OS**: `/config/custom_components/printer_energy/`
- **Docker**: `<your-config-path>/custom_components/printer_energy/`
- **HACS installed**: Usually `/config/custom_components/printer_energy/`

## 3. Try Different Search Terms

In **Settings → Devices & Services → Add Integration**, try searching for:

1. `printer` (partial match)
2. `printer energy` (two words)
3. `printer_energy` (domain name with underscore)
4. `energy` (single word)
5. Just browse the list manually if available

## 4. Verify Files Exist

Check that these files exist:
- ✅ `custom_components/printer_energy/manifest.json`
- ✅ `custom_components/printer_energy/__init__.py`
- ✅ `custom_components/printer_energy/config_flow.py`
- ✅ `custom_components/printer_energy/const.py`

## 5. Check Manifest.json Content

The manifest.json should contain:
```json
{
  "domain": "printer_energy",
  "name": "Printer Energy Tracker",
  "config_flow": true,
  "version": "1.0.0"
}
```

## 6. Manual Verification via Developer Tools

1. Go to **Developer Tools → YAML**
2. Check if there are any errors in the configuration
3. Look for any mentions of `printer_energy`

## 7. Clear All Caches

1. Restart Home Assistant (full restart, not reload)
2. Clear browser cache (Ctrl+Shift+Delete or Cmd+Shift+Delete)
3. Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
4. Try incognito/private browsing mode

## 8. Check HACS Installation

If installed via HACS:
1. Go to HACS → Integrations
2. Verify "Printer Energy Tracker" is listed and shows as "Installed"
3. Check the version matches (should be 1.0.0)
4. Try "Reinstall" if available

## 9. Manual Installation Test

If HACS doesn't work, try manual installation:
1. Download/copy the `printer_energy` folder
2. Place it in `custom_components/` directory
3. Ensure file permissions are correct (readable)
4. Restart Home Assistant

## 10. Check Home Assistant Version

This integration requires Home Assistant 2023.1.0 or later. Check your version:
- Go to **Settings → System → About**
- Verify version is 2023.1.0 or newer

## Common Issues and Solutions

### Issue: Integration shows in HACS but not in Add Integration
**Solution**: Full restart required after HACS installation

### Issue: Search returns no results
**Solution**: Try searching for just "printer" or browse manually

### Issue: Error in logs about missing module
**Solution**: Check all dependencies are installed, verify Python version

### Issue: Integration appears but shows error when adding
**Solution**: Check logs for specific error message about validation
