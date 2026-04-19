from __future__ import annotations

import json
from datetime import date, timedelta
from decimal import Decimal

import frappe

from .engine import LeaseCase, evaluate_lease_case
from .standards_profile import get_standards_profile as _get_standards_profile


@frappe.whitelist()
def get_standards_profile() -> dict:
	return _get_standards_profile()


@frappe.whitelist()
def evaluate_lease(principal: str, term_months: int, lease_type: str = "FINANCE", discount_rate: str = "0.08", residual_value: str = "0") -> dict:
	case = LeaseCase(principal=Decimal(str(principal)), term_months=int(term_months), lease_type=lease_type, discount_rate=Decimal(str(discount_rate)), residual_value=Decimal(str(residual_value)))
	return evaluate_lease_case(case).to_dict()


@frappe.whitelist()
def upsert_lease_contract(case_id: str | None = None, customer_name: str | None = None, lease_type: str = "FINANCE", principal: str = "0", term_months: int = 0, discount_rate: str = "0.08", rate_type: str = "FIXED", residual_value: str = "0", currency: str = "USD", country_code: str = "INTL", sector_risk_band: str = "MEDIUM") -> dict:
	assessment = evaluate_lease_case(LeaseCase(principal=Decimal(str(principal)), term_months=int(term_months), lease_type=lease_type, discount_rate=Decimal(str(discount_rate)), residual_value=Decimal(str(residual_value)), rate_type=rate_type, sector_risk_band=sector_risk_band)).to_dict()
	doc = frappe.get_doc("Leasing Finance Contract", case_id) if case_id and frappe.db.exists("Leasing Finance Contract", case_id) else frappe.new_doc("Leasing Finance Contract")
	doc.customer_name = customer_name or "Unknown Customer"
	doc.lease_type = lease_type
	doc.principal = Decimal(str(principal))
	doc.term_months = int(term_months)
	doc.discount_rate = Decimal(str(discount_rate))
	doc.rate_type = rate_type
	doc.currency = currency
	doc.country_code = country_code
	doc.residual_value = Decimal(str(residual_value))
	doc.rou_asset = Decimal(str(assessment.get("rou_asset", "0")))
	doc.lease_liability = Decimal(str(assessment.get("lease_liability", "0")))
	doc.periodic_payment = Decimal(str(assessment.get("periodic_payment", "0")))
	doc.lifecycle_stage = "CONTRACT"
	doc.ifrs9_stage = assessment.get("ifrs9_stage")
	doc.risk_score = float(Decimal(str(assessment.get("risk_score", "0"))))
	doc.pricing_spread = float(Decimal(str(assessment.get("pricing_spread", "0"))))
	doc.decision_reason_codes = ",".join(assessment.get("reason_codes", []))
	doc.required_controls = ",".join(assessment.get("required_controls", []))
	doc.save(ignore_permissions=True)
	return {"contract_id": doc.name, "assessment": assessment}


@frappe.whitelist()
def register_lease_asset(contract_id: str, asset_tag: str, asset_type: str, acquisition_value: str, residual_value: str = "0", insurance_policy_no: str | None = None) -> dict:
	doc = frappe.get_doc({"doctype": "Leasing Finance Asset", "contract_id": contract_id, "asset_tag": asset_tag, "asset_type": asset_type, "acquisition_value": Decimal(str(acquisition_value)), "residual_value": Decimal(str(residual_value)), "valuation_amount": Decimal(str(acquisition_value)), "insurance_policy_no": insurance_policy_no, "asset_status": "ACTIVE"})
	doc.insert(ignore_permissions=True)
	return {"asset_id": doc.name}


