from __future__ import annotations
import frappe

def get_bh_settings():
    """برگشت Singleton تنظیمات BlueHesab."""
    return frappe.get_single("BH Settings")
