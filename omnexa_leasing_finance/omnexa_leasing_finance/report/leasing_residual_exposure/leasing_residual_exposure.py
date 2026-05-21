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
		fields=['contract_id', 'residual_exposure', 'asset_risk_score'],
		filters=filters_dict,
		limit_page_length=5000,
	)

	return [{"label":_("Contract"),"fieldname":"contract_id","fieldtype":"Link","options":"Leasing Finance Contract","width":180},{"label":_("Residual Exposure"),"fieldname":"residual_exposure","fieldtype":"Currency","width":180},{"label":_("Risk"),"fieldname":"asset_risk_score","fieldtype":"Float","width":120}], data
