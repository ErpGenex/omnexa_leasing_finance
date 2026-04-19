from __future__ import annotations

import frappe


def maker_checker_pqc(user: str | None = None) -> str:
	usr = user or frappe.session.user
	return f"(owner={frappe.db.escape(usr)})"


def has_maker_checker_permission(doc, user: str | None = None) -> bool:
	usr = user or frappe.session.user
	roles = set(frappe.get_roles(usr) or [])
	return bool(roles & {"System Manager", "Risk Manager", "Compliance Manager"}) or getattr(doc, "owner", None) == usr
