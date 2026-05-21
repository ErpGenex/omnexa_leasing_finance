# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe
from frappe import _

from omnexa_core.omnexa_core.report_print.report_query_filters import (
	get_all_filters,
	policy_version_filters,
	prepare_filters,
	sql_conditions,
)



def execute(filters=None):
	filters = prepare_filters(filters)
	filters_dict = get_all_filters(filters, "Leasing Finance Risk Snapshot", date_field="creation", company=True, branch=True, extra_links={})
	data = frappe.get_all(
		"Leasing Finance Risk Snapshot",
		fields=['contract_id', 'delinquency_days', 'early_warning_flag'],
		filters=filters_dict,
		limit_page_length=5000,
	)

	return [{"label":"Contract","fieldname":"contract_id","fieldtype":"Link","options":"Leasing Finance Contract","width":180},{"label":"Delinquency Days","fieldname":"delinquency_days","fieldtype":"Int","width":140},{"label":"EWS","fieldname":"early_warning_flag","fieldtype":"Check","width":100}], data