@frappe.whitelist()
def generate_lease_schedule(contract_id: str) -> dict:
	contract = frappe.get_doc("Leasing Finance Contract", contract_id)
	term = int(contract.term_months or 0)
	balance = Decimal(str(contract.lease_liability or 0))
	pay = Decimal(str(contract.periodic_payment or 0))
	rate = Decimal(str(contract.discount_rate or 0)) / Decimal("12")
	count = 0
	for i in range(1, term + 1):
		interest = balance * rate
		principal = pay - interest
		if i == term:
			principal = balance
			pay = principal + interest
		balance = max(Decimal("0"), balance - principal)
		doc = frappe.get_doc({"doctype": "Leasing Finance Schedule", "contract_id": contract_id, "period_no": i, "due_date": str(date.today() + timedelta(days=30 * i)), "principal_component": principal, "interest_component": interest, "payment_amount": pay, "remaining_liability": balance, "status": "PLANNED"})
		doc.insert(ignore_permissions=True)
		count += 1
	return {"contract_id": contract_id, "schedule_rows": count}


@frappe.whitelist()
def record_lease_payment(contract_id: str, payment_amount: str, schedule_id: str | None = None) -> dict:
	p = frappe.get_doc({"doctype": "Leasing Finance Payment", "contract_id": contract_id, "schedule_id": schedule_id, "payment_date": str(date.today()), "payment_amount": Decimal(str(payment_amount)), "payment_status": "POSTED"})
	p.insert(ignore_permissions=True)
	if schedule_id and frappe.db.exists("Leasing Finance Schedule", schedule_id):
		s = frappe.get_doc("Leasing Finance Schedule", schedule_id)
		s.status = "PAID"
		s.save(ignore_permissions=True)
	return {"payment_id": p.name}


@frappe.whitelist()
def post_ifrs16_entries(contract_id: str) -> dict:
	contract = frappe.get_doc("Leasing Finance Contract", contract_id)
	entries = []
	for entry_type, amount in [
		("INITIAL_RECOGNITION", Decimal(str(contract.lease_liability or 0))),
		("DEPRECIATION", Decimal(str(contract.rou_asset or 0)) / Decimal(max(1, int(contract.term_months or 1)))),
		("INTEREST_EXPENSE", Decimal(str(contract.lease_liability or 0)) * (Decimal(str(contract.discount_rate or 0)) / Decimal("12"))),
	]:
		doc = frappe.get_doc({"doctype": "Leasing Finance Accounting Entry", "contract_id": contract_id, "entry_date": str(date.today()), "entry_type": entry_type, "debit_account": "Lease Expense", "credit_account": "Lease Liability", "amount": amount, "currency": contract.currency or "USD"})
		doc.insert(ignore_permissions=True)
		entries.append(doc.name)
	return {"posted_entries": entries}


@frappe.whitelist()
def apply_contract_modification(contract_id: str, modification_type: str, new_terms_json: str, remeasurement_impact: str = "0") -> dict:
	contract = frappe.get_doc("Leasing Finance Contract", contract_id)
	old = {"term_months": contract.term_months, "discount_rate": str(contract.discount_rate), "periodic_payment": str(contract.periodic_payment)}
	new_terms = json.loads(new_terms_json) if isinstance(new_terms_json, str) else (new_terms_json or {})
	if "term_months" in new_terms:
		contract.term_months = int(new_terms["term_months"])
	if "discount_rate" in new_terms:
		contract.discount_rate = Decimal(str(new_terms["discount_rate"]))
	contract.lifecycle_stage = "MODIFICATION"
	contract.save(ignore_permissions=True)
	log = frappe.get_doc({"doctype": "Leasing Finance Modification Log", "contract_id": contract_id, "modification_date": str(date.today()), "modification_type": modification_type, "old_terms_json": json.dumps(old), "new_terms_json": json.dumps(new_terms), "remeasurement_impact": Decimal(str(remeasurement_impact))})
	log.insert(ignore_permissions=True)
	post_ifrs16_entries(contract_id)
	return {"modification_log_id": log.name}


