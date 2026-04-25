import frappe


def execute(filters=None):
	columns=[{"label":"Due Date","fieldname":"due_date","fieldtype":"Date","width":120},{"label":"Contracts","fieldname":"contracts","fieldtype":"Int","width":100},{"label":"Projected Revenue","fieldname":"revenue","fieldtype":"Currency","width":160}]
	data=frappe.db.sql("select due_date, count(distinct contract_id) as contracts, sum(ifnull(interest_component,0)) as revenue from `tabLeasing Finance Schedule` group by due_date order by due_date",as_dict=True)
	return columns,data
