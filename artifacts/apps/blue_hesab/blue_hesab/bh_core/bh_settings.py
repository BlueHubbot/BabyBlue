# -*- coding: utf-8 -*-
"""
Compatibility shim.
Expected import:
  blue_hesab.bh_core.bh_settings.get_bh_settings

Canonical function is in:
  blue_hesab.bh_core.bh_settings_core.get_bh_settings
"""
from .bh_settings_core import get_bh_settings

__all__ = ["get_bh_settings"]
