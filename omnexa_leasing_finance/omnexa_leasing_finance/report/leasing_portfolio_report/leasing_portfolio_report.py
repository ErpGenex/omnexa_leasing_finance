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
	filters_dict = get_all_filters(filters, "Leasing Finance Contract", date_field="creation", company=True, branch=True, extra_links={})
	data = frappe.get_all(
		"Leasing Finance Contract",
		fields=['name', 'customer_name', 'lease_type', 'principal', 'lease_liability'],
		filters=filters_dict,
		limit_page_length=5000,
	)

	return [{"label":"Contract","fieldname":"name","fieldtype":"Link","options":"Leasing Finance Contract","width":180},{"label":"Customer","fieldname":"customer_name","fieldtype":"Data","width":180},{"label":"Lease Type","fieldname":"lease_type","fieldtype":"Data","width":120},{"label":"Principal","fieldname":"principal","fieldtype":"Currency","width":130},{"label":"Liability","fieldname":"lease_liability","fieldtype":"Currency","width":130}], data
