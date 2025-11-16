# -*- coding: utf-8 -*-
import frappe

site = "baba.bluehesab.ir"
frappe.init(site=site); frappe.connect()

pairs = [
("""By default, the Customer Name is set as per the Full Name entered. If you want Customers to be named by a <a href="https://docs.erpnext.com/docs/user/manual/en/setting-up/settings/naming-series" target="_blank">Naming Series</a>. Choose the Naming
