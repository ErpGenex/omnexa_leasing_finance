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
	filters_dict = get_all_filters(filters, "Leasing Finance Schedule", date_field="creation", company=True, branch=True, extra_links={})
	data = frappe.get_all(
		"Leasing Finance Schedule",
		fields=['contract_id', 'period_no', 'remaining_liability'],
		filters=filters_dict,
		limit_page_length=5000,
	)

	return [{"label":"Contract","fieldname":"contract_id","fieldtype":"Link","options":"Leasing Finance Contract","width":180},{"label":"Period","fieldname":"period_no","fieldtype":"Int","width":80},{"label":"Remaining Liability","fieldname":"remaining_liability","fieldtype":"Currency","width":180}], data
