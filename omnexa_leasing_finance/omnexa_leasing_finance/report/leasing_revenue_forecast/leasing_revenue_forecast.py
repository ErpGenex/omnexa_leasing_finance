# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe
from frappe import _

from omnexa_core.omnexa_core.report_print.report_query_filters import prepare_filters, sql_conditions


def execute(filters=None):
	columns = [
		{"label": _("Due Date"), "fieldname": "due_date", "fieldtype": "Date", "width": 120},
		{"label": _("Contracts"), "fieldname": "contracts", "fieldtype": "Int", "width": 100},
		{"label": _("Projected Revenue"), "fieldname": "revenue", "fieldtype": "Currency", "width": 160},
	]
	filters = prepare_filters(filters)
	conditions, params = sql_conditions(
		filters,
		"Leasing Finance Schedule",
		date_field="due_date",
		company=True,
		branch=False,
	)
	rows = frappe.db.sql(
		f"""
		SELECT
			due_date,
			COUNT(DISTINCT contract_id) AS contracts,
			SUM(IFNULL(interest_component, 0)) AS revenue
		FROM `tabLeasing Finance Schedule`
		WHERE {' AND '.join(conditions)}
		GROUP BY due_date
		ORDER BY due_date
		""",
		params,
		as_dict=True,
	)
	return columns, rows
