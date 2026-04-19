import frappe


def execute(filters=None):
	columns=[{"label":"Contract","fieldname":"name","fieldtype":"Link","options":"Leasing Finance Contract","width":180},{"label":"Customer","fieldname":"customer_name","fieldtype":"Data","width":180},{"label":"Lease Type","fieldname":"lease_type","fieldtype":"Data","width":120},{"label":"Principal","fieldname":"principal","fieldtype":"Currency","width":130},{"label":"Liability","fieldname":"lease_liability","fieldtype":"Currency","width":130}]
	data=frappe.get_all("Leasing Finance Contract",fields=["name","customer_name","lease_type","principal","lease_liability"],order_by="modified desc")
	return columns,data
