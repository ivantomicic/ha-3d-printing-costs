"""The Printer Energy integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

from .const import DOMAIN
from .coordinator import PrinterEnergyCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BUTTON, Platform.NUMBER, Platform.SELECT]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Printer Energy from a config entry."""
    # Merge options with data (options override data)
    config = {**entry.data}
    if entry.options:
        config.update(entry.options)
    
    hass.data.setdefault(DOMAIN, {})
    
    # Check if coordinator already exists (on reload)
    existing_coordinator = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if existing_coordinator and isinstance(existing_coordinator, PrinterEnergyCoordinator):
        # Update cost config if currency/cost settings changed
        existing_coordinator._update_cost_config(config)
        coordinator = existing_coordinator
    else:
        # Create coordinator with entry_id for per-instance storage
        coordinator = PrinterEnergyCoordinator(hass, config, entry.entry_id)
        hass.data[DOMAIN][entry.entry_id] = coordinator
        
        # Set up listeners first, before first refresh
        remove_listener = coordinator.async_setup_listeners()
        entry.async_on_unload(remove_listener)
        
        await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)

async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry."""
    version = config_entry.version
    
    # Migration from version 1 to 2: Add currency if missing
    if version == 1:
        from .const import CONF_CURRENCY, DEFAULT_CURRENCY
        
        new_data = {**config_entry.data}
        if CONF_CURRENCY not in new_data:
            new_data[CONF_CURRENCY] = DEFAULT_CURRENCY
        
        hass.config_entries.async_update_entry(config_entry, data=new_data, version=2)
        version = 2
    
    # Migration from version 2 to 3: Migrate old shared storage to per-entry storage
    if version == 2:
        from .const import DOMAIN, STORAGE_KEY, STORAGE_VERSION
        from homeassistant.helpers.storage import Store
        
        # Try to load old shared storage and migrate to new entry-specific storage
        old_store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        old_data = await old_store.async_load()
        
        if old_data:
            # Migrate to entry-specific storage
            from .storage import PrinterEnergyStorage
            new_storage = PrinterEnergyStorage(hass, config_entry.entry_id)
            await new_storage.save(old_data)
            # Note: We don't delete old storage here to allow other instances to migrate
        
        hass.config_entries.async_update_entry(config_entry, version=3)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    coordinator: PrinterEnergyCoordinator = hass.data[DOMAIN][entry.entry_id]
    await coordinator.async_shutdown()

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