@frappe.whitelist()
def run_residual_risk_snapshot(contract_id: str, asset_risk_score: str = "0.1", delinquency_days: int = 0) -> dict:
	assets = frappe.get_all("Leasing Finance Asset", filters={"contract_id": contract_id}, fields=["residual_value"])
	exposure = sum(Decimal(str(a.residual_value or 0)) for a in assets)
	flag = 1 if int(delinquency_days) > 30 or Decimal(str(asset_risk_score)) > Decimal("0.3") else 0
	doc = frappe.get_doc({"doctype": "Leasing Finance Risk Snapshot", "contract_id": contract_id, "snapshot_date": str(date.today()), "residual_exposure": exposure, "asset_risk_score": Decimal(str(asset_risk_score)), "delinquency_days": int(delinquency_days), "early_warning_flag": flag})
	doc.insert(ignore_permissions=True)
	return {"risk_snapshot_id": doc.name}


@frappe.whitelist()
def get_leasing_portfolio_dashboard() -> dict:
	kpi = frappe.db.sql("select count(*) as contracts, sum(ifnull(principal,0)) as gross_exposure, sum(ifnull(lease_liability,0)) as liability, avg(ifnull(risk_score,0)) as avg_risk from `tabLeasing Finance Contract`", as_dict=True)
	risk = frappe.db.sql("select ifrs9_stage, count(*) as cases from `tabLeasing Finance Contract` group by ifrs9_stage", as_dict=True)
	resid = frappe.db.sql("select sum(ifnull(residual_exposure,0)) as residual_exposure, avg(ifnull(asset_risk_score,0)) as avg_asset_risk from `tabLeasing Finance Risk Snapshot`", as_dict=True)
	return {"kpis": kpi[0] if kpi else {}, "risk_distribution": risk, "residual_metrics": resid[0] if resid else {}}


@frappe.whitelist()
def submit_policy_version(policy_name: str, version: str, payload: str, effective_from: str | None = None) -> dict:
	from .governance import submit_policy_version as _submit
	obj = json.loads(payload) if isinstance(payload, str) else payload
	if not isinstance(obj, dict):
		frappe.throw(frappe._("payload must be a JSON object"))
	return _submit("omnexa_leasing_finance", policy_name=policy_name, version=version, payload=obj, effective_from=effective_from)


@frappe.whitelist()
def approve_policy_version(policy_name: str, version: str) -> dict:
	from .governance import approve_policy_version as _approve
	return _approve("omnexa_leasing_finance", policy_name=policy_name, version=version)


@frappe.whitelist()
def create_audit_snapshot(process_name: str, inputs: str, outputs: str, policy_ref: str | None = None) -> dict:
	from .governance import create_audit_snapshot as _snap
	in_obj = json.loads(inputs) if isinstance(inputs, str) else inputs
	out_obj = json.loads(outputs) if isinstance(outputs, str) else outputs
	return _snap("omnexa_leasing_finance", process_name=process_name, inputs=in_obj, outputs=out_obj, policy_ref=policy_ref)


@frappe.whitelist()
def get_governance_overview() -> dict:
	from .governance import governance_overview as _overview
	return _overview("omnexa_leasing_finance")


@frappe.whitelist()
def list_policy_versions(policy_name: str | None = None) -> list[dict]:
	from .governance import list_policy_versions as _list
	return _list("omnexa_leasing_finance", policy_name=policy_name)


@frappe.whitelist()
def list_audit_snapshots(process_name: str | None = None, limit: int = 100) -> list[dict]:
	from .governance import list_audit_snapshots as _list
	return _list("omnexa_leasing_finance", process_name=process_name, limit=int(limit))


@frappe.whitelist()
def get_regulatory_dashboard() -> dict:
	from .governance import governance_overview
	std = _get_standards_profile()
	gov = governance_overview("omnexa_leasing_finance")
	return {"app": "omnexa_leasing_finance", "standards": std.get("standards", []), "activity_controls": std.get("activity_controls", []), "governance": gov}
