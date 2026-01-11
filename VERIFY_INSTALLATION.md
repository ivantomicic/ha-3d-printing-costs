# Verify Integration Installation

Since you see **NO logs** when searching, this means Home Assistant isn't discovering the integration at all. Follow these steps:

## Step 1: Verify Installation Location

**CRITICAL**: Check that the integration is installed at:

```
<config>/custom_components/printer_energy/
```

Where `<config>` is your Home Assistant configuration directory.

Common locations:

-   **Home Assistant OS**: `/config/custom_components/printer_energy/`
-   **Docker**: Check your Docker volume mount path
-   **HACS installed**: Should be `/config/custom_components/printer_energy/`

**Verify files exist:**

-   `manifest.json` ✅
-   `__init__.py` ✅
-   `config_flow.py` ✅
-   `const.py` ✅

## Step 2: Check Home Assistant Logs on Startup

1. Go to **Settings → System → Logs**
2. **Filter by**: `printer_energy` or `custom_components`
3. **Restart Home Assistant** (full restart)
4. **Immediately check logs** - look for:
    - Any errors containing "printer_energy"
    - Any errors about "custom_components"
    - Import errors
    - Syntax errors

**Expected**: You should see something, even if it's an error.

## Step 3: Manual File Verification

If you have SSH/terminal access to your Home Assistant:

```bash
# Check if files exist
ls -la /config/custom_components/printer_energy/

# Check manifest.json
cat /config/custom_components/printer_energy/manifest.json

# Check Python syntax
python3 -m py_compile /config/custom_components/printer_energy/*.py
```

## Step 4: Check HACS Installation

1. Go to **HACS → Integrations**
2. Look for "Printer Energy Tracker"
3. Check status:
    - Is it listed?
    - What version shows?
    - Does it say "Installed"?
    - Try clicking "Reinstall" if available

## Step 5: Test Manual Installation

If HACS isn't working:

1. **Remove from HACS** (if installed via HACS)
2. **Manually copy** the `printer_energy` folder to:
    ```
    <config>/custom_components/printer_energy/
    ```
3. **Ensure file permissions** are correct (readable)
4. **Full restart** Home Assistant
5. **Check logs** again

## Step 6: Check Home Assistant Version

This integration requires **Home Assistant 2023.1.0 or later**.

1. Go to **Settings → System → About**
2. Check your Home Assistant version
3. If older than 2023.1.0, update Home Assistant first

## Common Issues

### Files not in correct location

**Symptom**: No logs, integration doesn't appear
**Solution**: Verify exact path matches `<config>/custom_components/printer_energy/`

### HACS installation incomplete

**Symptom**: Shows in HACS but not discoverable
**Solution**: Try manual installation or reinstall via HACS

### Import errors preventing discovery

**Symptom**: No logs, silent failure
**Solution**: Check logs for Python import errors

### Version incompatibility

**Symptom**: Integration doesn't appear in search
**Solution**: Update Home Assistant to 2023.1.0 or later
