"""Helper functions for Printer Energy integration."""

from __future__ import annotations

import re


def slugify_device_name(name: str) -> str:
    """Convert device name to a valid entity ID slug.
    
    Example: "K2 Pro Cost Tracker" -> "k2_pro_cost_tracker"
    """
    if not name:
        return "printer_energy"
    
    # Convert to lowercase
    slug = name.lower()
    # Replace spaces and hyphens with underscores
    slug = slug.replace(" ", "_").replace("-", "_")
    # Remove special characters, keep only alphanumeric and underscores
    slug = re.sub(r"[^a-z0-9_]", "", slug)
    # Remove consecutive underscores
    slug = re.sub(r"_+", "_", slug)
    # Remove leading/trailing underscores
    slug = slug.strip("_")
    # Ensure it's not empty
    if not slug:
        slug = "printer_energy"
    return slug
