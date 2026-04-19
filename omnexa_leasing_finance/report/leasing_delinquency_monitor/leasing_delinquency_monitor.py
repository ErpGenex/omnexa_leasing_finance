import frappe


def execute(filters=None):
	columns=[{"label":"Contract","fieldname":"contract_id","fieldtype":"Link","options":"Leasing Finance Contract","width":180},{"label":"Delinquency Days","fieldname":"delinquency_days","fieldtype":"Int","width":140},{"label":"EWS","fieldname":"early_warning_flag","fieldtype":"Check","width":100}]
	data=frappe.get_all("Leasing Finance Risk Snapshot",fields=["contract_id","delinquency_days","early_warning_flag"],order_by="delinquency_days desc")
	return columns,data
