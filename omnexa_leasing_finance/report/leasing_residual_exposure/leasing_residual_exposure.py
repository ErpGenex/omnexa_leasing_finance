import frappe


def execute(filters=None):
	columns=[{"label":"Contract","fieldname":"contract_id","fieldtype":"Link","options":"Leasing Finance Contract","width":180},{"label":"Residual Exposure","fieldname":"residual_exposure","fieldtype":"Currency","width":180},{"label":"Risk","fieldname":"asset_risk_score","fieldtype":"Float","width":120}]
	data=frappe.get_all("Leasing Finance Risk Snapshot",fields=["contract_id","residual_exposure","asset_risk_score"],order_by="residual_exposure desc")
	return columns,data
