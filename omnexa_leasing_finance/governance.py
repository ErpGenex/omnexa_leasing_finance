from __future__ import annotations

import hashlib
import json

import frappe
from frappe.utils import now_datetime

ALLOWED_CHECKER_ROLES = {"System Manager", "Compliance Manager", "Risk Manager"}
BACKEND = {"omnexa_leasing_finance": {"policy_doctype": "Leasing Finance Policy Version", "snapshot_doctype": "Leasing Finance Audit Snapshot"}}


def _nowts() -> str:
	return now_datetime().replace(microsecond=0).isoformat(sep=" ")


def _policy_doctype(app: str) -> str: return BACKEND[app]["policy_doctype"]
def _snapshot_doctype(app: str) -> str: return BACKEND[app]["snapshot_doctype"]


def _parse_json(raw):
	if not raw: return {}
	try:
		v = json.loads(str(raw)); return v if isinstance(v, dict) else {}
	except Exception:
		return {}


def _require_checker_role():
	if not (set(frappe.get_roles() or []) & ALLOWED_CHECKER_ROLES):
		frappe.throw(frappe._("You do not have checker approval role."))


def _policy_doc_to_dict(doc):
	return {"name": doc.name, "policy_name": doc.policy_name, "version": doc.policy_version, "payload": _parse_json(getattr(doc, "payload_json", None)), "effective_from": getattr(doc, "effective_from", None), "status": getattr(doc, "status", None), "maker": getattr(doc, "maker", None), "checker": getattr(doc, "checker", None), "rejector": getattr(doc, "rejector", None), "created_at": getattr(doc, "created_at", None), "approved_at": getattr(doc, "approved_at", None), "rejected_at": getattr(doc, "rejected_at", None), "rejection_reason": getattr(doc, "rejection_reason", None)}


def submit_policy_version(app, policy_name, version, payload, effective_from=None):
	dt = _policy_doctype(app)
	if frappe.db.exists(dt, {"policy_name": policy_name, "policy_version": version}):
		frappe.throw(frappe._("Policy version already exists."))
	doc = frappe.get_doc({"doctype": dt, "policy_name": policy_name, "policy_version": version, "payload_json": json.dumps(payload, separators=(",", ":"), sort_keys=True), "effective_from": effective_from, "status": "PENDING_APPROVAL", "maker": frappe.session.user, "created_at": _nowts()})
	doc.insert(ignore_permissions=True)
	return _policy_doc_to_dict(doc)


def approve_policy_version(app, policy_name, version):
	_require_checker_role()
	dt = _policy_doctype(app)
	name = frappe.db.exists(dt, {"policy_name": policy_name, "policy_version": version})
	if not name: frappe.throw(frappe._("Policy version not found."))
	doc = frappe.get_doc(dt, name)
	if doc.maker == frappe.session.user: frappe.throw(frappe._("Maker and checker must be different users."))
	doc.status = "APPROVED"; doc.checker = frappe.session.user; doc.approved_at = _nowts(); doc.save(ignore_permissions=True)
	return _policy_doc_to_dict(doc)


def reject_policy_version(app, policy_name, version, reason=""):
	_require_checker_role()
	dt = _policy_doctype(app)
	name = frappe.db.exists(dt, {"policy_name": policy_name, "policy_version": version})
	if not name: frappe.throw(frappe._("Policy version not found."))
	doc = frappe.get_doc(dt, name)
	if doc.maker == frappe.session.user: frappe.throw(frappe._("Maker and checker must be different users."))
	doc.status = "REJECTED"; doc.rejector = frappe.session.user; doc.rejected_at = _nowts(); doc.rejection_reason = reason or ""; doc.save(ignore_permissions=True)
	return _policy_doc_to_dict(doc)


def list_policy_versions(app, policy_name=None):
	filters = {"policy_name": policy_name} if policy_name else {}
	names = frappe.get_all(_policy_doctype(app), filters=filters, order_by="creation asc", pluck="name")
	return [_policy_doc_to_dict(frappe.get_doc(_policy_doctype(app), n)) for n in names]


def create_audit_snapshot(app, process_name, inputs, outputs, policy_ref=None):
	now = _nowts()
	payload = {"process_name": process_name, "inputs": inputs, "outputs": outputs, "policy_ref": policy_ref, "actor": frappe.session.user, "created_at": now}
	serial = json.dumps(payload, separators=(",", ":"), sort_keys=True)
	snapshot_hash = hashlib.sha256(serial.encode("utf-8")).hexdigest()
	doc = frappe.get_doc({"doctype": _snapshot_doctype(app), "process_name": process_name, "policy_ref": policy_ref, "inputs_json": json.dumps(inputs, separators=(",", ":"), sort_keys=True), "outputs_json": json.dumps(outputs, separators=(",", ":"), sort_keys=True), "snapshot_hash": snapshot_hash, "actor": frappe.session.user, "created_at": now})
	doc.insert(ignore_permissions=True)
	payload["snapshot_hash"] = snapshot_hash
	return payload


def list_audit_snapshots(app, process_name=None, limit=100):
	filters = {"process_name": process_name} if process_name else {}
	rows = frappe.get_all(_snapshot_doctype(app), filters=filters, fields=["process_name", "policy_ref", "inputs_json", "outputs_json", "snapshot_hash", "actor", "created_at"], order_by="creation asc")
	out=[]
	for r in rows[-int(limit):]:
		out.append({"process_name": r.process_name, "policy_ref": r.policy_ref, "inputs": _parse_json(r.inputs_json), "outputs": _parse_json(r.outputs_json), "snapshot_hash": r.snapshot_hash, "actor": r.actor, "created_at": r.created_at})
	return out


def governance_overview(app):
	policies = list_policy_versions(app)
	snaps = list_audit_snapshots(app, limit=500)
	return {"app": app, "policies_total": len(policies), "policies_pending": sum(1 for p in policies if p.get("status") == "PENDING_APPROVAL"), "policies_approved": sum(1 for p in policies if p.get("status") == "APPROVED"), "policies_rejected": sum(1 for p in policies if p.get("status") == "REJECTED"), "snapshots_total": len(snaps)}
