import frappe


def execute(filters=None):
	columns=[{"label":"Contract","fieldname":"contract_id","fieldtype":"Link","options":"Leasing Finance Contract","width":180},{"label":"Period","fieldname":"period_no","fieldtype":"Int","width":80},{"label":"Remaining Liability","fieldname":"remaining_liability","fieldtype":"Currency","width":180}]
	data=frappe.get_all("Leasing Finance Schedule",fields=["contract_id","period_no","remaining_liability"],order_by="contract_id asc, period_no asc")
	return columns,data
